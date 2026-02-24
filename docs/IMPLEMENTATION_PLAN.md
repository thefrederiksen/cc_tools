# CC Tools - Implementation Plan

## Overview

This document outlines the complete implementation plan for the cc-tools open source project, starting with repository structure and the first tool (cc-markdown).

---

## Phase 1: Repository Structure & Foundation

### 1.1 Directory Structure

```
cc-tools/
├── .github/
│   ├── workflows/
│   │   ├── build.yml              # CI for every push
│   │   ├── release.yml            # Build & publish on tag
│   │   └── test.yml               # Run tests
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   ├── cc-markdown/               # First tool
│   │   ├── README.md              # Tool-specific docs
│   │   ├── src/                   # Source code
│   │   ├── themes/                # CSS theme files
│   │   └── tests/                 # Tool tests
│   ├── cc_transcribe/             # Future
│   ├── cc_image/                  # Future
│   ├── cc_voice/                  # Future
│   ├── cc_whisper/                # Future
│   └── cc_video/                  # Future
├── scripts/
│   ├── install.sh                 # Unix installer
│   └── install.ps1                # Windows installer
├── docs/
│   ├── CC_Tools_Strategy.md
│   ├── cc-markdown_PRD.md
│   ├── HANDOVER.md
│   └── IMPLEMENTATION_PLAN.md     # This document
├── .claude-plugin/                # Claude Code plugin support
│   ├── plugin.json
│   └── marketplace.json
├── skills/                        # Claude Code skills
│   └── cc-markdown/
│       └── SKILL.md
├── README.md                      # Main project README
├── LICENSE                        # MIT License (exists)
├── CONTRIBUTING.md                # Contribution guidelines
├── CODE_OF_CONDUCT.md             # Community standards
├── CHANGELOG.md                   # Release history
└── .gitignore
```

### 1.2 Root Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `README.md` | Main project documentation (update existing) | P0 |
| `CONTRIBUTING.md` | How to contribute | P1 |
| `CODE_OF_CONDUCT.md` | Community standards | P1 |
| `CHANGELOG.md` | Release history | P1 |
| `.gitignore` | Ignore build artifacts, etc. | P0 |

### 1.3 README Structure (Main)

The main README.md should follow this structure:

```markdown
# CC Tools

[Brief tagline - one sentence]

[Badges: License, Build Status, Downloads]

## What is CC Tools?
[2-3 sentences explaining the project]

## Tools
[Table of available tools with status]

## Installation
### Pre-compiled Binaries (Recommended)
### Package Managers
### Build from Source

## Quick Start
[One example per tool]

## Documentation
[Links to tool-specific docs]

## Contributing
[Link to CONTRIBUTING.md]

## License
MIT License - see LICENSE

## About
Built by CenterConsulting Inc.
```

### 1.4 GitHub Actions Workflows

#### build.yml (CI)
- Trigger: Push to main, PRs
- Jobs: Lint, Test, Build (matrix: windows, linux, macos)

#### release.yml (Release)
- Trigger: Push tag `v*`
- Jobs:
  1. Build all platforms (Windows x64, Linux x64, macOS x64, macOS ARM64)
  2. Create GitHub Release
  3. Upload binaries as release assets
  4. Generate checksums

### 1.5 Claude Code Plugin Structure

```json
// .claude-plugin/plugin.json
{
  "name": "cc-tools",
  "version": "0.1.0",
  "description": "CLI tools for agentic coding workflows",
  "author": "CenterConsulting Inc.",
  "skills": ["cc-markdown"],
  "mcp_servers": []
}
```

---

## Phase 2: cc-markdown Implementation

### 2.1 Technology Decision

**Language: Python**

| Factor | Python | C# | TypeScript |
|--------|--------|-----|------------|
| Markdown parsing | Excellent (markdown-it-py, mistune) | Good (Markdig) | Good (marked) |
| PDF generation | Good (weasyprint, playwright) | Good (Playwright) | Good (Playwright) |
| Word generation | Good (python-docx) | Excellent (OpenXML) | Limited |
| Single executable | PyInstaller, Nuitka | dotnet publish | pkg, bun compile |
| Dev speed | Fast | Medium | Fast |
| Cross-platform | Excellent | Excellent | Excellent |

**Decision: Python with PyInstaller**
- Fastest to develop
- Excellent library ecosystem
- PyInstaller produces reliable executables
- Existing fred_tools code is Python

### 2.2 Architecture

```
Input: Markdown file
    |
    v
[1. Parse Markdown]
    - Use markdown-it-py (CommonMark + GFM)
    - Extract title from first H1
    |
    v
[2. Generate HTML]
    - Apply CSS theme
    - Embed syntax highlighting CSS
    - Create standalone HTML document
    |
    v
[3. Convert to Output Format]
    |
    +--> PDF: Playwright (headless Chrome)
    |         - High fidelity CSS rendering
    |         - Page size options (A4, Letter)
    |
    +--> Word: python-docx
    |         - Parse HTML, map to Word styles
    |         - Headings, lists, tables, code blocks
    |
    +--> HTML: Output as-is (standalone)
```

### 2.3 Dependencies

```
# Core
markdown-it-py>=3.0.0      # Markdown parsing (CommonMark + GFM)
mdit-py-plugins>=0.4.0     # GFM extensions (tables, strikethrough, etc.)
pygments>=2.17.0           # Syntax highlighting

# Output formats
playwright>=1.40.0         # PDF generation (headless Chrome)
python-docx>=1.1.0         # Word document generation
beautifulsoup4>=4.12.0     # HTML parsing for Word conversion

# CLI
typer>=0.9.0               # CLI framework
rich>=13.0.0               # Terminal formatting

# Build
pyinstaller>=6.0.0         # Executable packaging
```

### 2.4 File Structure

```
src/cc-markdown/
├── README.md                    # Tool documentation
├── pyproject.toml               # Python project config
├── requirements.txt             # Dependencies
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # CLI interface (typer)
│   ├── parser.py                # Markdown parsing
│   ├── html_generator.py        # HTML generation
│   ├── pdf_converter.py         # HTML to PDF
│   ├── word_converter.py        # HTML to Word
│   └── themes/
│       ├── __init__.py
│       ├── base.css             # Common styles
│       ├── boardroom.css
│       ├── terminal.css
│       ├── paper.css
│       ├── spark.css
│       ├── thesis.css
│       ├── obsidian.css
│       └── blueprint.css
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_html.py
│   ├── test_pdf.py
│   ├── test_word.py
│   └── fixtures/
│       └── sample.md
└── build/
    └── build.py                 # PyInstaller build script
```

### 2.5 CLI Interface

```bash
# Basic usage
cc-markdown input.md -o output.pdf
cc-markdown input.md -o output.docx
cc-markdown input.md -o output.html

# With theme
cc-markdown input.md -o output.pdf --theme boardroom
cc-markdown input.md -o output.pdf --theme terminal

# With custom CSS
cc-markdown input.md -o output.pdf --css custom.css

# Options
cc-markdown input.md -o output.pdf --page-size letter  # Default: a4
cc-markdown input.md -o output.pdf --margin 1in        # Default: 1in

# Utility commands
cc-markdown --themes          # List available themes
cc-markdown --version         # Show version
cc-markdown --help            # Show help
```

### 2.6 Implementation Steps

#### Step 1: Project Setup
- [ ] Create `src/cc-markdown/` directory structure
- [ ] Create `pyproject.toml` with dependencies
- [ ] Create `requirements.txt`
- [ ] Set up virtual environment

#### Step 2: Core Parser
- [ ] Implement `parser.py` with markdown-it-py
- [ ] Add GFM extensions (tables, task lists, strikethrough)
- [ ] Add syntax highlighting with Pygments
- [ ] Write tests for parser

#### Step 3: HTML Generator
- [ ] Implement `html_generator.py`
- [ ] Create base CSS template
- [ ] Create theme loader
- [ ] Generate standalone HTML with embedded CSS
- [ ] Write tests

#### Step 4: PDF Converter
- [ ] Implement `pdf_converter.py` with Playwright
- [ ] Add page size options (A4, Letter)
- [ ] Add margin configuration
- [ ] Handle Playwright browser installation
- [ ] Write tests

#### Step 5: Word Converter
- [ ] Implement `word_converter.py` with python-docx
- [ ] Map HTML elements to Word styles:
  - Headings (H1-H6)
  - Paragraphs
  - Lists (ordered, unordered)
  - Tables
  - Code blocks
  - Images
- [ ] Apply theme colors to Word styles
- [ ] Write tests

#### Step 6: CLI Interface
- [ ] Implement `cli.py` with Typer
- [ ] Add all command options
- [ ] Add `--themes` command
- [ ] Add progress indicators
- [ ] Add error handling with clear messages
- [ ] Write integration tests

#### Step 7: Themes
- [ ] Create `base.css` with common styles
- [ ] Create 7 theme CSS files:
  - [ ] Boardroom (corporate, serif)
  - [ ] Terminal (monospace, dark-friendly)
  - [ ] Paper (minimal, clean)
  - [ ] Spark (colorful, modern)
  - [ ] Thesis (academic, serif)
  - [ ] Obsidian (dark theme)
  - [ ] Blueprint (technical)
- [ ] Test each theme with sample documents

#### Step 8: Build & Package
- [ ] Create PyInstaller spec file
- [ ] Build Windows executable
- [ ] Build Linux executable
- [ ] Build macOS executables (x64 + ARM64)
- [ ] Test executables on each platform
- [ ] Document build process

#### Step 9: Documentation
- [ ] Write tool README.md
- [ ] Create theme gallery/preview
- [ ] Document CLI usage
- [ ] Add examples

### 2.7 Theme Design Specifications

| Theme | Font | Colors | Vibe |
|-------|------|--------|------|
| **Boardroom** | Georgia, serif | Navy (#1a365d), Gold (#d69e2e) | Executive, serious |
| **Terminal** | JetBrains Mono, monospace | Green (#22c55e), Dark (#1e1e1e) | Technical, hacker |
| **Paper** | Inter, sans-serif | Black, Light gray | Minimal, clean |
| **Spark** | Poppins, sans-serif | Purple (#8b5cf6), Pink (#ec4899) | Creative, modern |
| **Thesis** | Crimson Text, serif | Black, Muted | Academic, scholarly |
| **Obsidian** | Inter, sans-serif | Purple (#a855f7), Dark (#0f0f0f) | Dark mode |
| **Blueprint** | Source Sans Pro, sans-serif | Blue (#3b82f6), Gray | Technical docs |

### 2.8 Success Criteria

cc-markdown v1.0 is complete when:

1. [ ] User can download single executable from GitHub Releases
2. [ ] `cc-markdown doc.md -o doc.pdf` produces valid PDF
3. [ ] `cc-markdown doc.md -o doc.docx` produces valid Word doc
4. [ ] `cc-markdown doc.md -o doc.html` produces valid HTML
5. [ ] All 7 themes work correctly
6. [ ] `--css` flag works for custom styles
7. [ ] Works on Windows, Linux, macOS (x64 and ARM64)
8. [ ] README has clear installation and usage instructions
9. [ ] Claude Code skill is defined and working

### 2.9 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Playwright browser size | Document browser install requirement, or bundle Chromium |
| Word CSS mapping complexity | Start simple, iterate based on feedback |
| PyInstaller issues on macOS ARM64 | Test early, have fallback to x64 |
| Theme rendering differences | Test all themes on all output formats |

---

## Phase 3: Future Tools (Not in Scope)

For reference, future phases will implement:
- cc_transcribe
- cc_image
- cc_voice
- cc_whisper
- cc_video

Each will follow the same pattern established in Phase 2.

---

## Timeline Estimate

| Phase | Scope | Effort |
|-------|-------|--------|
| Phase 1 | Repository structure | 1 session |
| Phase 2, Steps 1-3 | Parser + HTML | 1 session |
| Phase 2, Steps 4-5 | PDF + Word | 1-2 sessions |
| Phase 2, Steps 6-7 | CLI + Themes | 1 session |
| Phase 2, Steps 8-9 | Build + Docs | 1 session |

---

## Next Actions

1. **Approve this plan** - Review and confirm approach
2. **Phase 1** - Create repository structure and foundation files
3. **Phase 2** - Implement cc-markdown step by step

---

*Document Version: 1.0*
*Created: 2026-02-12*
*Status: Draft - Awaiting Approval*
