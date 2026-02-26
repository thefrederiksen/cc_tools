# cc-brandingrecommendations

Branding and SEO recommendations engine. Reads cc-websiteaudit JSON reports and generates prioritized action plans with weekly schedules.

## Commands

### Generate recommendations (console)

```bash
cc-brandingrecommendations --audit <path-to-audit.json>
```

### Save as markdown

```bash
cc-brandingrecommendations --audit audit.json -o plan.md
```

### Save as JSON

```bash
cc-brandingrecommendations --audit audit.json --format json -o plan.json
```

### With budget and targeting

```bash
cc-brandingrecommendations --audit audit.json --budget high --industry saas --keywords "seo,marketing" --competitors "rival1.com,rival2.com"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--audit <path>` | Path to cc-websiteaudit JSON report (required) | - |
| `-o, --output <path>` | Output file path | stdout |
| `--format <type>` | console, json, markdown | console |
| `--budget <level>` | low (5h/wk), medium (10h/wk), high (20h/wk) | medium |
| `--industry <type>` | Industry vertical for tailored recs | - |
| `--keywords <list>` | Comma-separated target keywords | - |
| `--competitors <list>` | Comma-separated competitor domains | - |
| `--verbose` | Show detailed progress | false |

## Typical Workflow

```bash
# Step 1: Audit the website
cc-websiteaudit example.com --format json -o audit.json

# Step 2: Generate recommendations
cc-brandingrecommendations --audit audit.json -o plan.md

# Step 3: Convert to PDF
cc-markdown plan.md -o plan.pdf --theme boardroom
```

## Output

Generates prioritized recommendations across 8 areas:
- Technical SEO, On-Page SEO, Security, Structured Data, AI Readiness
- Content Strategy, Social Presence, Backlinks

Each recommendation includes: what the issue is, why it matters, how to fix it (step-by-step), and how to measure success.

Weekly plan distributes tasks across 12 weeks based on budget constraints.

## Requirements

- Node.js 18+
- cc-websiteaudit JSON output as input
