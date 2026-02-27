# cc-browser Deployment Guide

## Architecture

cc-browser is a **CLI + daemon pair**, NOT a standalone executable.

- **CLI** (`cli.mjs`) -- sends HTTP requests to the daemon. This is what runs when you type `cc-browser <command>`.
- **Daemon** (`daemon.mjs`) -- a long-running Node.js process that holds the Playwright browser connection and imports `session.mjs`, `interactions.mjs`, `snapshot.mjs`, etc.
- The `cc-browser daemon` command spawns `node daemon.mjs` as a child process -- this **requires source files on disk**.

## Why There Is No `.exe`

- The daemon cannot be packaged into a standalone exe because it spawns itself as a child Node.js process (`node daemon.mjs`).
- The esbuild + pkg build only bundles `cli.mjs` -- it does NOT include the daemon or any of its imports.
- Deploying a `.exe` is misleading: it appears to work for simple CLI commands but silently breaks daemon management.
- On Windows, `.exe` takes precedence over `.cmd` in PATH resolution, so a stale `.exe` will shadow the correct `.cmd` entry point.

**Do NOT build or deploy cc-browser.exe.**

## Runtime Dependencies

- **Node.js** -- must be installed and on PATH (required to run the daemon)
- **playwright-core** -- installed in `cc-browser/node_modules/`

## What Gets Deployed

```
%LOCALAPPDATA%\cc-tools\bin\
  cc-browser.cmd              <- entry point (~40 bytes, calls node)
  cc-browser\
    package.json
    node_modules\             <- playwright-core + deps
    src\
      cli.mjs                 <- CLI (HTTP client)
      daemon.mjs              <- daemon server (long-running)
      session.mjs             <- browser/tab/page management
      interactions.mjs        <- click, type, hover, etc.
      snapshot.mjs            <- ARIA tree / page info
      chrome.mjs              <- Chrome/Edge detection + launch
      human-mode.mjs          <- human-like delays
      captcha.mjs             <- CAPTCHA detection/solving
      vision.mjs              <- Anthropic vision API
      main.mjs                <- legacy standalone entry point
```

## cc-browser.cmd Content

```cmd
@node "%~dp0cc-browser\src\cli.mjs" %*
```

This invokes `cli.mjs` via Node.js. The `%~dp0` expands to the directory containing the `.cmd` file.

## Deployment Procedure

### Manual

1. Copy entire `cc-browser/` directory (src + node_modules + package.json) to `%LOCALAPPDATA%\cc-tools\bin\cc-browser\`
2. Ensure `cc-browser.cmd` exists at `%LOCALAPPDATA%\cc-tools\bin\cc-browser.cmd`
3. Delete any `cc-browser.exe` in that directory -- it will take precedence over `.cmd` and cause confusion
4. After deploying updated source, restart any running daemon:
   ```bash
   cc-browser stop
   cc-browser daemon --workspace edge-work
   ```

### Using npm deploy script

From the `src/cc-browser/` directory:

```bash
npm run deploy
```

This copies source files to the deployed location and removes any stale `.exe`.

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|------------|-----|
| Editing source in repo but not deploying | Daemon runs old code | Run `npm run deploy` then restart daemon |
| Building and deploying `.exe` | `.exe` shadows `.cmd`; daemon commands break | Delete the `.exe`, use `.cmd` only |
| Forgetting to restart daemon after deploy | Daemon still has old code loaded in memory | `cc-browser stop` then `cc-browser daemon` |
| Missing node_modules in deployed dir | Daemon crashes on import | Copy `node_modules/` with the rest of the directory |
