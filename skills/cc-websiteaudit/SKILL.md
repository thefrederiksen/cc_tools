# cc-websiteaudit

Comprehensive website auditing tool. Crawls sites and grades them across technical SEO, on-page SEO, security, structured data, and AI readiness.

## Commands

### Basic audit

```bash
cc-websiteaudit <url>
cc-websiteaudit https://example.com
```

### Save report

```bash
cc-websiteaudit example.com -o report.pdf
cc-websiteaudit example.com --format json -o audit.json
cc-websiteaudit example.com --format markdown -o audit.md
cc-websiteaudit example.com --format html -o audit.html
```

### Custom crawl

```bash
cc-websiteaudit example.com --pages 50 --depth 4 --verbose
cc-websiteaudit example.com --modules technical-seo,security
cc-websiteaudit example.com --quiet
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<url>` | Website URL to audit (required) | - |
| `-o, --output <path>` | Output file path | stdout |
| `--format <type>` | console, json, html, markdown, pdf | console |
| `--modules <list>` | Comma-separated modules | all |
| `--pages <number>` | Max pages to crawl | 25 |
| `--depth <number>` | Max crawl depth | 3 |
| `--verbose` | Show detailed progress | false |
| `--quiet` | Only show final grade | false |

## Analyzer Modules

- **technical-seo** - robots.txt, sitemaps, canonicals, HTTPS, redirects, status codes
- **on-page-seo** - titles, meta descriptions, headings, alt text, linking, Open Graph
- **security** - HSTS, CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **structured-data** - JSON-LD, Organization/Article/FAQ/Breadcrumb schemas
- **ai-readiness** - /llms.txt, AI crawler access, citability, semantic HTML

## Grades

A+ (97+) through F (<60). Each category scored 0-100, weighted for overall grade.

## Workflow

```bash
# Audit -> Recommendations -> PDF
cc-websiteaudit example.com --format json -o audit.json
cc-brandingrecommendations --audit audit.json -o plan.md
cc-markdown plan.md -o plan.pdf --theme boardroom
```

## Requirements

- Node.js 18+
- Chrome/Chromium (for PDF output and SPA sites)
