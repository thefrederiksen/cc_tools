# cc-crawl4ai

AI-ready web crawler: crawl pages to clean markdown for LLM/RAG workflows.

**Requirements:**
- `cc-crawl4ai.exe` must be in PATH
- Playwright browsers: `playwright install chromium`

---

## Quick Reference

```bash
# Crawl a URL to markdown
cc-crawl4ai crawl "https://example.com"

# Save to file
cc-crawl4ai crawl URL -o page.md

# Use fit markdown (noise filtered)
cc-crawl4ai crawl URL --fit

# Batch crawl from URL list
cc-crawl4ai batch urls.txt -o ./output/

# Stealth mode (evade bot detection)
cc-crawl4ai crawl URL --stealth
```

---

## Commands

### Single URL Crawl

```bash
# Basic crawl
cc-crawl4ai crawl "https://example.com"

# Save to file
cc-crawl4ai crawl URL -o page.md

# Different output formats
cc-crawl4ai crawl URL -f json -o page.json
cc-crawl4ai crawl URL -f html -o page.html
cc-crawl4ai crawl URL -f raw

# Fit markdown (noise filtered, recommended for LLM)
cc-crawl4ai crawl URL --fit

# Content filter with BM25 query
cc-crawl4ai crawl URL --query "machine learning"
```

### Batch Crawling

```bash
# Crawl multiple URLs
cc-crawl4ai batch urls.txt -o ./output/

# With parallel workers
cc-crawl4ai batch urls.txt -o ./output/ --parallel 10

# With options
cc-crawl4ai batch urls.txt -o ./output/ --fit --stealth
```

### Session Management

```bash
# List saved sessions
cc-crawl4ai session list

# Create session (for authenticated crawling)
cc-crawl4ai session create mysite -u "https://example.com/login" --interactive

# Use session
cc-crawl4ai crawl URL --session mysite

# Delete session
cc-crawl4ai session delete mysite
```

---

## Browser Options

```bash
# Stealth mode (evade bot detection)
cc-crawl4ai crawl URL --stealth

# Different browser
cc-crawl4ai crawl URL --browser firefox

# Headful mode (visible browser)
cc-crawl4ai crawl URL --no-headless

# Custom viewport
cc-crawl4ai crawl URL --viewport 1920x1080

# With proxy
cc-crawl4ai crawl URL --proxy "http://user:pass@host:port"

# Disable images (faster)
cc-crawl4ai crawl URL --text-only

# Custom timeout
cc-crawl4ai crawl URL --timeout 60000
```

---

## Dynamic Content Options

```bash
# Wait for element
cc-crawl4ai crawl URL --wait-for ".content-loaded"

# Wait for network idle
cc-crawl4ai crawl URL --wait-until networkidle

# Scroll full page (infinite scroll)
cc-crawl4ai crawl URL --scroll

# Scroll with delay
cc-crawl4ai crawl URL --scroll --scroll-delay 1000

# Wait for lazy images
cc-crawl4ai crawl URL --lazy-load

# Remove popups/banners
cc-crawl4ai crawl URL --remove-overlays

# Execute custom JavaScript
cc-crawl4ai crawl URL --js "document.querySelector('.popup').remove()"
```

---

## Extraction Options

```bash
# Extract specific CSS selector
cc-crawl4ai crawl URL --css "article.main"

# Extract with XPath
cc-crawl4ai crawl URL --xpath "//article"

# LLM-based extraction
cc-crawl4ai crawl URL --llm-extract --llm-prompt "Extract product prices"

# Extract links
cc-crawl4ai crawl URL --links

# Internal links only
cc-crawl4ai crawl URL --links --internal-links-only
```

---

## Media Options

```bash
# Take screenshot
cc-crawl4ai crawl URL --screenshot

# Generate PDF
cc-crawl4ai crawl URL --pdf

# Extract media URLs
cc-crawl4ai crawl URL --extract-media
```

---

## Options Reference

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `-f, --format` | Format: markdown, json, html, raw, cleaned |
| `--fit` | Use fit markdown (noise filtered) |
| `-q, --query` | BM25 content filter query |
| `-b, --browser` | Browser: chromium, firefox, webkit |
| `--stealth` | Enable stealth mode |
| `--proxy` | Proxy URL |
| `--viewport` | Viewport size (WIDTHxHEIGHT) |
| `--timeout` | Page timeout in ms |
| `--headless/--no-headless` | Run headless |
| `--text-only` | Disable images |
| `-s, --session` | Use saved session |
| `--wait-for` | CSS selector to wait for |
| `--wait-until` | Wait: domcontentloaded, networkidle |
| `--scroll` | Scroll full page |
| `--scroll-delay` | Delay between scrolls (ms) |
| `--lazy-load` | Wait for lazy images |
| `--js` | JavaScript to execute |
| `--remove-overlays` | Remove popups/banners |
| `--css` | CSS selector for extraction |
| `--xpath` | XPath for extraction |
| `--screenshot` | Capture screenshot |
| `--pdf` | Generate PDF |
| `--links` | Extract links |
| `--cache` | Cache mode: on, off, refresh, read-only |

---

## Examples

### Basic Documentation Crawl

```bash
cc-crawl4ai crawl "https://docs.example.com/api" -o api-docs.md --fit
```

### Crawl Dynamic Page

```bash
cc-crawl4ai crawl URL --wait-for ".content" --scroll --remove-overlays
```

### Authenticated Crawling

```bash
# First, create session interactively
cc-crawl4ai session create github -u "https://github.com/login" --interactive
# Browser opens, you log in, close browser

# Now crawl with session
cc-crawl4ai crawl "https://github.com/notifications" --session github
```

### Batch Crawl Documentation

```bash
echo "https://docs.example.com/page1
https://docs.example.com/page2
https://docs.example.com/page3" > urls.txt

cc-crawl4ai batch urls.txt -o ./docs/ --fit --parallel 5
```

### Stealth Mode for Protected Sites

```bash
cc-crawl4ai crawl URL --stealth --wait-until networkidle
```

---

## LLM Use Cases

1. **Research** - "Crawl this documentation page and summarize it"
2. **RAG ingestion** - "Download these pages as clean markdown for indexing"
3. **Content extraction** - "Get the article content from this news page"
4. **Web scraping** - "Extract product information from this page"
5. **Documentation** - "Crawl the API docs for analysis"
