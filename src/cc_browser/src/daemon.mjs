#!/usr/bin/env node
// CC Browser - HTTP Daemon Server
// Fast browser automation for Claude Code
// Usage: node daemon.mjs [--port 9280]

import { createServer } from 'http';
import { parse as parseUrl } from 'url';
import { existsSync, readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

import { ensureChromeAvailable, checkChromeRunning, stopChrome, launchChrome, listAvailableBrowsers, listChromeProfiles } from './chrome.mjs';

// ---------------------------------------------------------------------------
// Profile Configuration Reader
// ---------------------------------------------------------------------------

function getProfileDir(browser, profile) {
  const localAppData = process.env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local');
  return join(localAppData, 'cc-browser', `${browser}-${profile}`);
}

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
  const localAppData = process.env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local');
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
import { connectBrowser, disconnectBrowser, getCachedBrowser, getPageState } from './session.mjs';
import {
  listPagesViaPlaywright,
  createPageViaPlaywright,
  closePageByTargetIdViaPlaywright,
  focusPageByTargetIdViaPlaywright,
} from './session.mjs';
import {
  clickViaPlaywright,
  hoverViaPlaywright,
  dragViaPlaywright,
  selectOptionViaPlaywright,
  pressKeyViaPlaywright,
  typeViaPlaywright,
  fillFormViaPlaywright,
  evaluateViaPlaywright,
  scrollViaPlaywright,
  scrollIntoViewViaPlaywright,
  waitForViaPlaywright,
  takeScreenshotViaPlaywright,
  setInputFilesViaPlaywright,
  resizeViaPlaywright,
  navigateViaPlaywright,
  reloadViaPlaywright,
  goBackViaPlaywright,
  goForwardViaPlaywright,
} from './interactions.mjs';
import {
  snapshotViaPlaywright,
  getPageInfoViaPlaywright,
  getTextContentViaPlaywright,
  getHtmlViaPlaywright,
  screenshotWithLabelsViaPlaywright,
} from './snapshot.mjs';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const DEFAULT_DAEMON_PORT = 9280;
const DEFAULT_CDP_PORT = 9222;

// Track the actual port this daemon is listening on
let actualDaemonPort = DEFAULT_DAEMON_PORT;

// Track the default profile for this daemon (set via CLI args)
let defaultDaemonBrowser = null;
let defaultDaemonProfile = null;
let defaultDaemonCdpPort = null;

// Track the active browser session
let activeCdpPort = null;
let activeBrowserKind = null;
let activeProfile = null;

function getActiveCdpPort() {
  // Active session takes priority
  if (activeCdpPort) return activeCdpPort;
  // Then use daemon's default profile CDP port
  if (defaultDaemonCdpPort) return defaultDaemonCdpPort;
  // Finally fall back to default
  return DEFAULT_CDP_PORT;
}

function setActiveSession(cdpPort, browserKind, profile) {
  activeCdpPort = cdpPort;
  activeBrowserKind = browserKind;
  activeProfile = profile;
  console.log(`[cc-browser] Active session: ${browserKind}-${profile} on port ${cdpPort}`);
}

function clearActiveSession() {
  console.log(`[cc-browser] Session cleared (was: ${activeBrowserKind}-${activeProfile} on port ${activeCdpPort})`);
  activeCdpPort = null;
  activeBrowserKind = null;
  activeProfile = null;
}

function validateSession(body) {
  // If no active session, return error
  if (!activeCdpPort) {
    return { valid: false, error: 'No browser session active. Run "start" first.' };
  }

  // If browser/profile specified, validate they match
  if (body.browser && body.browser !== activeBrowserKind) {
    return {
      valid: false,
      error: `Browser mismatch: requested "${body.browser}" but active session is "${activeBrowserKind}". Stop current session first.`,
    };
  }
  if (body.profile && body.profile !== activeProfile) {
    return {
      valid: false,
      error: `Profile mismatch: requested "${body.profile}" but active session is "${activeProfile}". Stop current session first.`,
    };
  }

  return { valid: true };
}

// ---------------------------------------------------------------------------
// JSON Response Helpers
// ---------------------------------------------------------------------------

function jsonResponse(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function jsonError(res, statusCode, message) {
  jsonResponse(res, statusCode, { success: false, error: message });
}

function jsonSuccess(res, data = {}) {
  jsonResponse(res, 200, { success: true, ...data });
}

// ---------------------------------------------------------------------------
// Request Body Parser
// ---------------------------------------------------------------------------

async function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1024 * 1024) {
        reject(new Error('Request body too large'));
      }
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        const preview = body.length > 100 ? body.slice(0, 100) + '...' : body;
        reject(new Error(`Invalid JSON: ${err.message} (body: ${preview})`));
      }
    });
    req.on('error', reject);
  });
}

// ---------------------------------------------------------------------------
// Route Handlers
// ---------------------------------------------------------------------------

const routes = {
  // List available browsers
  'GET /browsers': async (req, res, params) => {
    const browsers = listAvailableBrowsers();
    jsonSuccess(res, { browsers });
  },

  // List Chrome profiles
  'GET /profiles': async (req, res, params, body, query) => {
    const browserKind = query?.browser || 'chrome';
    const profiles = listChromeProfiles(browserKind);
    jsonSuccess(res, { browser: browserKind, profiles });
  },

  // Status
  'GET /': async (req, res, params) => {
    const cdpPort = getActiveCdpPort();
    const status = await checkChromeRunning(cdpPort);
    const cached = getCachedBrowser();

    jsonSuccess(res, {
      daemon: 'running',
      daemonPort: params.daemonPort,
      browser: status.running ? 'connected' : 'not running',
      cdpUrl: status.cdpUrl,
      cdpPort,
      browserKind: activeBrowserKind,
      profile: activeProfile,
      tabs: status.tabs || [],
      activeTab: status.activeTab,
      playwrightConnected: !!cached,
    });
  },

  // Start browser
  'POST /start': async (req, res, params, body) => {
    const profileName = body.profile || defaultDaemonProfile || 'default';
    const browserKind = body.browser || defaultDaemonBrowser || 'chrome';

    // Read profile.json to get cdpPort - priority: explicit body.port > profile.json > default
    let cdpPort = body.port; // Only use if explicitly provided
    if (!cdpPort) {
      const profileConfig = readProfileConfig(browserKind, profileName);
      if (profileConfig && profileConfig.cdpPort) {
        cdpPort = profileConfig.cdpPort;
      }
    }
    if (!cdpPort) {
      cdpPort = DEFAULT_CDP_PORT;
    }

    const result = await ensureChromeAvailable({
      port: cdpPort,
      headless: body.headless,
      executablePath: body.exe,
      browser: body.browser,
      profileName: profileName,
      useSystemProfile: body.systemProfile || body.useSystemProfile,
      profileDir: body.profileDir,
    });

    // Connect Playwright
    await connectBrowser(result.cdpUrl);

    // Track this as the active session
    setActiveSession(cdpPort, result.browserKind, profileName);

    jsonSuccess(res, {
      started: result.started,
      cdpUrl: result.cdpUrl,
      cdpPort,
      browserKind: result.browserKind,
      profile: profileName,
      tabs: result.tabs,
      activeTab: result.activeTab,
    });
  },

  // Stop browser
  'POST /stop': async (req, res, params) => {
    const cdpPort = activeCdpPort || params.cdpPort || DEFAULT_CDP_PORT;
    await disconnectBrowser();
    const result = await stopChrome(cdpPort);
    clearActiveSession();
    jsonSuccess(res, result);
  },

  // Navigate
  'POST /navigate': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) {
      return jsonError(res, 400, validation.error);
    }
    const cdpPort = getActiveCdpPort();
    const cdpUrl = `http://127.0.0.1:${cdpPort}`;
    const result = await navigateViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      url: body.url,
      waitUntil: body.waitUntil,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, result);
  },

  // Reload
  'POST /reload': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await reloadViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      waitUntil: body.waitUntil,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, result);
  },

  // Go back
  'POST /back': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await goBackViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      waitUntil: body.waitUntil,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, result);
  },

  // Go forward
  'POST /forward': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await goForwardViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      waitUntil: body.waitUntil,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, result);
  },

  // Snapshot
  'POST /snapshot': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await snapshotViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      interactive: body.interactive,
      compact: body.compact,
      maxDepth: body.maxDepth,
      maxChars: body.maxChars,
    });
    jsonSuccess(res, result);
  },

  // Page info
  'POST /info': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await getPageInfoViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
    });
    jsonSuccess(res, result);
  },

  // Click
  'POST /click': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await clickViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      ref: body.ref,
      doubleClick: body.doubleClick || body.double,
      button: body.button,
      modifiers: body.modifiers,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { clicked: body.ref });
  },

  // Type
  'POST /type': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await typeViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      ref: body.ref,
      text: body.text,
      submit: body.submit,
      slowly: body.slowly,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { typed: body.text, ref: body.ref });
  },

  // Press key
  'POST /press': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await pressKeyViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      key: body.key,
      delayMs: body.delay,
    });
    jsonSuccess(res, { pressed: body.key });
  },

  // Hover
  'POST /hover': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await hoverViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      ref: body.ref,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { hovered: body.ref });
  },

  // Drag
  'POST /drag': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await dragViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      startRef: body.startRef || body.from,
      endRef: body.endRef || body.to,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { dragged: `${body.startRef || body.from} -> ${body.endRef || body.to}` });
  },

  // Select
  'POST /select': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await selectOptionViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      ref: body.ref,
      values: Array.isArray(body.values) ? body.values : [body.value || body.values],
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { selected: body.values || body.value, ref: body.ref });
  },

  // Fill form
  'POST /fill': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await fillFormViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      fields: body.fields,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { filled: body.fields?.length || 0 });
  },

  // Scroll
  'POST /scroll': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await scrollViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      direction: body.direction,
      amount: body.amount,
      ref: body.ref,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { scrolled: body.ref || body.direction || 'down' });
  },

  // Wait
  'POST /wait': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await waitForViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      timeMs: body.time,
      text: body.text,
      textGone: body.textGone,
      selector: body.selector,
      url: body.url,
      loadState: body.loadState,
      fn: body.fn,
      timeoutMs: body.timeout,
    });
    jsonSuccess(res, { waited: true });
  },

  // Evaluate JavaScript
  'POST /evaluate': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await evaluateViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      fn: body.fn || body.js || body.code,
      ref: body.ref,
    });
    jsonSuccess(res, { result });
  },

  // Screenshot
  'POST /screenshot': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const { buffer } = await takeScreenshotViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      ref: body.ref,
      element: body.element,
      fullPage: body.fullPage,
      type: body.type || 'png',
    });

    // Return as base64
    jsonSuccess(res, {
      screenshot: buffer.toString('base64'),
      type: body.type || 'png',
    });
  },

  // Screenshot with labels
  'POST /screenshot-labels': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const { buffer, labels, skipped } = await screenshotWithLabelsViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      maxLabels: body.maxLabels,
      type: body.type || 'png',
    });

    jsonSuccess(res, {
      screenshot: buffer.toString('base64'),
      type: body.type || 'png',
      labels,
      skipped,
    });
  },

  // Upload file
  'POST /upload': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await setInputFilesViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      inputRef: body.ref,
      element: body.element,
      paths: Array.isArray(body.paths) ? body.paths : [body.path || body.paths],
    });
    jsonSuccess(res, { uploaded: body.paths || body.path });
  },

  // Resize viewport
  'POST /resize': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const result = await resizeViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      width: body.width,
      height: body.height,
    });
    jsonSuccess(res, result);
  },

  // List tabs
  'POST /tabs': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const tabs = await listPagesViaPlaywright({ cdpUrl });
    jsonSuccess(res, { tabs });
  },

  // Open new tab
  'POST /tabs/open': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const tab = await createPageViaPlaywright({ cdpUrl, url: body.url });
    jsonSuccess(res, { tab });
  },

  // Close tab
  'POST /tabs/close': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await closePageByTargetIdViaPlaywright({ cdpUrl, targetId: body.tab || body.targetId });
    jsonSuccess(res, { closed: body.tab || body.targetId });
  },

  // Focus tab
  'POST /tabs/focus': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    await focusPageByTargetIdViaPlaywright({ cdpUrl, targetId: body.tab || body.targetId });
    jsonSuccess(res, { focused: body.tab || body.targetId });
  },

  // Get text content
  'POST /text': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const text = await getTextContentViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      selector: body.selector,
    });
    jsonSuccess(res, { text });
  },

  // Get HTML
  'POST /html': async (req, res, params, body) => {
    const validation = validateSession(body);
    if (!validation.valid) return jsonError(res, 400, validation.error);
    const cdpUrl = `http://127.0.0.1:${getActiveCdpPort()}`;
    const html = await getHtmlViaPlaywright({
      cdpUrl,
      targetId: body.tab || body.targetId,
      selector: body.selector,
      outer: body.outer,
    });
    jsonSuccess(res, { html });
  },
};

// ---------------------------------------------------------------------------
// HTTP Server
// ---------------------------------------------------------------------------

async function handleRequest(req, res) {
  const { pathname, query } = parseUrl(req.url, true);
  const method = req.method.toUpperCase();
  const routeKey = `${method} ${pathname}`;

  // Parse query params - use active session port as default
  const params = {
    cdpPort: query.cdpPort ? parseInt(query.cdpPort, 10) : getActiveCdpPort(),
    daemonPort: query.daemonPort ? parseInt(query.daemonPort, 10) : actualDaemonPort,
  };

  // Find route handler
  const handler = routes[routeKey];
  if (!handler) {
    return jsonError(res, 404, `Unknown route: ${routeKey}`);
  }

  try {
    const body = method === 'GET' ? {} : await parseBody(req);
    await handler(req, res, params, body, query);
  } catch (err) {
    console.error(`[ERROR] ${routeKey}:`, err.message);
    jsonError(res, 500, err.message);
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
let daemonPort = DEFAULT_DAEMON_PORT;
let defaultBrowser = null;
let defaultProfile = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--port' && args[i + 1]) {
    daemonPort = parseInt(args[i + 1], 10);
  } else if (args[i] === '--browser' && args[i + 1]) {
    defaultBrowser = args[i + 1];
    i++;
  } else if (args[i] === '--profile' && args[i + 1]) {
    defaultProfile = args[i + 1];
    i++;
  }
}

// If profile is specified without browser, try to resolve as alias
if (defaultProfile && !defaultBrowser) {
  const resolved = resolveAlias(defaultProfile);
  if (resolved) {
    console.log(`[cc-browser] Alias "${defaultProfile}" resolved to ${resolved.browser}-${resolved.profile}`);
    defaultBrowser = resolved.browser;
    defaultProfile = resolved.profile;
  }
}

// If browser and profile are set, try to read ports from profile.json
if (defaultBrowser && defaultProfile) {
  const config = readProfileConfig(defaultBrowser, defaultProfile);
  if (config) {
    // Only use config daemonPort if not explicitly set via --port
    if (!args.includes('--port') && config.daemonPort) {
      daemonPort = config.daemonPort;
    }
    // Store default CDP port for this daemon
    if (config.cdpPort) {
      defaultDaemonCdpPort = config.cdpPort;
    }
  }
  // Store daemon's default browser/profile
  defaultDaemonBrowser = defaultBrowser;
  defaultDaemonProfile = defaultProfile;
}

const server = createServer(handleRequest);

// Store actual port for status responses
actualDaemonPort = daemonPort;

server.listen(daemonPort, '127.0.0.1', () => {
  console.log(`[cc-browser] Daemon listening on http://127.0.0.1:${daemonPort}`);
  if (defaultBrowser && defaultProfile) {
    const config = readProfileConfig(defaultBrowser, defaultProfile);
    const cdpPort = config?.cdpPort || DEFAULT_CDP_PORT;
    console.log(`[cc-browser] Profile: ${defaultBrowser}-${defaultProfile} (CDP: ${cdpPort})`);
  } else {
    console.log(`[cc-browser] CDP port: ${DEFAULT_CDP_PORT}`);
  }
  console.log('[cc-browser] Ready for commands');
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n[cc-browser] Shutting down...');
  await disconnectBrowser();
  server.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n[cc-browser] Shutting down...');
  await disconnectBrowser();
  server.close();
  process.exit(0);
});
