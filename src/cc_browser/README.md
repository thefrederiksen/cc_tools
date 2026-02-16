# cc-browser

Fast browser automation daemon for Claude Code. Extracted from OpenClaw's browser module with unwanted dependencies removed.

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

## Why This Exists

- **No MCP overhead** - Direct CLI, no MCP protocol latency
- **Persistent connection** - Daemon keeps Playwright/CDP connection warm
- **Fast commands** - ~20-50ms per command vs 500-800ms for cold start
- **Uses existing logins** - Isolated profile but real Chrome
- **No dependencies on pi-agent-core** - Standalone module

## Quick Start

```bash
# Terminal 1: Start the daemon (keeps running)
cd cc-browser
node src/daemon.mjs

# Terminal 2: Send commands
node src/cli.mjs start                           # Launch Chrome
node src/cli.mjs navigate --url "https://example.com"
node src/cli.mjs snapshot --interactive          # Get element refs
node src/cli.mjs click --ref e1                  # Click element
node src/cli.mjs type --ref e2 --text "hello"    # Type into element
node src/cli.mjs screenshot                      # Take screenshot
node src/cli.mjs stop                            # Close browser
```

## Commands

### Daemon
| Command | Description |
|---------|-------------|
| `daemon` | Start the daemon (foreground) |
| `status` | Check daemon and browser status |

### Browser Lifecycle
| Command | Description |
|---------|-------------|
| `browsers` | List available browsers |
| `profiles [--browser edge]` | List Chrome/Edge profiles with emails |
| `start [--headless]` | Launch with isolated profile |
| `start --browser edge` | Launch Edge instead of Chrome |
| `start --profileDir "Profile 1"` | Use existing Chrome profile (requires Chrome closed) |
| `stop` | Close browser |

### Navigation
| Command | Description |
|---------|-------------|
| `navigate --url <url>` | Go to URL |
| `reload` | Reload page |
| `back` | Go back |
| `forward` | Go forward |

### Page Inspection
| Command | Description |
|---------|-------------|
| `snapshot [--interactive]` | Get page structure with element refs |
| `info` | Get URL, title, viewport |
| `text [--selector <css>]` | Get page text |
| `html [--selector <css>]` | Get page HTML |

### Interactions
| Command | Description |
|---------|-------------|
| `click --ref <e1>` | Click element |
| `type --ref <e1> --text "hi"` | Type into element |
| `press --key Enter` | Press keyboard key |
| `hover --ref <e1>` | Hover over element |
| `select --ref <e1> --value "opt"` | Select dropdown |
| `scroll [--direction down]` | Scroll viewport |
| `scroll --ref <e1>` | Scroll element into view |

### Screenshots
| Command | Description |
|---------|-------------|
| `screenshot [--fullPage]` | Take screenshot (base64) |
| `screenshot-labels` | Screenshot with element labels |

### Tabs
| Command | Description |
|---------|-------------|
| `tabs` | List all tabs |
| `tabs-open [--url <url>]` | Open new tab |
| `tabs-close --tab <id>` | Close tab |
| `tabs-focus --tab <id>` | Focus tab |

### Advanced
| Command | Description |
|---------|-------------|
| `wait --text "loaded"` | Wait for text |
| `wait --time 1000` | Wait for time (ms) |
| `evaluate --js "document.title"` | Run JavaScript |
| `fill --fields '[...]'` | Fill multiple form fields |
| `upload --ref <e1> --path <file>` | Upload file |

## Element Refs

The `snapshot` command returns element refs (e1, e2, etc.) that you can use in subsequent commands:

```bash
# Get the page structure
node src/cli.mjs snapshot --interactive
# Output: - button "Sign In" [ref=e1]
#         - textbox "Email" [ref=e2]

# Use the refs
node src/cli.mjs type --ref e2 --text "user@example.com"
node src/cli.mjs click --ref e1
```

## Options

| Option | Description |
|--------|-------------|
| `--port <port>` | Daemon port (default: 9280) |
| `--cdpPort <port>` | Chrome CDP port (default: 9222) |
| `--tab <targetId>` | Target specific tab |
| `--timeout <ms>` | Action timeout |

## Files

```
cc-browser/
  src/
    daemon.mjs        # HTTP server
    cli.mjs           # CLI client
    session.mjs       # Playwright connection & page state
    interactions.mjs  # Click, type, hover, drag, etc.
    snapshot.mjs      # Page snapshots & ref generation
    chrome.mjs        # Chrome detection & launch
  package.json
  cc-browser.cmd      # Windows launcher
```

## Ports

| Port | Purpose |
|------|---------|
| 9280 | Daemon HTTP API |
| 9222 | Chrome CDP |

## Comparison to MCP

| Aspect | Playwright MCP | cc-browser |
|--------|---------------|------------|
| Latency | 500-2000ms | 20-50ms |
| Connection | Cold start each call | Persistent |
| Browser | Launches new Chromium | Uses existing Chrome |
| Protocol | MCP + stdio | HTTP (fast) |
| Dependencies | @playwright/mcp | playwright-core only |
