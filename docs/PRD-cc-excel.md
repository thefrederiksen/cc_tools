# PRD: cc-excel

> Convert data (CSV, JSON, Markdown tables) to formatted Excel workbooks.

---

## 1. Overview

**cc-excel** is a CLI tool that creates professional, formatted `.xlsx` files from structured data sources. It targets LLMs and humans who need to produce polished Excel output without manual formatting.

**Problem:** LLMs can generate CSV and JSON easily but cannot produce formatted Excel files. Users must open raw data in Excel and manually apply formatting, column widths, headers, filters, and charts. This is repetitive and error-prone.

**Solution:** A single CLI tool that reads CSV, JSON, or Markdown tables and outputs a fully formatted `.xlsx` workbook with themes, autofilter, auto-sized columns, type-aware formatting, and optional charts.

**Target users:**
- LLMs generating reports, dashboards, and data exports
- Humans who want quick, themed Excel output from the command line

---

## 2. Goals & Non-Goals

### Goals

- Convert CSV, JSON, and Markdown tables to formatted `.xlsx` files
- Auto-detect column types (number, date, percentage, currency, text)
- Apply consistent visual themes matching the cc-tools theme system
- Support autofilter, freeze panes, auto-sized columns out of the box
- Generate basic charts (bar, line, pie) from data columns
- Produce single-file executables via PyInstaller

### Non-Goals

- Reading or modifying existing `.xlsx` files (write-only tool)
- Complex pivot tables or Excel formulas
- VBA macros or Excel scripting
- Multi-sheet relational data (one data source = one sheet per invocation)
- Interactive Excel features (data validation dropdowns, conditional formatting rules)
- Streaming/incremental writes for very large files (target: < 100k rows)

---

## 3. Technical Architecture

### 3.1 Directory Structure

```
src/cc-excel/
    main.py                     # PyInstaller entry point
    cc-excel.spec               # PyInstaller spec
    pyproject.toml              # Project config & dependencies
    requirements.txt            # Pinned runtime deps
    build.ps1                   # Windows build script
    build.sh                    # Unix build script
    samples/
        quarterly-sales.csv     # Example CSV
        api-response.json       # Example JSON
        report-table.md         # Example Markdown table
    src/
        __init__.py             # Package version
        __main__.py             # python -m entry point
        cli.py                  # Typer CLI with subcommands
        parsers/
            __init__.py
            csv_parser.py       # CSV -> SheetData
            json_parser.py      # JSON -> SheetData
            markdown_parser.py  # Markdown table -> SheetData
        type_inference.py       # Auto-detect column types
        xlsx_generator.py       # SheetData + Theme -> .xlsx
        chart_builder.py        # Chart creation helpers
        themes/
            __init__.py         # Theme dataclasses + registry
    tests/
        __init__.py
        test_csv_parser.py
        test_json_parser.py
        test_markdown_parser.py
        test_type_inference.py
        test_xlsx_generator.py
        test_chart_builder.py
        conftest.py             # Shared fixtures
```

### 3.2 Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `cli.py` | Typer app with `from-csv`, `from-json`, `from-markdown` subcommands |
| `parsers/csv_parser.py` | Read CSV with encoding detection, return `SheetData` |
| `parsers/json_parser.py` | Read JSON (array-of-objects or array-of-arrays), return `SheetData` |
| `parsers/markdown_parser.py` | Extract Markdown pipe tables, return `SheetData` |
| `type_inference.py` | Scan column values and assign `ColumnType` (number, date, percentage, currency, text) |
| `xlsx_generator.py` | Accept `SheetData` + `ExcelTheme`, write formatted `.xlsx` via XlsxWriter |
| `chart_builder.py` | Add chart worksheets from column references |
| `themes/__init__.py` | Frozen dataclass theme definitions + registry |

### 3.3 Internal Data Model

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ColumnType(Enum):
    """Detected column data type."""
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    BOOLEAN = "boolean"


@dataclass
class ColumnInfo:
    """Metadata for a single column."""
    name: str
    col_type: ColumnType = ColumnType.TEXT
    width: float = 12.0           # Auto-calculated character width
    number_format: str = ""       # Excel format string (e.g., "#,##0.00")


@dataclass
class SheetData:
    """Parsed tabular data ready for Excel generation."""
    title: str                                # Sheet name / workbook title
    columns: list[ColumnInfo]                 # Column metadata
    rows: list[list[object]]                  # Raw cell values (typed after inference)
    source_file: str = ""                     # Original file path for metadata


class ChartType(Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    COLUMN = "column"


@dataclass
class ChartSpec:
    """Specification for a chart to embed."""
    chart_type: ChartType
    title: str
    category_column: int          # Column index for X-axis / categories
    value_columns: list[int]      # Column indices for Y-axis / values
    sheet_name: str = "Chart"
```

### 3.4 Processing Pipeline

```
Input File (CSV / JSON / Markdown)
        |
        v
    [Parser]  -- selects csv_parser / json_parser / markdown_parser
        |
        v
    SheetData (raw string values)
        |
        v
    [Type Inference]  -- scans values, assigns ColumnType per column
        |
        v
    SheetData (typed values, format strings, widths)
        |
        v
    [XLSX Generator]  -- applies ExcelTheme, writes formatted workbook
        |
        +---> [Chart Builder]  -- optional, adds chart sheet(s)
        |
        v
    Output .xlsx file
```

---

## 4. CLI Interface

### 4.1 Subcommands

The tool uses subcommands because each input format has unique options.

#### `from-csv` -- Convert CSV to Excel

```bash
cc-excel from-csv sales.csv -o sales.xlsx
cc-excel from-csv sales.csv -o sales.xlsx --theme boardroom
cc-excel from-csv data.csv -o report.xlsx --delimiter ";" --encoding utf-8
cc-excel from-csv data.csv -o report.xlsx --no-header
cc-excel from-csv data.csv -o report.xlsx --sheet-name "Q4 Sales"
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `INPUT_FILE` | (required) | Path to CSV file |
| `-o, --output` | (required) | Output .xlsx path |
| `--theme, -t` | `paper` | Theme name |
| `--delimiter` | `,` | CSV delimiter character |
| `--encoding` | `utf-8` | File encoding |
| `--no-header` | `false` | First row is data, not headers |
| `--sheet-name` | filename stem | Worksheet tab name |
| `--no-autofilter` | `false` | Disable autofilter on header row |
| `--no-freeze` | `false` | Disable freeze panes on header row |
| `--chart` | (none) | Add chart: `bar`, `line`, `pie`, `column` |
| `--chart-x` | (none) | Column name or index for chart categories |
| `--chart-y` | (none) | Column name(s) or index(es) for chart values (repeatable) |

#### `from-json` -- Convert JSON to Excel

```bash
cc-excel from-json api-response.json -o report.xlsx
cc-excel from-json data.json -o report.xlsx --theme terminal
cc-excel from-json nested.json -o report.xlsx --json-path "$.results"
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `INPUT_FILE` | (required) | Path to JSON file |
| `-o, --output` | (required) | Output .xlsx path |
| `--theme, -t` | `paper` | Theme name |
| `--json-path` | (root) | JSONPath expression to locate the array |
| `--sheet-name` | filename stem | Worksheet tab name |
| `--no-autofilter` | `false` | Disable autofilter |
| `--no-freeze` | `false` | Disable freeze panes |
| `--chart` | (none) | Chart type |
| `--chart-x` | (none) | Chart category column |
| `--chart-y` | (none) | Chart value column(s) |

**JSON formats supported:**
1. Array of objects: `[{"name": "Alice", "score": 95}, ...]`
2. Array of arrays with header row: `[["name", "score"], ["Alice", 95], ...]`

#### `from-markdown` -- Convert Markdown table to Excel

```bash
cc-excel from-markdown report.md -o report.xlsx
cc-excel from-markdown report.md -o report.xlsx --theme boardroom
cc-excel from-markdown report.md -o report.xlsx --table-index 2
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `INPUT_FILE` | (required) | Path to Markdown file |
| `-o, --output` | (required) | Output .xlsx path |
| `--theme, -t` | `paper` | Theme name |
| `--table-index` | `0` | Which table to extract (0-based) if file has multiple |
| `--all-tables` | `false` | Extract all tables as separate sheets |
| `--sheet-name` | `Table` | Worksheet tab name |
| `--no-autofilter` | `false` | Disable autofilter |
| `--no-freeze` | `false` | Disable freeze panes |

### 4.2 Global Options

```bash
cc-excel --version       # Show version
cc-excel --themes        # List available themes
```

---

## 5. Theme System

### 5.1 Dataclass Definitions

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ExcelColors:
    """Color scheme for Excel formatting."""
    header_bg: str           # Header row background (hex)
    header_text: str         # Header row text color (hex)
    alt_row_bg: str          # Alternating row background (hex)
    border: str              # Cell border color (hex)
    text: str                # Body text color (hex)
    accent: str              # Accent color for charts and highlights (hex)
    chart_colors: tuple[str, ...]  # Series colors for charts (hex tuple)


@dataclass(frozen=True)
class ExcelFonts:
    """Font configuration for Excel."""
    header: str              # Header row font name
    body: str                # Body cell font name
    header_size: int         # Header font size in points
    body_size: int           # Body font size in points


@dataclass(frozen=True)
class ExcelTheme:
    """Complete theme for Excel workbook generation."""
    name: str
    description: str
    colors: ExcelColors
    fonts: ExcelFonts
    header_bold: bool        # Bold header row
    alt_row_shading: bool    # Enable alternating row colors
    border_style: str        # "thin", "medium", "none"
```

### 5.2 Standard Themes

| Theme | Header BG | Header Text | Alt Row | Body Font | Style |
|-------|-----------|-------------|---------|-----------|-------|
| **boardroom** | `#1A365D` | `#FFFFFF` | `#F7FAFC` | Palatino Linotype | Medium borders, serif |
| **paper** | `#4A5568` | `#FFFFFF` | `#F9FAFB` | Segoe UI | Thin borders, clean |
| **terminal** | `#1E1E1E` | `#00FF00` | `#2D2D2D` | Consolas | Thin borders, monospace |
| **spark** | `#7C3AED` | `#FFFFFF` | `#F5F3FF` | Segoe UI | Medium borders, vibrant |
| **thesis** | `#1A202C` | `#FFFFFF` | `#F7FAFC` | Times New Roman | Thin borders, academic |
| **obsidian** | `#374151` | `#E5E7EB` | `#1F2937` | Segoe UI | Thin borders, dark |
| **blueprint** | `#1E40AF` | `#FFFFFF` | `#EFF6FF` | Consolas | Medium borders, technical |

### 5.3 Theme-to-Format Mapping

Themes control these XlsxWriter format properties:

| Theme Property | XlsxWriter Format |
|----------------|-------------------|
| `header_bg` | `set_bg_color()` on header row |
| `header_text` | `set_font_color()` on header row |
| `alt_row_bg` | `set_bg_color()` on even rows |
| `border` | `set_border_color()` on all cells |
| `fonts.header` | `set_font_name()` on header row |
| `fonts.body` | `set_font_name()` on data cells |
| `border_style` | `set_border(1)` thin, `set_border(2)` medium |
| `chart_colors` | `set_custom_property()` on chart series |

---

## 6. Dependencies

| Library | Version | Rationale |
|---------|---------|-----------|
| **XlsxWriter** | `>=3.1.0` | Write-only Excel library. Faster than openpyxl for generation. Zero external deps. Superior chart support. Matches our write-only use case. |
| **markdown-it-py** | `>=3.0.0` | Token-level Markdown parsing for table extraction. Same library used by cc-powerpoint. |
| **mdit-py-plugins** | `>=0.4.0` | Table extension for markdown-it-py. |
| **typer** | `>=0.9.0` | CLI framework (cc-tools standard). |
| **rich** | `>=13.0.0` | Console output (cc-tools standard). |

**Why XlsxWriter over openpyxl:**
1. Write-only -- we never read existing files, so openpyxl's read support is unused weight
2. Performance -- XlsxWriter is significantly faster for generation workloads
3. Zero native deps -- pure Python, no lxml required
4. Chart API -- cleaner, more complete chart creation interface
5. Memory -- streams rows to disk, lower memory for large datasets

---

## 7. Key Design Decisions

### Decision 1: Subcommand pattern instead of single command
**Rationale:** CSV, JSON, and Markdown inputs have fundamentally different options (`--delimiter` for CSV, `--json-path` for JSON, `--table-index` for Markdown). A single command with format auto-detection would lead to a confusing mix of options where most don't apply. Subcommands keep each interface clean and self-documenting.

### Decision 2: XlsxWriter over openpyxl
**Rationale:** cc-excel is strictly a write-only tool. XlsxWriter is purpose-built for generation, is faster, uses less memory (row streaming), has zero native dependencies, and provides a better chart API. openpyxl's read/modify capabilities are unnecessary overhead.

### Decision 3: Type inference in parsers
**Rationale:** Raw CSV and Markdown data arrives as strings. Auto-detecting numbers, dates, percentages, and currency values lets the generator apply correct Excel number formats (`#,##0.00`, `0.0%`, `$#,##0.00`, `yyyy-mm-dd`). Without this, all cells would be text and lose Excel functionality (sorting, summing, charting).

### Decision 4: Dataclass theme system (not CSS)
**Rationale:** Excel formatting is set via API calls (font name, size, color, borders), not stylesheets. A dataclass maps directly to XlsxWriter format properties with zero translation layer. This matches cc-powerpoint's proven pattern and keeps themes type-safe and IDE-friendly.

### Decision 5: Charts as optional CLI flags, not a separate command
**Rationale:** Charts are derived from the same data being tabulated. Requiring a separate step would force users to specify the data source twice. `--chart bar --chart-x 0 --chart-y 1` is concise and co-located with the data command.

### Decision 6: Autofilter and freeze panes on by default
**Rationale:** Nearly every data table benefits from filterable headers and a frozen header row. Making these the default reduces the common case to zero flags. Users who need plain output can opt out with `--no-autofilter` and `--no-freeze`.

### Decision 7: Single sheet per invocation
**Rationale:** Each subcommand processes one data source into one worksheet. Multi-sheet workbooks add complexity (sheet naming conflicts, cross-sheet references) without clear CLI ergonomics. The exception is `--all-tables` for Markdown files with multiple tables, where each table becomes a sheet.

---

## 8. Implementation Sequence

1. **Project scaffolding** -- Directory structure, `pyproject.toml`, `main.py`, `__init__.py`, `__main__.py`
2. **Theme system** -- `themes/__init__.py` with frozen dataclasses, 7 themes, registry functions
3. **Data model** -- `ColumnType`, `ColumnInfo`, `SheetData`, `ChartSpec` dataclasses
4. **CSV parser** -- Read CSV, return `SheetData` with raw string values
5. **Type inference** -- Column scanning, type detection, format string assignment
6. **XLSX generator** -- Accept `SheetData` + `ExcelTheme`, produce formatted workbook (headers, borders, autofilter, freeze, auto-width)
7. **CLI: `from-csv` subcommand** -- Wire up parser -> inference -> generator pipeline with Typer
8. **JSON parser** -- Array-of-objects and array-of-arrays support
9. **CLI: `from-json` subcommand** -- Wire up with `--json-path` option
10. **Markdown parser** -- Extract pipe tables using markdown-it-py tokens
11. **CLI: `from-markdown` subcommand** -- Wire up with `--table-index` and `--all-tables`
12. **Chart builder** -- Create chart sheets from `ChartSpec`
13. **Chart CLI flags** -- Add `--chart`, `--chart-x`, `--chart-y` to all subcommands
14. **Tests** -- Unit tests for each module (parsers, inference, generator, charts)
15. **PyInstaller spec** -- `cc-excel.spec` with hidden imports
16. **Build scripts** -- `build.ps1` and `build.sh`
17. **Sample files** -- Example CSV, JSON, Markdown inputs

---

## 9. Ecosystem Integration

### 9.1 Build System

- PyInstaller spec bundles all dependencies into `cc-excel.exe`
- Build scripts (`build.ps1` / `build.sh`) create venv, install deps, run PyInstaller
- Output deployed to `%LOCALAPPDATA%\cc-tools\bin\cc-excel.exe`

### 9.2 Documentation

- Update `docs/cc-tools.md` with cc-excel section (commands, options, examples)
- Add cc-excel to the Quick Reference table and Requirements Summary

### 9.3 Skills

- Update cc-tools skill to recognize cc-excel triggers ("create excel", "csv to excel", "format spreadsheet")

### 9.4 Testing

- pytest with `tests/` directory following cc-tools conventions
- Test naming: `test_<function>_<scenario>_<expected_result>`
- Shared fixtures in `conftest.py` (sample CSV strings, JSON objects, Markdown tables)

---

## 10. Verification Plan

### End-to-End Tests

| Test | Input | Expected Output |
|------|-------|-----------------|
| CSV basic | 3-column CSV with headers | `.xlsx` with header formatting, autofilter, freeze pane |
| CSV types | CSV with numbers, dates, percentages | Correct Excel number formats per column |
| CSV chart | Sales CSV + `--chart bar` | Workbook with data sheet + chart sheet |
| CSV no-header | CSV without headers + `--no-header` | Auto-generated column names (A, B, C) |
| CSV delimiter | Semicolon-delimited CSV + `--delimiter ";"` | Correct parsing |
| JSON objects | Array of objects | Headers from keys, data from values |
| JSON arrays | Array of arrays with header | First row as headers |
| JSON path | Nested JSON + `--json-path "$.data"` | Extracts correct sub-array |
| Markdown single | `.md` with one pipe table | Single-sheet workbook |
| Markdown multi | `.md` with 3 tables + `--all-tables` | 3-sheet workbook |
| Theme applied | Any input + `--theme boardroom` | Header colors, fonts, borders match theme spec |
| All 7 themes | CSV input cycled through all themes | All produce valid `.xlsx` without errors |
| Error: bad file | Non-existent input path | Clear error message, exit code 1 |
| Error: bad JSON | Malformed JSON | Clear error message, exit code 1 |
| Error: no table | Markdown with no tables | Clear error message, exit code 1 |

### Manual Verification

1. Open each theme's output in Excel -- verify visual appearance matches theme spec
2. Confirm autofilter dropdowns work on header row
3. Confirm freeze pane keeps header visible when scrolling
4. Confirm number columns sort numerically (not alphabetically)
5. Confirm date columns display in expected format
6. Confirm chart renders with correct data series
