# Coding Style Guide

> **Current language scope:** Python

This document defines the coding standards for cc_tools. These are CLI tools and MCP servers that require robust error handling, comprehensive logging, and clear user feedback.

---

## 0. Development Philosophy

1. **Fail Fast, Fail Loud** - Validate early, raise specific exceptions, log everything
2. **No Fallbacks** - Fix root causes, don't add workarounds that hide problems
3. **Clear User Feedback** - CLI users must understand what's happening and what went wrong
4. **Type Safety** - Use type hints everywhere for better tooling and documentation
5. **Test Everything** - Every feature needs tests
6. **Zero Warnings** - Clean code with no linter warnings
7. **Simplicity** - The simplest solution that works correctly

### No Fallback Programming

**Never add fallback logic.** If something might fail, fix the root cause or fail explicitly.

```python
# BAD - fallback hides problems
def get_config_path():
    try:
        return Path(os.environ["CONFIG_PATH"])
    except KeyError:
        return Path.home() / ".config" / "app"  # NO! This hides the real problem

# GOOD - fail explicitly with clear error
def get_config_path() -> Path:
    config_path = os.environ.get("CONFIG_PATH")
    if not config_path:
        raise EnvironmentError(
            "CONFIG_PATH environment variable not set. "
            "Set it to your configuration directory path."
        )
    return Path(config_path)
```

---

## 1. Error Handling

### Catch at the Boundary

Every CLI tool has "boundaries" where user input enters your code. Catch exceptions **only** at these boundaries. Never in helpers or internal functions.

| Context | Boundaries |
|---------|-----------|
| CLI | Main entry point, command handlers |
| MCP Server | Tool handlers, resource handlers |
| API Client | Request handlers, callback functions |

**At every boundary:**
1. Log the full exception internally
2. Show the user a friendly message (never raw tracebacks in production)
3. Let helper functions raise - they are NOT boundaries

### No Bare Except Clauses

```python
# BAD - swallows all exceptions
try:
    process_file(path)
except:
    pass

# BAD - catches too broadly
try:
    process_file(path)
except Exception:
    print("Something went wrong")

# GOOD - catches specific exceptions
try:
    process_file(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise
except PermissionError as e:
    logger.error(f"Permission denied: {path}")
    raise
```

### Exception Hierarchy

```python
# Define clear exception hierarchy for your tool
class CcToolsError(Exception):
    """Base exception for cc_tools."""
    pass

class ConfigurationError(CcToolsError):
    """Configuration is invalid or missing."""
    pass

class ProcessingError(CcToolsError):
    """Error during content processing."""
    pass
```

---

## 2. Type Hints

### Required Everywhere

All public functions and methods MUST have type hints.

```python
# BAD - no type hints
def convert_file(input_path, output_path, format):
    ...

# GOOD - complete type hints
def convert_file(
    input_path: Path,
    output_path: Path,
    format: Literal["pdf", "docx", "html"]
) -> ConversionResult:
    ...
```

### Common Patterns

```python
from typing import Optional, List, Dict, Callable, TypeVar, Generic
from pathlib import Path
from collections.abc import Iterable, Sequence

# Optional for nullable parameters
def find_config(path: Optional[Path] = None) -> Config:
    ...

# Use Path, not str, for file paths
def read_file(path: Path) -> str:
    ...

# Use Literal for constrained string values
def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    ...

# Return types are required
def calculate_hash(data: bytes) -> str:
    ...
```

---

## 3. Naming Conventions

### General Rules

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `cc_markdown`, `file_utils` |
| Classes | PascalCase | `MarkdownConverter`, `ConfigParser` |
| Functions | snake_case | `convert_file`, `parse_config` |
| Methods | snake_case | `get_metadata`, `set_option` |
| Variables | snake_case | `file_path`, `output_dir` |
| Constants | UPPER_SNAKE | `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT` |
| Private | _leading_underscore | `_internal_state`, `_helper_func` |
| Boolean | is_, has_, can_ prefix | `is_valid`, `has_header`, `can_write` |

### Class Suffix Conventions

| Suffix | Responsibility | Example |
|--------|---------------|---------|
| `*Converter` | Format conversion | `MarkdownConverter`, `PdfConverter` |
| `*Parser` | Parsing input | `ConfigParser`, `ArgumentParser` |
| `*Handler` | Event/request handling | `ErrorHandler`, `RequestHandler` |
| `*Client` | External API access | `ApiClient`, `GmailClient` |
| `*Manager` | Resource lifecycle | `SessionManager`, `CacheManager` |

---

## 4. Logging Standards

### Use Python logging Module

```python
import logging

logger = logging.getLogger(__name__)

def process_file(path: Path) -> ProcessResult:
    logger.info(f"Processing file: {path}")
    try:
        result = do_processing(path)
        logger.debug(f"Processing complete: {result.summary}")
        return result
    except ProcessingError as e:
        logger.error(f"Processing failed for {path}: {e}")
        raise
```

### Logging Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| **ERROR** | Operation failed, needs attention | Exception caught, process failed |
| **WARNING** | Potential issue, didn't cause failure | Retry needed, deprecated usage |
| **INFO** | Important business events | File converted, command completed |
| **DEBUG** | Detailed diagnostic info | Method entry/exit, state changes |

### Never Use Print for Logging

```python
# BAD - print statements for diagnostics
print(f"Processing {filename}...")
print("Done!")

# GOOD - use logger
logger.info(f"Processing {filename}")
logger.info("Processing complete")

# EXCEPTION: CLI user-facing output (not diagnostics)
# Use click.echo() or similar for intentional user output
click.echo(f"Converted: {output_path}")
```

### Never Log Secrets

```python
# BAD
logger.info(f"Connecting with API key: {api_key}")

# GOOD
logger.info(f"Connecting with API key: {api_key[:4]}...")
```

---

## 5. Testing Standards

### Test Coverage Requirements

- All public functions must have unit tests
- All bug fixes must include a regression test
- All new features must include tests before merge

### Test Structure

Use pytest with Arrange-Act-Assert pattern:

```python
def test_convert_markdown_to_pdf_creates_output_file(tmp_path: Path) -> None:
    # Arrange
    input_file = tmp_path / "test.md"
    input_file.write_text("# Hello World")
    output_file = tmp_path / "test.pdf"

    # Act
    convert_markdown_to_pdf(input_file, output_file)

    # Assert
    assert output_file.exists()
    assert output_file.stat().st_size > 0
```

### Test Naming

`test_<function>_<scenario>_<expected_result>`

```python
# GOOD
def test_parse_config_with_missing_file_raises_file_not_found() -> None:
def test_convert_empty_markdown_returns_empty_pdf() -> None:
def test_get_metadata_with_valid_path_returns_dict() -> None:

# BAD
def test_parse_config() -> None:
def test_1() -> None:
```

### Test Organization

```
tests/
    test_cc_markdown/
        test_converter.py
        test_parser.py
        conftest.py  # Shared fixtures
    test_cc_voice/
        test_transcriber.py
```

---

## 6. Function Design

### Mutable Default Arguments

**NEVER use mutable default arguments.**

```python
# BAD - mutable default argument bug
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)  # Bug: shared across calls!
    return items

# GOOD - use None and create new list
def add_item(item: str, items: Optional[list[str]] = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Function Length

Functions should be under 50 lines. If longer, split into smaller functions.

### Guard Clauses

Validate early and exit early:

```python
def process_file(path: Path) -> ProcessResult:
    # Guard clauses at the top
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"File is empty: {path}")

    # Main logic after validation
    ...
```

---

## 7. Module Structure

### Standard Script Guard

```python
# Required at bottom of executable scripts
if __name__ == "__main__":
    main()
```

### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, List

# Third-party imports
import click
import httpx
from pydantic import BaseModel

# Local imports
from .converter import MarkdownConverter
from .config import load_config
```

### Never Use Star Imports

```python
# BAD - pollutes namespace, unclear dependencies
from os.path import *
from mymodule import *

# GOOD - explicit imports
from os.path import join, dirname, exists
from mymodule import SpecificClass, specific_function
```

---

## 8. Security

### Never Hard-Code Credentials

```python
# BAD
API_KEY = "sk-abc123xyz789..."

# GOOD - read from environment
def get_api_key() -> str:
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise EnvironmentError(
            "API_KEY environment variable not set. "
            "Get your API key from https://example.com/api-keys"
        )
    return api_key
```

### Common Secrets Patterns to Avoid

Never commit code containing these patterns:

| Pattern | Example | What It Usually Is |
|---------|---------|-------------------|
| `sk-` | `sk-abc123...` | OpenAI API key |
| `AKIA` | `AKIAIOSFODNN7EXAMPLE` | AWS Access Key ID |
| `ghp_` | `ghp_xxxx...` | GitHub Personal Access Token |
| `gho_` | `gho_xxxx...` | GitHub OAuth Token |
| `Bearer eyJ` | `Bearer eyJhbGc...` | JWT Auth Token |
| `-----BEGIN` | `-----BEGIN RSA PRIVATE KEY-----` | Private Key |
| `password=` | `password="secret123"` | Hardcoded Password |
| `postgres://user:pass@` | `postgres://admin:pass123@host` | DB Connection String |
| `client_secret` | `client_secret="abc..."` | OAuth Client Secret |

**Where credentials should go:**
- Environment variables (preferred)
- `.env` files (must be in `.gitignore`)
- Secure secret managers (Azure Key Vault, AWS Secrets Manager)
- Config files excluded from version control

### Never Commit PII (Personal Identifiable Information)

PII in code is a security and privacy risk. Never commit:

- **Real email addresses** (except @example.com, @test.com)
- **Phone numbers** (real ones - 555-xxx-xxxx is OK for tests)
- **Physical addresses** (street addresses, city/state/zip)
- **Personal names** with other identifying info
- **Employee IDs, account numbers**
- **Internal company URLs or system names**

**For test data, use:**

```python
# BAD - real data
TEST_USER = {
    "name": "John Smith",
    "email": "jsmith@company.com",
    "phone": "415-555-1234"
}

# GOOD - obviously fake data
TEST_USER = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "555-000-0000"
}

# BETTER - use Faker library for realistic fake data
from faker import Faker
fake = Faker()
TEST_USER = {
    "name": fake.name(),
    "email": fake.email(),
    "phone": fake.phone_number()
}
```

**Test domains and numbers:**
- Use `@example.com`, `@test.com`, `@placeholder.com` for emails
- Use `555-xxx-xxxx` for US phone numbers (reserved for fiction)
- Use `John Doe`, `Jane Doe`, `Test User` for names
- Use `123 Test Street, Anytown, ST 00000` for addresses

### Safe File Operations

```python
# GOOD - use context managers
with open(path, "r") as f:
    content = f.read()

# GOOD - Path methods with context managers
content = path.read_text()

# BAD - manual file handling
f = open(path, "r")
content = f.read()
f.close()  # May not be called if exception occurs
```

### Path Safety

```python
# Validate paths before operations
def safe_read(base_dir: Path, relative_path: str) -> str:
    full_path = (base_dir / relative_path).resolve()

    # Prevent directory traversal attacks
    if not str(full_path).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path escapes base directory: {relative_path}")

    return full_path.read_text()
```

---

## 9. Documentation

### Docstrings for Public Functions

```python
def convert_markdown(
    input_path: Path,
    output_path: Path,
    options: Optional[ConvertOptions] = None
) -> ConversionResult:
    """Convert a Markdown file to PDF.

    Args:
        input_path: Path to the input Markdown file.
        output_path: Path where the PDF will be written.
        options: Optional conversion settings.

    Returns:
        ConversionResult with status and metadata.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        ConversionError: If conversion fails.
    """
    ...
```

### Code Comments

Comments explain **why**, not **what**:

```python
# GOOD - explains why
# Rate limit to avoid API throttling (max 10 req/sec)
time.sleep(0.1)

# BAD - explains what (obvious from code)
# Sleep for 0.1 seconds
time.sleep(0.1)
```

---

## 10. Async Code

### Async All The Way

Once you go async, stay async up the call chain:

```python
# BAD - blocking call in async function
async def fetch_data(url: str) -> dict:
    response = requests.get(url)  # Blocks the event loop!
    return response.json()

# GOOD - use async HTTP client
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Never Block the Event Loop

```python
# BAD - blocks event loop
async def process_file(path: Path) -> str:
    with open(path) as f:  # Blocking I/O!
        return f.read()

# GOOD - use run_in_executor for blocking I/O
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_file(path: Path) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, path.read_text)

# BETTER - use aiofiles for async file I/O
import aiofiles

async def process_file(path: Path) -> str:
    async with aiofiles.open(path) as f:
        return await f.read()
```

---

## 11. Project Configuration

### pyproject.toml Settings

```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W"]

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_ignores = true
```

### Required Project Files

- `pyproject.toml` - Project metadata and dependencies
- `README.md` - Usage documentation
- `requirements.txt` - Pinned dependencies (if not using pyproject.toml exclusively)

---

## 12. Quick Reference

| Aspect | Rule | Example |
|--------|------|---------|
| Type hints | Required on all public functions | `def func(x: int) -> str:` |
| Mutable defaults | Forbidden | Use `None` then create new list/dict |
| Bare except | Forbidden | Catch specific exceptions |
| Fallback catches | Forbidden | Fix root cause instead |
| Print for logs | Forbidden | Use `logging` module |
| Hard-coded secrets | Forbidden | Use environment variables |
| PII in code | Forbidden | Use fake/test data |
| API keys | Forbidden | Use env vars or secret manager |
| Real emails | Forbidden | Use @example.com or @test.com |
| Star imports | Forbidden | Import specific names |
| Functions | Under 50 lines | Split into smaller functions |
| Tests | Required for public functions | pytest with AAA pattern |
| Docstrings | Required for public functions | Google style |
| Comments | Explain why, not what | Only when logic isn't obvious |

---

## When in Doubt

1. Log more, not less
2. Fail explicitly, not silently
3. Show clear error messages
4. Write a test
5. Use type hints
