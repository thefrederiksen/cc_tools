# cc-excel

Convert CSV, JSON, and Markdown tables to professionally formatted Excel workbooks (.xlsx).

## Commands

### From CSV

```bash
cc-excel from-csv <input.csv> -o <output.xlsx>
cc-excel from-csv data.csv -o report.xlsx --theme boardroom
cc-excel from-csv data.csv -o report.xlsx --delimiter ";" --no-header
```

### From JSON

```bash
cc-excel from-json <input.json> -o <output.xlsx>
cc-excel from-json nested.json -o report.xlsx --json-path "$.results"
```

### From Markdown

```bash
cc-excel from-markdown <input.md> -o <output.xlsx>
cc-excel from-markdown report.md -o report.xlsx --all-tables
cc-excel from-markdown report.md -o report.xlsx --table-index 2
```

### With Charts

```bash
cc-excel from-csv sales.csv -o chart.xlsx --chart bar --chart-x Quarter --chart-y Revenue
cc-excel from-csv sales.csv -o chart.xlsx --chart line --chart-x 0 --chart-y 1 --chart-y 2
```

### Utility

```bash
cc-excel --version
cc-excel --themes
```

## Key Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output .xlsx file path (required) | - |
| `-t, --theme` | Theme: boardroom, paper, terminal, spark, thesis, obsidian, blueprint | paper |
| `--chart` | Chart type: bar, line, pie, column | - |
| `--chart-x` | Column for chart categories | - |
| `--chart-y` | Column for chart values (repeatable) | - |
| `--json-path` | JSONPath to data array | - |
| `--all-tables` | Extract all Markdown tables | false |
| `--table-index` | Which Markdown table (0-based) | 0 |
| `--delimiter` | CSV delimiter | , |
| `--no-header` | CSV has no header row | false |
| `--sheet-name` | Custom worksheet tab name | - |

## Features

- Automatic type inference (integer, float, percentage, currency, date, boolean)
- 7 professional themes with custom colors, fonts, borders
- Autofilter on header row, freeze top pane
- Dynamic column widths
- Chart generation on separate worksheet

## Requirements

- Python 3.11+
