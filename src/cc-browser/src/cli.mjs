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

// Get profile directory path
function getProfileDir(browser, profile) {
  const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
  return join(localAppData, 'cc-browser', `${browser}-${profile}`);
}

// Read profile.json configuration
function readProfileConfig(browser, profile) {
  const profileDir = getProfileDir(browser, profile);
  const configPath = join(profileDir, 'profile.json');

  if (!existsSync(configPath)) {
    return null;
  }

  const content = readFileSync(configPath, 'utf8');
  return JSON.parse(content);
}

// Resolve alias to browser+profile
function resolveAlias(alias) {
  const localAppData = process.env.LOCALAPPDATA || join(process.env.HOME || '', 'AppData', 'Local');
  const ccBrowserDir = join(localAppData, 'cc-browser');

  if (!existsSync(ccBrowserDir)) return null;

  const dirs = readdirSync(ccBrowserDir);
  for (const dir of dirs) {
    const configPath = join(ccBrowserDir, dir, 'profile.json');
    if (existsSync(configPath)) {
      const config = JSON.parse(readFileSync(configPath, 'utf8'));
      if (config.aliases && config.aliases.includes(alias)) {
        const [browser, ...profileParts] = dir.split('-');
        const profile = profileParts.join('-');
        return { browser, profile, config };
      }
    }
  }
  return null;
}

// Get daemon port from profile.json, lockfile, or default
function getDaemonPort(args) {
  // If port is explicitly provided, use it
  if (args.port) {
    console.error(`[DEBUG] Using explicit port: ${args.port}`);
    return args.port;
  }

  // If browser and profile are specified, try to read from profile.json
  if (args.browser && args.profile) {
    console.error(`[DEBUG] Looking for ${args.browser}-${args.profile} config`);
    const config = readProfileConfig(args.browser, args.profile);
    if (config && config.daemonPort) {
      console.error(`[DEBUG] Found daemonPort: ${config.daemonPort}`);
      return config.daemonPort;
    }
    console.error(`[DEBUG] No config or daemonPort found`);
  } else if (args.profile && !args.browser) {
    // Profile specified without browser - try to resolve as alias
    console.error(`[DEBUG] Resolving alias: ${args.profile}`);
    const resolved = resolveAlias(args.profile);
    if (resolved) {
      console.error(`[DEBUG] Alias resolved: ${resolved.browser}-${resolved.profile}`);
      // Update args with resolved browser/profile for downstream use
      args.browser = resolved.browser;
      args.profile = resolved.profile;
      if (resolved.config.daemonPort) {
        console.error(`[DEBUG] Found daemonPort: ${resolved.config.daemonPort}`);
        return resolved.config.daemonPort;
      }
    }
    console.error(`[DEBUG] Alias not found: ${args.profile}`);
  } else {
    // No browser/profile specified - check lockfile for running daemon
    console.error(`[DEBUG] No browser/profile specified, checking lockfile...`);
    const lockData = readLockfile();
    if (lockData && lockData.port) {
      console.error(`[DEBUG] Found running daemon via lockfile: port=${lockData.port}, browser=${lockData.browser}, profile=${lockData.profile}`);
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
  cc-browser browsers                     List available browsers
  cc-browser profiles [--browser chrome]  List Chrome/Edge profiles (with emails)
  cc-browser favorites --profile work     Get favorites from profile.json
  cc-browser start                        Start with default isolated profile
  cc-browser start --browser edge         Start Edge (default profile)
  cc-browser start --browser edge --profile work  Start Edge with 'work' profile
  cc-browser start --browser chrome --profile personal  Start Chrome with 'personal' profile
  cc-browser start --profileDir "Profile 1"  Use existing system Chrome profile
  cc-browser stop                         Stop browser

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

ADVANCED:
  cc-browser wait --text "loaded"              Wait for text to appear
  cc-browser wait --time 1000                  Wait for time (ms)
  cc-browser evaluate --js "document.title"    Run JavaScript
  cc-browser fill --fields '[...]'             Fill multiple form fields
  cc-browser upload --ref <e1> --path <file>   Upload file

OPTIONS:
  --port <port>     Daemon port (default: 9280)
  --cdpPort <port>  Chrome CDP port (default: 9222)
  --browser <name>  Browser to use: chrome, edge, brave
  --profile <name>  Named profile for isolated sessions (persists logins)
  --tab <targetId>  Target specific tab
  --timeout <ms>    Action timeout

EXAMPLES:
  # Start daemon (run in background terminal)
  cc-browser daemon

  # List available browsers and profiles
  cc-browser browsers
  cc-browser profiles                    # List system Chrome profiles
  cc-browser profiles --browser edge     # List system Edge profiles

  # Named profiles (recommended - persistent logins, isolated sessions)
  cc-browser start --browser edge --profile work      # Edge for work
  cc-browser start --browser chrome --profile personal  # Chrome personal account
  cc-browser start --browser chrome --profile business  # Chrome business account

  # Simple start (default profile)
  cc-browser start --browser edge
  cc-browser start --browser chrome

  # Use existing system Chrome/Edge profile (requires all browser windows closed)
  cc-browser start --profileDir "Default"
  cc-browser start --profileDir "Profile 1"
  cc-browser start --browser edge --profileDir "Default"

  # Basic workflow
  cc-browser start --browser edge --profile work
  cc-browser navigate --url "https://example.com"
  cc-browser snapshot --interactive
  cc-browser click --ref e3
  cc-browser type --ref e4 --text "hello"
  cc-browser screenshot
  cc-browser stop

  # Profile data stored at: %LOCALAPPDATA%\\cc-browser\\<browser>-<profile>\\

MULTI-PROFILE (SIMULTANEOUS BROWSERS):
  Each profile has its own ports defined in profile.json:
  - edge-work: daemon=9280, cdp=9222
  - chrome-work: daemon=9281, cdp=9223
  - chrome-personal: daemon=9282, cdp=9224

  # Start daemons for each profile (in separate terminals):
  cc-browser daemon --browser edge --profile work         # Port 9280
  cc-browser daemon --browser chrome --profile work       # Port 9281
  cc-browser daemon --browser chrome --profile personal   # Port 9282

  # Commands auto-detect daemon port from profile.json:
  cc-browser start --browser edge --profile work
  cc-browser start --browser chrome --profile work
  cc-browser start --browser chrome --profile personal
`);
  },

  // Start daemon (foreground)
  daemon: async (args) => {
    const port = getDaemonPort(args);
    const daemonPath = join(__dirname, 'daemon.mjs');

    const daemonArgs = ['--port', String(port)];
    if (args.browser) daemonArgs.push('--browser', args.browser);
    if (args.profile) daemonArgs.push('--profile', args.profile);

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

  // Get favorites from profile.json
  favorites: async (args) => {
    const browser = args.browser || 'edge';
    const profile = args.profile;

    if (!profile) {
      output({ success: false, error: 'Profile name required. Use --profile <name>' });
      return;
    }

    const profileDir = getProfileDir(browser, profile);
    const profileJsonPath = join(profileDir, 'profile.json');

    if (!existsSync(profileJsonPath)) {
      output({ success: false, error: `Profile not found: ${profileJsonPath}` });
      return;
    }

    try {
      const data = JSON.parse(readFileSync(profileJsonPath, 'utf8'));
      output({
        success: true,
        browser,
        profile,
        favorites: data.favorites || [],
        name: data.name,
        purpose: data.purpose,
      });
    } catch (err) {
      output({ success: false, error: `Failed to read profile: ${err.message}` });
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
      profile: args.profile,
      profileDir: args.profileDir,
      useSystemProfile: args.profileDir ? true : args.systemProfile,
    }, port);
    output(result);
  },

  // Stop browser
  stop: async (args) => {
    const port = getDaemonPort(args);
    const result = await request('POST', '/stop', {
      browser: args.browser,
      profile: args.profile,
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
