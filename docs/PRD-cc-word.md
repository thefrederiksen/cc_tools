# PRD: cc-word

> Convert Markdown to professional Word (.docx) documents with themes.

---

## 1. Overview

**cc-word** is a CLI tool that converts Markdown files to professionally formatted Word documents. It improves upon cc-markdown's existing `word_converter.py` by parsing Markdown directly at the token level rather than converting through HTML, preserving inline formatting (bold, italic, code, links) that the current approach loses.

**Problem:** cc-markdown's Word output uses an HTML-to-BeautifulSoup pipeline that strips inline formatting. `get_text(strip=True)` collapses `**bold** and *italic*` into plain text. Users get structurally correct documents with no character-level formatting. Additionally, cc-markdown's Word output has no theme support -- every document looks the same.

**Solution:** A dedicated tool that parses Markdown tokens directly using markdown-it-py and maps them to python-docx runs with preserved inline formatting. Themes control fonts, colors, spacing, and page layout via frozen dataclasses.

**Target users:**
- LLMs generating reports, proposals, and documentation
- Humans who write in Markdown and need Word output for stakeholders

---

## 2. Goals & Non-Goals

### Goals

- Convert Markdown to `.docx` with full inline formatting (bold, italic, code, links, strikethrough)
- Support all common Markdown elements: headings, paragraphs, lists (nested), tables, code blocks, images, blockquotes, horizontal rules
- Apply visual themes matching the cc-tools theme system (7 standard themes)
- Generate cover pages, table of contents, headers/footers
- Produce single-file executables via PyInstaller

### Non-Goals

- Reading or modifying existing `.docx` files (write-only)
- Template-based generation (`.dotx` template files)
- Track changes or comments
- Mail merge or variable substitution
- Complex page layouts (multi-column, text wrapping around images)
- PDF output (use cc-markdown for that)
- HTML output (use cc-markdown for that)

---

## 3. Technical Architecture

### 3.1 Directory Structure

```
src/cc-word/
    main.py                     # PyInstaller entry point
    cc-word.spec                # PyInstaller spec
    pyproject.toml              # Project config & dependencies
    requirements.txt            # Pinned runtime deps
    build.ps1                   # Windows build script
    build.sh                    # Unix build script
    samples/
        project-report.md       # Example document
    src/
        __init__.py             # Package version
        __main__.py             # python -m entry point
        cli.py                  # Typer CLI (single command)
        parser.py               # Markdown -> DocumentModel via token parsing
        docx_generator.py       # DocumentModel + Theme -> .docx
        inline_parser.py        # Token stream -> list[InlineRun]
        elements/
            __init__.py         # Element handler registry
            cover_page.py       # Title page generation
            toc.py              # Table of contents (Word field code)
            headers_footers.py  # Page headers and footers
            code_block.py       # Fenced code block formatting
            table.py            # Table generation with styling
            image.py            # Image embedding and sizing
            blockquote.py       # Blockquote formatting
        themes/
            __init__.py         # Theme dataclasses + registry
    tests/
        __init__.py
        test_parser.py
        test_inline_parser.py
        test_docx_generator.py
        test_elements.py
        conftest.py             # Shared fixtures
```

### 3.2 Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `cli.py` | Typer app with single `main()` command |
| `parser.py` | Parse Markdown into `DocumentModel` using markdown-it-py tokens |
| `inline_parser.py` | Convert inline token sequences to `list[InlineRun]` preserving bold/italic/code/link |
| `docx_generator.py` | Walk `DocumentModel` and emit python-docx elements with theme styling |
| `elements/cover_page.py` | Generate title page from document title and metadata |
| `elements/toc.py` | Insert Word TOC field code (`TOC \o "1-3" \h \z \u`) |
| `elements/headers_footers.py` | Add page headers (title) and footers (page numbers) |
| `elements/code_block.py` | Format code blocks with background shading and monospace font |
| `elements/table.py` | Generate styled tables with header row formatting |
| `elements/image.py` | Embed images with size constraints |
| `elements/blockquote.py` | Format blockquotes with left border and indent |
| `themes/__init__.py` | Frozen dataclass theme definitions + registry |

### 3.3 Internal Data Model

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InlineStyle(Enum):
    """Inline text formatting flags."""
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    CODE = "code"
    STRIKETHROUGH = "strikethrough"


@dataclass
class InlineRun:
    """A segment of text with uniform formatting.

    A paragraph like "Hello **world** and *stuff*" becomes:
    [
        InlineRun(text="Hello ", style=PLAIN),
        InlineRun(text="world", style=BOLD),
        InlineRun(text=" and ", style=PLAIN),
        InlineRun(text="stuff", style=ITALIC),
    ]
    """
    text: str
    style: InlineStyle = InlineStyle.PLAIN
    link_url: str = ""          # Non-empty if this run is a hyperlink


class BlockType(Enum):
    """Document block element types."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    ORDERED_LIST = "ordered_list"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
    IMAGE = "image"
    HORIZONTAL_RULE = "hr"
    THEMATIC_BREAK = "thematic_break"


@dataclass
class ListItem:
    """A single list item with optional nesting."""
    runs: list[InlineRun]       # Inline content
    level: int = 0              # Nesting depth (0 = top level)


@dataclass
class TableCell:
    """A single table cell."""
    runs: list[InlineRun]       # Inline content with formatting
    is_header: bool = False


@dataclass
class TableData:
    """Parsed table structure."""
    headers: list[TableCell]
    rows: list[list[TableCell]]


@dataclass
class ImageData:
    """Image reference."""
    src: str
    alt: str = ""
    width: Optional[float] = None   # Inches, None = auto


@dataclass
class Block:
    """A single document block element."""
    block_type: BlockType
    # Content fields (populated based on block_type)
    runs: list[InlineRun] = field(default_factory=list)         # HEADING, PARAGRAPH, BLOCKQUOTE
    heading_level: int = 0                                       # HEADING: 1-6
    list_items: list[ListItem] = field(default_factory=list)     # BULLET_LIST, ORDERED_LIST
    code: str = ""                                                # CODE_BLOCK
    code_language: str = ""                                       # CODE_BLOCK
    table: Optional[TableData] = None                             # TABLE
    image: Optional[ImageData] = None                             # IMAGE


@dataclass
class DocumentMetadata:
    """Document-level metadata extracted from frontmatter or content."""
    title: str = ""
    subtitle: str = ""
    author: str = ""
    date: str = ""


@dataclass
class DocumentModel:
    """Complete parsed document ready for generation."""
    metadata: DocumentMetadata
    blocks: list[Block]
```

### 3.4 Processing Pipeline

```
Input Markdown File
        |
        v
    [Parser]  -- markdown-it-py tokenization
        |
        +---> [Inline Parser]  -- token stream -> list[InlineRun]
        |                         (preserves bold/italic/code/link per segment)
        |
        v
    DocumentModel (metadata + list[Block])
        |
        v
    [DOCX Generator]  -- walks blocks, applies WordTheme
        |
        +---> [Element Handlers]
        |       |-- cover_page.py   (if --cover)
        |       |-- toc.py          (if --toc)
        |       |-- headers_footers.py (if --header/--footer)
        |       |-- code_block.py
        |       |-- table.py
        |       |-- image.py
        |       +-- blockquote.py
        |
        v
    Output .docx file
```

---

## 4. CLI Interface

### 4.1 Single Command

cc-word uses a single command (not subcommands) because there is one input format (Markdown) and one output format (.docx).

```bash
# Basic conversion
cc-word report.md -o report.docx

# With theme
cc-word report.md -o report.docx --theme boardroom

# With cover page and TOC
cc-word report.md -o report.docx --cover --toc

# With headers and footers
cc-word report.md -o report.docx --header --footer

# Full professional document
cc-word report.md -o report.docx --theme boardroom --cover --toc --header --footer

# Page size and margins
cc-word report.md -o report.docx --page-size letter --margin 1in

# List themes
cc-word --themes

# Version
cc-word --version
```

### 4.2 Options

| Option | Default | Description |
|--------|---------|-------------|
| `INPUT_FILE` | (required) | Path to Markdown file |
| `-o, --output` | (required) | Output .docx path |
| `--theme, -t` | `paper` | Theme name |
| `--cover` | `false` | Generate cover page from first H1 |
| `--toc` | `false` | Insert table of contents |
| `--toc-depth` | `3` | TOC heading depth (1-6) |
| `--header` | `false` | Add page header (document title) |
| `--footer` | `false` | Add page footer (page numbers) |
| `--page-size` | `a4` | Page size: `a4` or `letter` |
| `--margin` | `1in` | Page margins (e.g., `1in`, `2cm`, `0.75in`) |
| `--version, -v` | -- | Show version and exit |
| `--themes` | -- | List available themes and exit |

---

## 5. Theme System

### 5.1 Dataclass Definitions

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class WordColors:
    """Color scheme for Word document."""
    heading: str             # Heading text color (hex)
    body_text: str           # Body text color (hex)
    accent: str              # Accent color (links, highlights) (hex)
    code_bg: str             # Code block background (hex)
    code_text: str           # Code block text color (hex)
    table_header_bg: str     # Table header background (hex)
    table_header_text: str   # Table header text color (hex)
    table_border: str        # Table border color (hex)
    blockquote_border: str   # Blockquote left border color (hex)
    blockquote_text: str     # Blockquote text color (hex)
    cover_title: str         # Cover page title color (hex)
    cover_accent: str        # Cover page accent line color (hex)


@dataclass(frozen=True)
class WordFonts:
    """Font configuration for Word document."""
    heading: str             # Heading font name
    body: str                # Body text font name
    code: str                # Code block font name


@dataclass(frozen=True)
class WordSizes:
    """Font sizes in points for Word document."""
    h1: int
    h2: int
    h3: int
    h4: int
    body: int
    code: int
    small: int               # Footers, captions


@dataclass(frozen=True)
class WordSpacing:
    """Paragraph spacing in points."""
    after_heading: int       # Space after headings
    after_paragraph: int     # Space after body paragraphs
    line_spacing: float      # Line spacing multiplier (1.0, 1.15, 1.5)


@dataclass(frozen=True)
class WordTheme:
    """Complete theme for Word document generation."""
    name: str
    description: str
    colors: WordColors
    fonts: WordFonts
    sizes: WordSizes
    spacing: WordSpacing
```

### 5.2 Standard Themes

| Theme | Heading Font | Body Font | Heading Color | Style |
|-------|-------------|-----------|---------------|-------|
| **boardroom** | Palatino Linotype | Georgia | `#1A365D` | Corporate, executive with serif fonts |
| **paper** | Segoe UI | Segoe UI | `#2D3748` | Minimal, clean, elegant |
| **terminal** | Consolas | Consolas | `#E2E8F0` | Technical, monospace |
| **spark** | Segoe UI | Segoe UI | `#7C3AED` | Creative, colorful with vibrant accents |
| **thesis** | Times New Roman | Times New Roman | `#1A202C` | Academic, scholarly |
| **obsidian** | Segoe UI | Segoe UI | `#E5E7EB` | Dark theme with subtle highlights |
| **blueprint** | Consolas | Segoe UI | `#1E40AF` | Technical documentation |

### 5.3 Theme-to-Format Mapping

Themes control these python-docx properties:

| Theme Property | python-docx API |
|----------------|-----------------|
| `fonts.heading` | `run.font.name` on heading paragraphs |
| `fonts.body` | `run.font.name` on body paragraphs |
| `fonts.code` | `run.font.name` on code runs |
| `sizes.h1` | `run.font.size = Pt(size)` |
| `colors.heading` | `run.font.color.rgb = RGBColor(...)` |
| `colors.code_bg` | Paragraph shading via `OxmlElement` |
| `colors.table_header_bg` | Cell shading on first row |
| `spacing.after_paragraph` | `paragraph_format.space_after = Pt(n)` |
| `spacing.line_spacing` | `paragraph_format.line_spacing = n` |
| `--page-size` | `section.page_width`, `section.page_height` |
| `--margin` | `section.left_margin`, `section.right_margin`, etc. |

---

## 6. Dependencies

| Library | Version | Rationale |
|---------|---------|-----------|
| **python-docx** | `>=1.1.0` | Industry-standard Word document generation. Mature, well-documented, active maintenance. |
| **markdown-it-py** | `>=3.0.0` | Token-level Markdown parsing. Same library used by cc-powerpoint and cc-markdown. Enables inline formatting preservation. |
| **mdit-py-plugins** | `>=0.4.0` | Extensions: tables, strikethrough, tasklists, footnotes. |
| **typer** | `>=0.9.0` | CLI framework (cc-tools standard). |
| **rich** | `>=13.0.0` | Console output (cc-tools standard). |

**Why token-level parsing instead of HTML->BeautifulSoup:**
The current cc-markdown `word_converter.py` converts Markdown -> HTML -> BeautifulSoup -> python-docx. This pipeline loses inline formatting because `get_text(strip=True)` flattens all HTML tags. Token-level parsing with markdown-it-py provides a stream of open/close tokens (`strong_open`, `em_open`, `code_inline`) that can be directly mapped to python-docx run formatting without any information loss.

---

## 7. Key Design Decisions

### Decision 1: Token-level parsing, not HTML intermediate
**Rationale:** cc-markdown's `word_converter.py` demonstrates the problem with the HTML path: `child.get_text(strip=True)` on line 68 strips all inline formatting from paragraphs. A `<p>Hello <strong>world</strong></p>` becomes just "Hello world" with no bold. Token-level parsing gives us `text("Hello ")`, `strong_open`, `text("world")`, `strong_close` -- directly mappable to python-docx runs.

### Decision 2: InlineRun dataclass for formatting preservation
**Rationale:** Each text segment in a paragraph can have different formatting (bold, italic, code, link). The `InlineRun` dataclass captures this at the smallest granularity. The docx generator maps each `InlineRun` to a `paragraph.add_run()` call with the appropriate `run.font` properties. This is the fundamental unit that makes inline formatting work.

### Decision 3: Element handler pattern (elements/ directory)
**Rationale:** Cover pages, TOC, headers/footers, code blocks, tables, and images each require significant python-docx code (20-80 lines). Putting them in a single generator file would exceed 500 lines and violate the 50-line function limit. Separate handler modules keep each element self-contained, testable, and easy to extend.

### Decision 4: Single command, not subcommands
**Rationale:** cc-word has one input format (Markdown) and one output format (.docx). Unlike cc-excel which has fundamentally different input parsers, cc-word's options are universal. A single command with optional flags (`--cover`, `--toc`, `--header`, `--footer`) is cleaner than subcommands that would share 90% of their options.

### Decision 5: TOC as Word field code
**Rationale:** Word's built-in TOC uses field codes (`TOC \o "1-3" \h \z \u`) that Word populates when the document is opened. This is the standard approach used by every Word document generator. Manually building a TOC from headings would be fragile (wrong page numbers) and wouldn't update when the document is edited. The field code approach means the TOC says "Update this table" on first open, which is expected behavior.

### Decision 6: Cover page from first H1
**Rationale:** When `--cover` is enabled, the first `# Heading` becomes the cover page title and the first paragraph after it (if any) becomes the subtitle. This avoids requiring separate metadata or YAML frontmatter -- the Markdown structure itself drives the cover page. If YAML frontmatter is present (title, subtitle, author, date), those fields take priority.

### Decision 7: Frozen dataclass themes matching cc-powerpoint pattern
**Rationale:** Consistency across cc-tools. cc-powerpoint proved the pattern works: frozen dataclasses are type-safe, IDE-friendly, immutable, and map directly to format API calls. Word's formatting API is property-based (just like PowerPoint's), so the same pattern applies cleanly.

---

## 8. Implementation Sequence

1. **Project scaffolding** -- Directory structure, `pyproject.toml`, `main.py`, `__init__.py`, `__main__.py`
2. **Theme system** -- `themes/__init__.py` with frozen dataclasses, 7 themes, registry functions
3. **Data model** -- `InlineRun`, `Block`, `DocumentModel`, and supporting dataclasses
4. **Inline parser** -- Convert markdown-it-py inline token stream to `list[InlineRun]` with bold/italic/code/link tracking
5. **Document parser** -- Parse full Markdown document into `DocumentModel` (headings, paragraphs, lists, code blocks, tables, images, blockquotes)
6. **DOCX generator (core)** -- Walk `DocumentModel` blocks, create python-docx document with themed formatting
7. **CLI** -- Typer app with all options, wire up parser -> generator pipeline
8. **Element: code_block.py** -- Shaded code block with monospace font and language label
9. **Element: table.py** -- Styled table with themed header row
10. **Element: image.py** -- Embed images with size constraints
11. **Element: blockquote.py** -- Left-bordered blockquote with indent
12. **Element: cover_page.py** -- Title page with accent line and metadata
13. **Element: toc.py** -- Word field code insertion
14. **Element: headers_footers.py** -- Page header (title) and footer (page numbers)
15. **Tests** -- Unit tests for inline parser, document parser, generator, each element
16. **PyInstaller spec** -- `cc-word.spec` with hidden imports
17. **Build scripts** -- `build.ps1` and `build.sh`
18. **Sample files** -- Example Markdown document demonstrating all features

---

## 9. Ecosystem Integration

### 9.1 Build System

- PyInstaller spec bundles all dependencies into `cc-word.exe`
- Build scripts (`build.ps1` / `build.sh`) create venv, install deps, run PyInstaller
- Output deployed to `%LOCALAPPDATA%\cc-tools\bin\cc-word.exe`

### 9.2 Documentation

- Update `docs/cc-tools.md` with cc-word section (commands, options, examples)
- Add cc-word to the Quick Reference table and Requirements Summary

### 9.3 Relationship to cc-markdown

cc-word does NOT replace cc-markdown's Word output. cc-markdown remains the tool for quick Markdown-to-Word conversion as part of its multi-format pipeline. cc-word is the dedicated tool when Word output quality matters: inline formatting, cover pages, TOC, themed styling.

Users should use:
- `cc-markdown report.md -o report.docx` -- Quick conversion, basic formatting
- `cc-word report.md -o report.docx --theme boardroom --cover --toc` -- Professional document

### 9.4 Skills

- Update cc-tools skill to recognize cc-word triggers ("create word doc", "markdown to word", "format document")

### 9.5 Testing

- pytest with `tests/` directory following cc-tools conventions
- Test naming: `test_<function>_<scenario>_<expected_result>`
- Shared fixtures in `conftest.py` (sample Markdown strings, expected document structures)

---

## 10. Verification Plan

### End-to-End Tests

| Test | Input | Expected Output |
|------|-------|-----------------|
| Basic paragraphs | Markdown with plain text paragraphs | `.docx` with Normal-styled paragraphs |
| Inline formatting | `**bold** *italic* \`code\` ~~strike~~` | Runs with correct font properties per segment |
| Mixed inline | `**bold and *italic* inside**` | Nested bold+italic runs |
| Headings H1-H6 | All 6 heading levels | Correct heading styles and font sizes |
| Bullet list | Nested bullet list (2 levels) | Word list paragraphs with correct indentation |
| Ordered list | Numbered list with sub-items | Numbered list style with nesting |
| Code block | Fenced code with language | Shaded paragraph, monospace font, language label |
| Table | Pipe table with header | Styled table, bold header row |
| Image | `![alt](path.png)` | Embedded image with constraints |
| Blockquote | `> quoted text` | Indented paragraph with left border color |
| Horizontal rule | `---` | Page break or styled separator |
| Links | `[text](url)` | Hyperlink run with URL |
| Cover page | `--cover` flag with H1 | Title page with centered title and accent |
| TOC | `--toc` flag | Word TOC field code present |
| Headers/footers | `--header --footer` | Title in header, page number in footer |
| Page size | `--page-size letter` | Letter dimensions (8.5" x 11") |
| Margins | `--margin 0.75in` | 0.75" margins on all sides |
| All 7 themes | Cycled through all themes | All produce valid `.docx` without errors |
| Theme fonts | `--theme boardroom` | Heading font = Palatino Linotype, body = Georgia |
| Theme colors | `--theme boardroom` | Heading color = #1A365D |
| Error: bad file | Non-existent input path | Clear error message, exit code 1 |
| Error: bad output | Output with `.pdf` extension | Clear error message, exit code 1 |

### Manual Verification

1. Open each theme's output in Word -- verify visual appearance matches theme spec
2. Confirm inline formatting renders correctly (bold, italic, code spans visible)
3. Confirm TOC field code prompts "Update this table" on open
4. Confirm cover page appears as first page with correct title
5. Confirm headers show document title, footers show page numbers
6. Confirm images display at reasonable size (not overflowing margins)
7. Confirm code blocks have visible background shading
8. Confirm tables have styled header row distinct from data rows
9. Confirm hyperlinks are clickable in Word
