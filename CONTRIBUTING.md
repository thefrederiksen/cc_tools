# Contributing to CC Tools

Thank you for your interest in contributing to CC Tools!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](../../issues)
2. If not, create a new issue using the bug report template
3. Include:
   - Which tool is affected
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, version)

### Suggesting Features

1. Check if the feature has been requested in [Issues](../../issues)
2. Create a new issue using the feature request template
3. Describe the problem and proposed solution

### Contributing Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Write/update tests
5. Run tests: `pytest tests/ -v`
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/cc-tools.git
cd cc-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
# or: venv\Scripts\activate  # Windows

# Install dependencies
cd src/cc-markdown
pip install -r requirements.txt
pip install -e .

# Install Playwright browsers (for PDF generation)
playwright install chromium
```

### Running Tests

```bash
cd src/cc-markdown
pytest tests/ -v
```

### Building Executables

```bash
cd src/cc-markdown
pip install pyinstaller
pyinstaller --onefile --name cc-markdown src/__main__.py
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small

## Commit Messages

Use clear, descriptive commit messages:

- `fix: resolve PDF margin issue on Windows`
- `feat: add --page-size option`
- `docs: update installation instructions`
- `test: add tests for Word table conversion`

## Pull Request Guidelines

- One feature/fix per PR
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass
- Request review from maintainers

## Questions?

Open an issue with the question label or reach out to the maintainers.

---

Thank you for contributing!
