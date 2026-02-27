#!/usr/bin/env node
// CC Browser - CLI Client
// Fast browser automation for Claude Code
// Usage: node cli.mjs <command> [options]

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync, existsSync, readdirSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const DEFAULT_DAEMON_PORT = 9280;
const DEFAULT_CDP_PORT = 9222;

// Lockfile path for daemon port auto-detection
function getLockfilePath() {
  const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
  return join(localAppData, 'cc-browser', 'daemon.lock');
}

// Read lockfile to get running daemon port
function readLockfile() {
  const lockPath = getLockfilePath();
  if (!existsSync(lockPath)) {
    return null;
  }
  try {
    const content = readFileSync(lockPath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.error(`[DEBUG] Failed to read lockfile: ${err.message}`);
    return null;
  }
}

// Get workspace directory path
function getWorkspaceDir(browser, workspace) {
  const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
  return join(localAppData, 'cc-browser', `${browser}-${workspace}`);
}

// Read workspace.json configuration
function readWorkspaceConfig(browser, workspace) {
  const workspaceDir = getWorkspaceDir(browser, workspace);
  const configPath = join(workspaceDir, 'workspace.json');

  if (!existsSync(configPath)) {
    return null;
  }

  const content = readFileSync(configPath, 'utf8');
  return JSON.parse(content);
}

// Resolve alias to browser+workspace
function resolveAlias(alias) {
  const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
  const ccBrowserDir = join(localAppData, 'cc-browser');

  if (!existsSync(ccBrowserDir)) return null;

  const dirs = readdirSync(ccBrowserDir);
  for (const dir of dirs) {
    const configPath = join(ccBrowserDir, dir, 'workspace.json');
    if (existsSync(configPath)) {
      const config = JSON.parse(readFileSync(configPath, 'utf8'));
      if (config.aliases && config.aliases.includes(alias)) {
        const [browser, ...workspaceParts] = dir.split('-');
        const workspace = workspaceParts.join('-');
        return { browser, workspace, config };
      }
    }
  }
  return null;
}

// Get daemon port from workspace.json, lockfile, or default
function getDaemonPort(args) {
  // If port is explicitly provided, use it
  if (args.port) {
    console.error(`[DEBUG] Using explicit port: ${args.port}`);
    return args.port;
  }

  // If browser and workspace are specified, try to read from workspace.json
  if (args.browser && args.workspace) {
    console.error(`[DEBUG] Looking for ${args.browser}-${args.workspace} config`);
    const config = readWorkspaceConfig(args.browser, args.workspace);
    if (config && config.daemonPort) {
      console.error(`[DEBUG] Found daemonPort: ${config.daemonPort}`);
      return config.daemonPort;
    }
    console.error(`[DEBUG] No config or daemonPort found`);
  } else if (args.workspace && !args.browser) {
    // Workspace specified without browser - try to resolve as alias
    console.error(`[DEBUG] Resolving alias: ${args.workspace}`);
    const resolved = resolveAlias(args.workspace);
    if (resolved) {
      console.error(`[DEBUG] Alias resolved: ${resolved.browser}-${resolved.workspace}`);
      // Update args with resolved browser/workspace for downstream use
      args.browser = resolved.browser;
      args.workspace = resolved.workspace;
      if (resolved.config.daemonPort) {
        console.error(`[DEBUG] Found daemonPort: ${resolved.config.daemonPort}`);
        return resolved.config.daemonPort;
      }
    }
    console.error(`[DEBUG] Alias not found: ${args.workspace}`);
  } else {
    // No browser/workspace specified - check lockfile for running daemon
    console.error(`[DEBUG] No browser/workspace specified, checking lockfile...`);
    const lockData = readLockfile();
    if (lockData && lockData.port) {
      console.error(`[DEBUG] Found running daemon via lockfile: port=${lockData.port}, browser=${lockData.browser}, workspace=${lockData.workspace}`);
      return lockData.port;
    }
    console.error(`[DEBUG] No lockfile found`);
  }

  console.error(`[DEBUG] Using default port: ${DEFAULT_DAEMON_PORT}`);
  return DEFAULT_DAEMON_PORT;
}

// ---------------------------------------------------------------------------
// Argument Parser
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = { _: [] };
  const tokens = argv.slice(2);

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const next = tokens[i + 1];
      if (next && !next.startsWith('--')) {
        // Try to parse as JSON for complex values (arrays, objects)
        // If not valid JSON, use as plain string - this is intentional
        try {
          args[key] = JSON.parse(next);
        } catch (_parseError) {
          args[key] = next;
        }
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(token);
    }
  }

  return args;
}

// ---------------------------------------------------------------------------
// HTTP Client
// ---------------------------------------------------------------------------

async function request(method, path, body, port = DEFAULT_DAEMON_PORT) {
  const url = `http://127.0.0.1:${port}${path}`;
  console.error(`[DEBUG] Request: ${method} ${url}`);

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(60000),
    });

    const data = await res.json();
    return data;
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.cause?.code === 'ECONNREFUSED') {
      return {
        success: false,
        error: `Daemon not running on port ${port}. Start it with: cc-browser daemon`,
      };
    }
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Output Helpers
// ---------------------------------------------------------------------------

function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

function outputError(message) {
  console.error(JSON.stringify({ success: false, error: message }, null, 2));
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

const commands = {
  // Help
  help: () => {
    console.log(`
cc-browser - Fast browser automation for Claude Code

USAGE:
  cc-browser <command> [options]

DAEMON:
  cc-browser daemon              Start the daemon (keeps running)
  cc-browser status              Check daemon and browser status

BROWSER LIFECYCLE:
  cc-browser browsers                       List available browsers
  cc-browser profiles [--browser chrome]    List Chrome/Edge built-in profiles (with emails)
  cc-browser workspaces                     List configured cc-browser workspaces
  cc-browser favorites --workspace work     Get favorites from workspace.json
  cc-browser start                          Start with default isolated workspace
  cc-browser start --browser edge           Start Edge (default workspace)
  cc-browser start --workspace mindzie      Start using workspace alias
  cc-browser start --browser chrome --workspace personal  Start Chrome with workspace
  cc-browser start --profileDir "Profile 1" Use existing system Chrome profile
  cc-browser start --no-indicator           Start without automation info bar
  cc-browser stop                           Stop browser

NAVIGATION:
  cc-browser navigate --url <url>              Go to URL
  cc-browser reload                            Reload page
  cc-browser back                              Go back
  cc-browser forward                           Go forward

PAGE INSPECTION:
  cc-browser snapshot [--interactive]          Get page structure with element refs
  cc-browser info                              Get page URL, title, viewport
  cc-browser text [--selector <css>]           Get page text content
  cc-browser html [--selector <css>]           Get page HTML

INTERACTIONS:
  cc-browser click --ref <e1>                  Click element by ref
  cc-browser type --ref <e1> --text "hello"    Type into element
  cc-browser press --key Enter                 Press keyboard key
  cc-browser hover --ref <e1>                  Hover over element
  cc-browser select --ref <e1> --value "opt"   Select dropdown option
  cc-browser scroll [--direction down]         Scroll viewport
  cc-browser scroll --ref <e1>                 Scroll element into view

SCREENSHOTS:
  cc-browser screenshot [--fullPage]           Take screenshot (base64)
  cc-browser screenshot-labels                 Screenshot with element labels

TABS:
  cc-browser tabs                              List all tabs
  cc-browser tabs-open [--url <url>]           Open new tab
  cc-browser tabs-close --tab <targetId>       Close tab
  cc-browser tabs-focus --tab <targetId>       Focus tab

MODE:
  cc-browser mode                              Show current mode
  cc-browser mode human                        Set human mode (delays + mouse curves)
  cc-browser mode fast                         Set fast mode (instant, no delays)
  cc-browser mode stealth                      Set stealth mode (human + anti-detect)
  cc-browser start --workspace x --mode human  Start with specific mode

CAPTCHA:
  cc-browser captcha detect                    Detect CAPTCHA on current page
  cc-browser captcha solve                     Auto-solve detected CAPTCHA
  cc-browser captcha solve --attempts 5        Solve with max attempts

ADVANCED:
  cc-browser wait --text "loaded"              Wait for text to appear
  cc-browser wait --time 1000                  Wait for time (ms)
  cc-browser evaluate --js "document.title"    Run JavaScript
  cc-browser fill --fields '[...]'             Fill multiple form fields
  cc-browser upload --ref <e1> --path <file>   Upload file

OPTIONS:
  --port <port>       Daemon port (default: 9280)
  --cdpPort <port>    Chrome CDP port (default: 9222)
  --browser <name>    Browser to use: chrome, edge, brave
  --workspace <name>  Named workspace for isolated sessions (persists logins)
  --no-indicator      Hide the automation info bar (shown by default)
  --tab <targetId>    Target specific tab
  --timeout <ms>      Action timeout

EXAMPLES:
  # Start daemon (run in background terminal)
  cc-browser daemon

  # List available browsers and Chrome profiles
  cc-browser browsers
  cc-browser profiles                      # List system Chrome profiles
  cc-browser profiles --browser edge       # List system Edge profiles
  cc-browser workspaces                    # List cc-browser workspaces

  # Named workspaces (recommended - persistent logins, isolated sessions)
  cc-browser start --workspace mindzie              # Use alias
  cc-browser start --browser edge --workspace work  # Edge for work
  cc-browser start --browser chrome --workspace personal  # Chrome personal

  # Simple start (default workspace)
  cc-browser start --browser edge
  cc-browser start --browser chrome

  # Use existing system Chrome/Edge profile (requires all browser windows closed)
  cc-browser start --profileDir "Default"
  cc-browser start --profileDir "Profile 1"
  cc-browser start --browser edge --profileDir "Default"

  # Basic workflow
  cc-browser start --workspace mindzie
  cc-browser navigate --url "https://example.com"
  cc-browser snapshot --interactive
  cc-browser click --ref e3
  cc-browser type --ref e4 --text "hello"
  cc-browser screenshot
  cc-browser stop

  # Workspace data stored at: %LOCALAPPDATA%\\cc-browser\\<browser>-<workspace>\\

MULTI-WORKSPACE (SIMULTANEOUS BROWSERS):
  Each workspace has its own ports defined in workspace.json:
  - edge-work: daemon=9280, cdp=9222
  - chrome-work: daemon=9281, cdp=9223
  - chrome-personal: daemon=9282, cdp=9224

  # Start daemons for each workspace (in separate terminals):
  cc-browser daemon --workspace mindzie                     # Port 9280
  cc-browser daemon --browser chrome --workspace work       # Port 9281
  cc-browser daemon --browser chrome --workspace personal   # Port 9282

  # Commands auto-detect daemon port from workspace.json:
  cc-browser start --workspace mindzie
  cc-browser start --browser chrome --workspace work
  cc-browser start --browser chrome --workspace personal
`);
  },

  // Start daemon (foreground)
  daemon: async (args) => {
    const port = getDaemonPort(args);
    const daemonPath = join(__dirname, 'daemon.mjs');

    const daemonArgs = ['--port', String(port)];
    if (args.browser) daemonArgs.push('--browser', args.browser);
    if (args.workspace) daemonArgs.push('--workspace', args.workspace);

    console.log(`Starting cc-browser daemon on port ${port}...`);
    const child = spawn(process.execPath, [daemonPath, ...daemonArgs], {
      stdio: 'inherit',
    });

    child.on('exit', (code) => {
      process.exit(code || 0);
    });
  },

  // Status
  status: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('GET', '/', null, port);
    output(result);
  },

  // List available browsers
  browsers: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('GET', '/browsers', null, port);
    output(result);
  },

  // List Chrome/Edge profiles
  profiles: async (args) => {
    const port = getDaemonPort(args);
    const browser = args.browser || 'chrome';
    const result = await request('GET', `/profiles?browser=${browser}`, null, port);
    output(result);
  },

  // List configured cc-browser workspaces
  workspaces: async (args) => {
    const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
    const ccBrowserDir = join(localAppData, 'cc-browser');

    if (!existsSync(ccBrowserDir)) {
      output({ success: true, workspaces: [] });
      return;
    }

    const workspaces = [];
    const dirs = readdirSync(ccBrowserDir);
    for (const dir of dirs) {
      const configPath = join(ccBrowserDir, dir, 'workspace.json');
      if (existsSync(configPath)) {
        try {
          const config = JSON.parse(readFileSync(configPath, 'utf8'));
          workspaces.push({
            directory: dir,
            name: config.name || dir,
            browser: config.browser || 'unknown',
            workspace: config.workspace || dir,
            daemonPort: config.daemonPort || null,
            cdpPort: config.cdpPort || null,
            aliases: config.aliases || [],
            purpose: config.purpose || '',
          });
        } catch {
          // Skip invalid configs
        }
      }
    }
    output({ success: true, workspaces });
  },

  // Get favorites from workspace.json
  favorites: async (args) => {
    const browser = args.browser || 'edge';
    const workspace = args.workspace;

    if (!workspace) {
      output({ success: false, error: 'Workspace name required. Use --workspace <name>' });
      return;
    }

    const workspaceDir = getWorkspaceDir(browser, workspace);
    const workspaceJsonPath = join(workspaceDir, 'workspace.json');

    if (!existsSync(workspaceJsonPath)) {
      output({ success: false, error: `Workspace not found: ${workspaceJsonPath}` });
      return;
    }

    try {
      const data = JSON.parse(readFileSync(workspaceJsonPath, 'utf8'));
      output({
        success: true,
        browser,
        workspace,
        favorites: data.favorites || [],
        name: data.name,
        purpose: data.purpose,
      });
    } catch (err) {
      output({ success: false, error: `Failed to read workspace: ${err.message}` });
    }
  },

  // Start browser
  start: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/start', {
      headless: args.headless,
      port: args.cdpPort,
      exe: args.exe,
      browser: args.browser,
      workspace: args.workspace,
      profileDir: args.profileDir,
      useSystemProfile: args.profileDir ? true : args.systemProfile,
      noIndicator: args['no-indicator'] || false,
      mode: args.mode,
    }, port);
    output(result);
  },

  // Stop browser
  stop: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/stop', {
      browser: args.browser,
      workspace: args.workspace,
    }, port);
    output(result);
  },

  // Navigate
  navigate: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/navigate', {
      url: args.url,
      tab: args.tab,
      waitUntil: args.waitUntil,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Reload
  reload: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/reload', {
      tab: args.tab,
      waitUntil: args.waitUntil,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Back
  back: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/back', {
      tab: args.tab,
    }, port);
    output(result);
  },

  // Forward
  forward: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/forward', {
      tab: args.tab,
    }, port);
    output(result);
  },

  // Snapshot
  snapshot: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/snapshot', {
      tab: args.tab,
      interactive: args.interactive,
      compact: args.compact,
      maxDepth: args.maxDepth,
      maxChars: args.maxChars,
    }, port);
    output(result);
  },

  // Info
  info: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/info', {
      tab: args.tab,
    }, port);
    output(result);
  },

  // Click
  click: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/click', {
      ref: args.ref,
      tab: args.tab,
      doubleClick: args.double || args.doubleClick,
      button: args.button,
      modifiers: args.modifiers,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Type
  type: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/type', {
      ref: args.ref,
      text: args.text,
      tab: args.tab,
      submit: args.submit,
      slowly: args.slowly,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Press
  press: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/press', {
      key: args.key,
      tab: args.tab,
      delay: args.delay,
    }, port);
    output(result);
  },

  // Hover
  hover: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/hover', {
      ref: args.ref,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Drag
  drag: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/drag', {
      startRef: args.from || args.startRef,
      endRef: args.to || args.endRef,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Select
  select: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/select', {
      ref: args.ref,
      values: args.values || args.value,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Scroll
  scroll: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/scroll', {
      direction: args.direction,
      amount: args.amount,
      ref: args.ref,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Wait
  wait: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/wait', {
      time: args.time,
      text: args.text,
      textGone: args.textGone,
      selector: args.selector,
      url: args.url,
      loadState: args.loadState,
      fn: args.fn,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Evaluate
  evaluate: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/evaluate', {
      fn: args.js || args.fn || args.code,
      ref: args.ref,
      tab: args.tab,
    }, port);
    output(result);
  },

  // Fill form
  fill: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/fill', {
      fields: args.fields,
      tab: args.tab,
      timeout: args.timeout,
    }, port);
    output(result);
  },

  // Screenshot
  screenshot: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/screenshot', {
      ref: args.ref,
      element: args.element,
      fullPage: args.fullPage,
      type: args.type,
      tab: args.tab,
    }, port);
    output(result);
  },

  // Screenshot with labels
  'screenshot-labels': async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/screenshot-labels', {
      maxLabels: args.maxLabels,
      type: args.type,
      tab: args.tab,
    }, port);
    output(result);
  },

  // Upload
  upload: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/upload', {
      ref: args.ref,
      element: args.element,
      paths: args.paths || args.path,
      tab: args.tab,
    }, port);
    output(result);
  },

  // Resize
  resize: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/resize', {
      width: args.width,
      height: args.height,
      tab: args.tab,
    }, port);
    output(result);
  },

  // List tabs
  tabs: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/tabs', {}, port);
    output(result);
  },

  // Open tab
  'tabs-open': async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/tabs/open', {
      url: args.url,
    }, port);
    output(result);
  },

  // Close tab
  'tabs-close': async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/tabs/close', {
      tab: args.tab,
    }, port);
    output(result);
  },

  // Focus tab
  'tabs-focus': async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/tabs/focus', {
      tab: args.tab,
    }, port);
    output(result);
  },

  // Text content
  text: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/text', {
      selector: args.selector,
      tab: args.tab,
    }, port);
    output(result);
  },

  // HTML
  html: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/html', {
      selector: args.selector,
      outer: args.outer,
      tab: args.tab,
    }, port);
    output(result);
  },

  // Mode - get or set
  mode: async (args) => {
    const port = getDaemonPort(args);
    const newMode = args._[1]; // e.g. "cc-browser mode human" -> args._[1] = "human"
    if (newMode) {
      const result = await request('POST', '/mode', { mode: newMode }, port);
      output(result);
    } else {
      const result = await request('GET', '/mode', null, port);
      output(result);
    }
  },

  // CAPTCHA detect
  'captcha': async (args) => {
    const port = getDaemonPort(args);
    const subcommand = args._[1]; // detect or solve
    if (subcommand === 'detect') {
      const result = await request('POST', '/captcha/detect', {
        tab: args.tab,
      }, port);
      output(result);
    } else if (subcommand === 'solve') {
      const result = await request('POST', '/captcha/solve', {
        tab: args.tab,
        attempts: args.attempts,
      }, port);
      output(result);
    } else {
      outputError('Usage: cc-browser captcha <detect|solve> [--attempts N]');
    }
  },
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);
  const command = args._[0] || 'help';

  const handler = commands[command];
  if (!handler) {
    outputError(`Unknown command: ${command}. Run 'cc-browser help' for usage.`);
  }

  try {
    await handler(args);
  } catch (err) {
    outputError(err.message);
  }
}

main();
