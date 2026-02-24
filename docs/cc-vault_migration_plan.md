# cc_vault Migration Plan

## Overview

Migrate vault code from `D:\ReposFred\cc_consult\src\` to `D:\ReposFred\cc_tools\src\cc_vault\` as a standalone open-source CLI tool.

**Goal:** Users configure one thing (vault directory via env var or config file) and everything works.

---

## Source Files to Migrate

Copy these files from `D:\ReposFred\cc_consult\src\`:

| Source File | Target File | Notes |
|-------------|-------------|-------|
| vault_config.py | src/config.py | Refactor: add env/file config resolution |
| vault.py | src/db.py | Remove CLI section, update imports |
| vault_vectors.py | src/vectors.py | Update imports |
| vault_chunker.py | src/chunker.py | Minimal changes |
| vault_converters.py | src/converters.py | Minimal changes |
| vault_importer.py | src/importer.py | Update imports |
| vault_rag.py | src/rag.py | Remove CLI section, update imports |

---

## Target Directory Structure

Create this structure in `D:\ReposFred\cc_tools\src\cc_vault\`:

```
cc_vault/
├── main.py                    # Entry point (PyInstaller)
├── pyproject.toml             # Package config
├── cc_vault.spec              # PyInstaller spec
├── build.ps1                  # Build script
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── src/
│   ├── __init__.py            # Version
│   ├── __main__.py            # Module entry
│   ├── cli.py                 # Typer CLI (NEW)
│   ├── config.py              # Configuration
│   ├── db.py                  # SQLite layer
│   ├── vectors.py             # ChromaDB
│   ├── chunker.py             # Document chunking
│   ├── converters.py          # File conversion
│   ├── importer.py            # Import logic
│   ├── rag.py                 # RAG engine
│   └── utils.py               # Helpers (NEW)
└── tests/
    └── __init__.py
```

Also create: `D:\ReposFred\cc_tools\skills\cc_vault\SKILL.md`

---

## Step-by-Step Implementation

### Step 1: Create Directory Structure

```bash
mkdir -p D:\ReposFred\cc_tools\src\cc_vault\src
mkdir -p D:\ReposFred\cc_tools\src\cc_vault\tests
mkdir -p D:\ReposFred\cc_tools\skills\cc_vault
```

### Step 2: Create Package Files

**src/cc_vault/src/__init__.py:**
```python
"""cc_vault - Personal life organizer CLI."""

__version__ = "1.0.0"
__author__ = "CenterConsulting Inc."
```

**src/cc_vault/src/__main__.py:**
```python
"""Package entry point."""
from .cli import app

if __name__ == "__main__":
    app()
```

**src/cc_vault/main.py:**
```python
#!/usr/bin/env python3
"""Entry point for cc_vault CLI."""

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
    sys.path.insert(0, str(base_path))
    sys.path.insert(0, str(base_path / 'src'))
else:
    base_path = Path(__file__).parent
    sys.path.insert(0, str(base_path))
    sys.path.insert(0, str(base_path / 'src'))

from cli import app

if __name__ == "__main__":
    app()
```

### Step 3: Create config.py (from vault_config.py)

Key changes from original:
- Replace hardcoded `VAULT_PATH = Path("D:/Vault")` with configurable resolution
- Add environment variable support: `CC_VAULT_PATH`
- Add config file support: `~/.cc_vault/config.json`
- Add `get_config()` function

```python
"""Configuration for cc_vault."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class VaultConfig:
    vault_path: Path
    db_path: Path
    vectors_path: Path
    documents_path: Path
    health_path: Path
    backups_path: Path
    embedding_model: str = "text-embedding-3-small"
    chunk_max_tokens: int = 400
    chunk_overlap_tokens: int = 80
    chunk_threshold_tokens: int = 500
    hybrid_vector_weight: float = 0.7
    hybrid_text_weight: float = 0.3

def get_vault_path() -> Path:
    """Get vault path from env > config file > default."""
    # 1. Environment variable
    if env_path := os.environ.get("CC_VAULT_PATH"):
        return Path(env_path)

    # 2. Config file
    config_file = Path.home() / ".cc_vault" / "config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            if "vault_path" in config:
                return Path(config["vault_path"])
        except (json.JSONDecodeError, IOError):
            pass

    # 3. Default
    return Path.home() / "Vault"

def get_config() -> VaultConfig:
    """Load configuration."""
    vault_path = get_vault_path()
    return VaultConfig(
        vault_path=vault_path,
        db_path=vault_path / "vault.db",
        vectors_path=vault_path / "vectors",
        documents_path=vault_path / "documents",
        health_path=vault_path / "health",
        backups_path=vault_path / "backups",
    )

def ensure_directories() -> None:
    """Create vault directories if needed."""
    config = get_config()
    for path in [
        config.vault_path,
        config.vectors_path,
        config.documents_path,
        config.documents_path / "transcripts",
        config.documents_path / "notes",
        config.documents_path / "journals",
        config.documents_path / "research",
        config.health_path,
        config.backups_path,
    ]:
        path.mkdir(parents=True, exist_ok=True)

# For backward compatibility - these are computed on import
_config = get_config()
VAULT_PATH = _config.vault_path
DB_PATH = _config.db_path
VECTORS_PATH = _config.vectors_path
DOCUMENTS_PATH = _config.documents_path
# ... etc
```

### Step 4: Create db.py (from vault.py)

1. Copy vault.py to db.py
2. Remove the entire `if __name__ == "__main__":` CLI section (lines ~2650+)
3. Update imports at top:
   ```python
   from .config import get_config, ensure_directories, DB_PATH, VAULT_PATH
   ```
4. Remove the try/except fallback for vault_config import

### Step 5: Create vectors.py (from vault_vectors.py)

1. Copy vault_vectors.py to vectors.py
2. Update imports:
   ```python
   from .config import VECTORS_PATH, EMBEDDING_MODEL, OPENAI_API_KEY, ...
   ```

### Step 6: Create chunker.py (from vault_chunker.py)

1. Copy vault_chunker.py to chunker.py
2. No import changes needed (standalone module)

### Step 7: Create converters.py (from vault_converters.py)

1. Copy vault_converters.py to converters.py
2. No import changes needed (standalone module)

### Step 8: Create importer.py (from vault_importer.py)

1. Copy vault_importer.py to importer.py
2. Update imports:
   ```python
   from .config import VAULT_PATH, DOCUMENTS_PATH, HEALTH_PATH, ...
   from .db import add_document, update_document, get_document_by_path, ...
   from .vectors import get_vault_vectors
   from .converters import convert_to_markdown, is_supported
   ```
3. Remove `if __name__ == "__main__":` section

### Step 9: Create rag.py (from vault_rag.py)

1. Copy vault_rag.py to rag.py
2. Update imports:
   ```python
   from .config import OPENAI_API_KEY, HYBRID_VECTOR_WEIGHT, HYBRID_TEXT_WEIGHT
   from .vectors import get_vault_vectors
   ```
3. Remove `if __name__ == "__main__":` section

### Step 10: Create cli.py (NEW - Typer CLI)

Use cc_outlook's cli.py as template. Structure:

```python
"""CLI for cc_vault using Typer."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import get_config, ensure_directories
from .db import (
    init_db, add_task, get_tasks, complete_task, cancel_task,
    add_goal, get_goals, achieve_goal,
    add_idea, get_ideas,
    add_contact, get_contact, get_contacts,
    get_statistics,
)
from .rag import VaultRAG
from .importer import VaultImporter

app = typer.Typer(name="cc_vault", help="Personal life organizer", add_completion=False)
tasks_app = typer.Typer(help="Manage tasks")
goals_app = typer.Typer(help="Manage goals")
ideas_app = typer.Typer(help="Manage ideas")
contacts_app = typer.Typer(help="Manage contacts")
docs_app = typer.Typer(help="Manage documents")
config_app = typer.Typer(help="Configuration")

app.add_typer(tasks_app, name="tasks")
app.add_typer(goals_app, name="goals")
app.add_typer(ideas_app, name="ideas")
app.add_typer(contacts_app, name="contacts")
app.add_typer(docs_app, name="docs")
app.add_typer(config_app, name="config")

console = Console()

@app.command()
def init():
    """Initialize the vault."""
    ensure_directories()
    init_db()
    console.print("[green]Vault initialized[/green]")

@app.command()
def stats():
    """Show vault statistics."""
    init_db(silent=True)
    # Display statistics with Rich tables

@app.command()
def ask(question: str, model: str = "gpt-4o"):
    """Ask a question using RAG."""
    rag = VaultRAG()
    result = rag.ask(question, model=model)
    console.print(result['answer'])

@app.command()
def search(query: str, n: int = 10):
    """Search across the vault."""
    # Implement search

# ... implement all task, goal, idea, contact, doc subcommands
```

### Step 11: Create utils.py (NEW)

Extract formatting functions from db.py:

```python
"""Utility functions for cc_vault."""

from rich.table import Table
from rich.console import Console

def truncate(text: str, max_len: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."

def format_tasks_table(tasks: list) -> Table:
    """Create Rich table for tasks."""
    table = Table(title="Tasks")
    table.add_column("ID", style="dim")
    table.add_column("P", style="bold")
    table.add_column("Task")
    table.add_column("Due", style="cyan")
    table.add_column("Context", style="dim")
    # ... add rows
    return table

# ... more formatting functions
```

### Step 12: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "cc_vault"
version = "1.0.0"
description = "Personal life organizer: contacts, tasks, goals, ideas, documents with RAG"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "CenterConsulting Inc."}]
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "chromadb>=0.4.0",
    "openai>=1.0.0",
    "tiktoken>=0.5.0",
]

[project.optional-dependencies]
converters = ["python-docx>=0.8.0", "pymupdf>=1.23.0"]
dev = ["pytest>=7.0.0", "pyinstaller>=6.0.0"]
all = ["python-docx>=0.8.0", "pymupdf>=1.23.0", "pytest>=7.0.0", "pyinstaller>=6.0.0"]

[project.scripts]
cc_vault = "src.cli:app"

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

### Step 13: Create cc_vault.spec

Use cc_outlook.spec as template, update hiddenimports:

```python
hiddenimports=[
    'cli', 'config', 'db', 'vectors', 'chunker', 'converters', 'importer', 'rag', 'utils',
    'typer', 'rich', 'chromadb', 'tiktoken', 'tiktoken_ext.openai_public',
]
```

### Step 14: Create build.ps1

Copy from cc_outlook and update tool name.

### Step 15: Create requirements.txt

```
typer>=0.9.0
rich>=13.0.0
chromadb>=0.4.0
openai>=1.0.0
tiktoken>=0.5.0
python-docx>=0.8.0
pymupdf>=1.23.0
pytest>=7.0.0
pyinstaller>=6.0.0
```

### Step 16: Create README.md

Document installation, configuration, and all commands.

### Step 17: Create SKILL.md

Create `D:\ReposFred\cc_tools\skills\cc_vault\SKILL.md` for Claude Code integration.

### Step 18: Update scripts/build.bat

Add `cc_vault` to the PYTHON_TOOLS list.

---

## CLI Command Reference

```bash
# System
cc_vault init                            # Initialize vault
cc_vault stats                           # Show statistics
cc_vault backup                          # Create backup

# Tasks
cc_vault tasks                           # List pending
cc_vault tasks add "Task" [--due DATE] [--priority 1-5] [--context work]
cc_vault tasks done ID
cc_vault tasks cancel ID

# Goals
cc_vault goals                           # List active
cc_vault goals add "Goal" [--category TYPE] [--timeframe short|medium|long]
cc_vault goals achieve ID
cc_vault goals pause ID
cc_vault goals resume ID

# Ideas
cc_vault ideas                           # List ideas
cc_vault ideas add "Idea" [--domain TYPE]
cc_vault ideas actionable ID
cc_vault ideas archive ID

# Contacts
cc_vault contacts                        # List contacts
cc_vault contacts add EMAIL --name "Name" [--account consulting|personal]
cc_vault contacts show EMAIL
cc_vault contacts profile EMAIL          # Full profile with memories
cc_vault contacts update EMAIL [--company X] [--title Y]
cc_vault contacts memory EMAIL "Fact about them"

# Documents
cc_vault docs                            # List documents
cc_vault docs add FILE [--type transcript|note|journal|research] [--title X]
cc_vault docs show ID
cc_vault docs search "query"

# RAG
cc_vault ask "Question?"                 # RAG query with citations
cc_vault search "query"                  # Semantic search

# Configuration
cc_vault config                          # Show current config
cc_vault config set vault_path PATH
cc_vault config set embedding_model MODEL
```

---

## Verification Checklist

After implementation, verify:

```bash
# 1. Build succeeds
cd D:\ReposFred\cc_tools\src\cc_vault
.\build.ps1

# 2. Executable created
dir dist\cc_vault.exe

# 3. Copy and test
copy dist\cc_vault.exe C:\cc-tools\

# 4. Initialize
cc_vault init

# 5. Test core commands
cc_vault stats
cc_vault tasks add "Test task"
cc_vault tasks
cc_vault tasks done 1

# 6. Test config
cc_vault config

# 7. Test RAG (requires OPENAI_API_KEY)
set OPENAI_API_KEY=your-key
cc_vault ask "What tasks do I have?"
```

---

## Dependencies

Required:
- Python 3.11+
- typer, rich (CLI)
- chromadb, openai, tiktoken (vector search)

Optional:
- python-docx (Word import)
- pymupdf (PDF import)

Build:
- pyinstaller

---

## Notes

- The vault stores data in `~/Vault` by default (or `CC_VAULT_PATH` env var)
- Config file at `~/.cc_vault/config.json`
- OPENAI_API_KEY required for vector search and RAG
- ChromaDB stores vectors in `{vault}/vectors/`
- SQLite database at `{vault}/vault.db`
