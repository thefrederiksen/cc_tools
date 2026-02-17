# cc_crawl4ai

AI-ready web crawler that extracts clean markdown from websites. Built on [Crawl4AI](https://github.com/unclecode/crawl4ai).

## Features

- **Clean Markdown Output** - Extract LLM-ready content from any webpage
- **Batch Processing** - Crawl multiple URLs in parallel
- **Session Management** - Save login sessions for authenticated crawling
- **Stealth Mode** - Evade bot detection
- **LLM Extraction** - Use GPT/Ollama to extract structured data
- **JSON Schema Extraction** - CSS/XPath-based structured extraction
- **Screenshot Capture** - Save screenshots during crawl
- **BM25 Filtering** - Extract only content relevant to your query
- **Multiple Browsers** - Chromium, Firefox, or WebKit

## Installation

```bash
# From source
cd src/cc_crawl4ai
pip install -e .

# Run Playwright setup (required once)
playwright install chromium
```

## Quick Start

```bash
# Crawl a single page to markdown
cc_crawl4ai crawl https://example.com -o page.md

# Crawl with noise filtering
cc_crawl4ai crawl https://example.com --fit -o clean.md

# Extract only relevant content
cc_crawl4ai crawl https://docs.python.org --query "async await" -o async.md

# Batch crawl URLs in parallel
cc_crawl4ai batch urls.txt -o ./results --parallel 10
```

## Commands

### crawl

Crawl a single URL and extract content.

```bash
cc_crawl4ai crawl <url> [options]
```

**Output Options:**
| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `-f, --format` | Output format: markdown, json, html, raw |
| `--fit` | Use fit markdown (noise filtered) |
| `-q, --query` | BM25 content filter query |

**Browser Options:**
| Option | Description |
|--------|-------------|
| `-b, --browser` | Browser: chromium, firefox, webkit |
| `--stealth` | Enable stealth mode (evade bot detection) |
| `--proxy` | Proxy URL (http://user:pass@host:port) |
| `--viewport` | Viewport size (WIDTHxHEIGHT) |
| `--timeout` | Page timeout in milliseconds |
| `--headless/--no-headless` | Run browser headless |

**Session Options:**
| Option | Description |
|--------|-------------|
| `-s, --session` | Use saved session |

**Dynamic Content:**
| Option | Description |
|--------|-------------|
| `--wait-for` | CSS selector to wait for |
| `--scroll` | Scroll full page before extraction |
| `--scroll-delay` | Delay between scrolls in ms |
| `--lazy-load` | Wait for lazy-loaded images |
| `--js` | JavaScript to execute before extraction |

**Extraction:**
| Option | Description |
|--------|-------------|
| `--css` | CSS selector for extraction |
| `--xpath` | XPath for extraction |
| `--schema` | JSON schema file for structured extraction |
| `--llm-extract` | Use LLM for extraction |
| `--llm-model` | LLM model (default: gpt-4o-mini) |
| `--llm-prompt` | Prompt for LLM extraction |

**Media:**
| Option | Description |
|--------|-------------|
| `--screenshot` | Capture screenshot |
| `--screenshot-path` | Screenshot output path |
| `--extract-media` | Extract images/video URLs |

**Cache:**
| Option | Description |
|--------|-------------|
| `--cache` | Cache mode: on, off, refresh, read-only |

**Links:**
| Option | Description |
|--------|-------------|
| `--links` | Extract and show links |

### batch

Crawl multiple URLs in parallel.

```bash
cc_crawl4ai batch <urls_file> -o <output_dir> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-o, --output-dir` | Output directory for results (required) |
| `-p, --parallel` | Number of parallel crawls (default: 5) |
| `-f, --format` | Output format: markdown, json, html, raw |
| `--fit` | Use fit markdown |
| `--stealth` | Enable stealth mode |
| `--screenshot` | Capture screenshots |

**URLs File Format:**
```
# Comments start with #
https://example.com/page1
https://example.com/page2
https://example.com/page3
```

### session

Manage browser sessions for authenticated crawling.

```bash
# List sessions
cc_crawl4ai session list

# Create session with interactive login
cc_crawl4ai session create mysite -u https://example.com/login --interactive

# Create session without login
cc_crawl4ai session create mysite -b firefox -d "My site session"

# Use session for crawling
cc_crawl4ai crawl https://example.com/dashboard --session mysite

# Delete session
cc_crawl4ai session delete mysite

# Rename session
cc_crawl4ai session rename oldname newname

# Show session info
cc_crawl4ai session info mysite
```

## Examples

### Basic Crawling

```bash
# Simple crawl
cc_crawl4ai crawl https://example.com

# Save to file
cc_crawl4ai crawl https://example.com -o page.md

# Get JSON output
cc_crawl4ai crawl https://example.com -f json -o page.json

# Get raw HTML
cc_crawl4ai crawl https://example.com -f raw -o page.html
```

### Content Filtering

```bash
# Filter for specific content using BM25
cc_crawl4ai crawl https://docs.python.org/3/library/asyncio.html \
  --query "event loop create task" \
  -o asyncio.md

# Use fit markdown to remove noise
cc_crawl4ai crawl https://news.site.com/article --fit -o article.md
```

### Dynamic Content

```bash
# Wait for element to load
cc_crawl4ai crawl https://spa-site.com --wait-for ".content-loaded"

# Scroll to load infinite scroll content
cc_crawl4ai crawl https://infinite-scroll.com --scroll --scroll-delay 1000

# Execute JS before extraction
cc_crawl4ai crawl https://site.com --js "document.querySelector('.expand').click()"
```

### Stealth Mode

```bash
# Evade bot detection
cc_crawl4ai crawl https://protected-site.com --stealth

# With proxy
cc_crawl4ai crawl https://site.com --stealth --proxy http://user:pass@proxy:8080
```

### LLM Extraction

```bash
# Extract structured data using LLM
cc_crawl4ai crawl https://store.com/product \
  --llm-extract \
  --llm-model gpt-4o \
  --llm-prompt "Extract product name, price, and description as JSON" \
  -o product.json
```

### JSON Schema Extraction

```bash
# Create schema file (product_schema.json)
# {
#   "name": "products",
#   "baseSelector": ".product-card",
#   "fields": [
#     {"name": "title", "selector": "h2", "type": "text"},
#     {"name": "price", "selector": ".price", "type": "text"},
#     {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"}
#   ]
# }

cc_crawl4ai crawl https://store.com/products --schema product_schema.json -o products.json
```

### Authenticated Crawling

```bash
# Create session with interactive login
cc_crawl4ai session create github -u https://github.com/login --interactive
# Browser opens, you log in manually, close browser when done

# Now crawl authenticated pages
cc_crawl4ai crawl https://github.com/settings/profile --session github -o profile.md
```

### Batch Processing

```bash
# Create urls.txt
# https://example.com/page1
# https://example.com/page2
# https://example.com/page3

# Crawl all URLs with 10 parallel workers
cc_crawl4ai batch urls.txt -o ./results --parallel 10

# With screenshots
cc_crawl4ai batch urls.txt -o ./results --parallel 5 --screenshot

# With stealth mode
cc_crawl4ai batch urls.txt -o ./results --parallel 3 --stealth
```

### Screenshots

```bash
# Capture screenshot
cc_crawl4ai crawl https://example.com --screenshot --screenshot-path page.png

# Batch with screenshots
cc_crawl4ai batch urls.txt -o ./results --screenshot
```

## Output Directory Structure (Batch)

```
results/
  page_0000.md
  page_0001.md
  page_0002.md
  screenshot_0000.png  (if --screenshot)
  screenshot_0001.png
  batch_summary.json
```

## Session Storage

Sessions are stored in `~/.cc_crawl4ai/sessions/`:

```
~/.cc_crawl4ai/
  sessions/
    mysite/
      session.json      # Session metadata
      profile/          # Browser profile with cookies/auth
  cache/                # Crawl cache
```

## Building Executable

```bash
cd src/cc_crawl4ai
pip install pyinstaller
pyinstaller --onefile --name cc_crawl4ai main.py
```

The executable will be in `dist/cc_crawl4ai.exe`.

## License

MIT
