# cc-browser

Fast browser automation daemon for Claude Code. Persistent browser connection with element refs for interaction.

**Requirements:**
- Node.js installed
- Chrome, Edge, or Brave browser

---

## Quick Reference

```bash
# Start daemon (keep running in background)
cc-browser daemon

# Launch browser
cc-browser start

# Navigate to URL
cc-browser navigate --url "https://example.com"

# Get page structure with element refs
cc-browser snapshot --interactive

# Click element
cc-browser click --ref e1

# Type into element
cc-browser type --ref e2 --text "hello"

# Take screenshot
cc-browser screenshot
```

---

## Architecture

```
Claude Code (Bash tool)
     |
     v
cc-browser CLI (Node.js)
     | HTTP (localhost:9280)
     v
cc-browser Daemon (keeps browser connection warm)
     | CDP (localhost:9222)
     v
Chrome/Edge/Brave
```

---

## Commands

### Daemon Control

```bash
# Start daemon (keep running)
cc-browser daemon

# Check daemon status
cc-browser status
```

### Browser Lifecycle

```bash
# List available browsers
cc-browser browsers

# List browser profiles
cc-browser profiles
cc-browser profiles --browser edge

# Start browser
cc-browser start
cc-browser start --headless
cc-browser start --browser edge
cc-browser start --browser chrome --profile personal

# Stop browser
cc-browser stop
```

### Navigation

```bash
# Navigate to URL
cc-browser navigate --url "https://example.com"

# Reload page
cc-browser reload

# Go back
cc-browser back

# Go forward
cc-browser forward
```

### Page Inspection

```bash
# Get page structure with element refs
cc-browser snapshot --interactive

# Get page info (URL, title)
cc-browser info

# Get page text
cc-browser text
cc-browser text --selector "article"

# Get page HTML
cc-browser html
cc-browser html --selector "main"
```

### Interactions

```bash
# Click element
cc-browser click --ref e1

# Type into element
cc-browser type --ref e1 --text "hello world"

# Press keyboard key
cc-browser press --key Enter
cc-browser press --key Tab

# Hover over element
cc-browser hover --ref e1

# Select dropdown option
cc-browser select --ref e1 --value "option1"

# Scroll viewport
cc-browser scroll --direction down

# Scroll element into view
cc-browser scroll --ref e1
```

### Screenshots

```bash
# Take screenshot (base64)
cc-browser screenshot

# Full page screenshot
cc-browser screenshot --fullPage

# Screenshot with element labels
cc-browser screenshot-labels
```

### Tabs

```bash
# List tabs
cc-browser tabs

# Open new tab
cc-browser tabs-open
cc-browser tabs-open --url "https://example.com"

# Close tab
cc-browser tabs-close --tab <id>

# Focus tab
cc-browser tabs-focus --tab <id>
```

### Advanced

```bash
# Wait for text
cc-browser wait --text "loaded"

# Wait for time (ms)
cc-browser wait --time 1000

# Run JavaScript
cc-browser evaluate --js "document.title"

# Fill multiple fields
cc-browser fill --fields '[{"ref":"e1","text":"hello"}]'

# Upload file
cc-browser upload --ref e1 --path ./file.pdf
```

---

## Element Refs

The `snapshot` command returns element refs (e1, e2, etc.) for subsequent commands:

```bash
# 1. Get page structure
cc-browser snapshot --interactive

# Output:
# - button "Sign In" [ref=e1]
# - textbox "Email" [ref=e2]
# - textbox "Password" [ref=e3]

# 2. Use refs
cc-browser type --ref e2 --text "user@example.com"
cc-browser type --ref e3 --text "password123"
cc-browser click --ref e1
```

---

## Multi-Profile Usage

```bash
# Start daemons for different profiles (separate terminals)
cc-browser daemon --browser edge --profile work       # Port 9280
cc-browser daemon --browser chrome --profile personal # Port 9282

# Commands auto-detect daemon port from profile
cc-browser start --browser edge --profile work
cc-browser start --browser chrome --profile personal
```

---

## Options

| Option | Description |
|--------|-------------|
| `--port <port>` | Daemon port (default: 9280) |
| `--cdpPort <port>` | Chrome CDP port (default: 9222) |
| `--tab <targetId>` | Target specific tab |
| `--timeout <ms>` | Action timeout |
| `--browser <name>` | Browser: chrome, edge, brave |
| `--profile <name>` | Profile name |
| `--headless` | Run headless |

---

## Examples

### Login to a Website

```bash
# 1. Start browser
cc-browser start

# 2. Navigate
cc-browser navigate --url "https://example.com/login"

# 3. Get element refs
cc-browser snapshot --interactive

# 4. Fill form and submit
cc-browser type --ref e2 --text "username"
cc-browser type --ref e3 --text "password"
cc-browser click --ref e1
```

### Take Screenshot of a Page

```bash
cc-browser start
cc-browser navigate --url "https://example.com"
cc-browser wait --time 2000
cc-browser screenshot --fullPage
```

### Fill and Submit a Form

```bash
cc-browser fill --fields '[
  {"ref":"e1","text":"John Doe"},
  {"ref":"e2","text":"john@example.com"},
  {"ref":"e3","text":"Hello, this is my message"}
]'
cc-browser click --ref e4
```

---

## Why cc-browser?

| Aspect | Playwright MCP | cc-browser |
|--------|---------------|------------|
| Latency | 500-2000ms | 20-50ms |
| Connection | Cold start each call | Persistent |
| Browser | Launches new Chromium | Uses existing Chrome |
| Protocol | MCP + stdio | HTTP (fast) |

---

## LLM Use Cases

1. **Web automation** - "Log into this website and download the report"
2. **Form filling** - "Fill out this form with the provided data"
3. **Web scraping** - "Get the text content from this page"
4. **Testing** - "Click through this user flow and verify each step"
5. **Screenshots** - "Take a screenshot of this webpage"
