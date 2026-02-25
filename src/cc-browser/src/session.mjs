// CC Browser - Session Management
// Adapted from: OpenClaw src/browser/pw-session.ts
// Manages Playwright browser connection, page state, and element refs

import { chromium } from 'playwright-core';

// ---------------------------------------------------------------------------
// Types (JSDoc for IDE support)
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} BrowserConsoleMessage
 * @property {string} type
 * @property {string} text
 * @property {string} timestamp
 * @property {{url?: string, lineNumber?: number, columnNumber?: number}} [location]
 */

/**
 * @typedef {Object} BrowserPageError
 * @property {string} message
 * @property {string} [name]
 * @property {string} [stack]
 * @property {string} timestamp
 */

/**
 * @typedef {Object} BrowserNetworkRequest
 * @property {string} id
 * @property {string} timestamp
 * @property {string} method
 * @property {string} url
 * @property {string} [resourceType]
 * @property {number} [status]
 * @property {boolean} [ok]
 * @property {string} [failureText]
 */

/**
 * @typedef {Object} RoleRef
 * @property {string} role
 * @property {string} [name]
 * @property {number} [nth]
 */

/**
 * @typedef {Object} PageState
 * @property {BrowserConsoleMessage[]} console
 * @property {BrowserPageError[]} errors
 * @property {BrowserNetworkRequest[]} requests
 * @property {WeakMap<object, string>} requestIds
 * @property {number} nextRequestId
 * @property {Record<string, RoleRef>} [roleRefs]
 * @property {'role'|'aria'} [roleRefsMode]
 * @property {string} [roleRefsFrameSelector]
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

/** @type {WeakMap<object, PageState>} */
const pageStates = new WeakMap();

/** @type {WeakSet<object>} */
const observedPages = new WeakSet();

/** @type {Map<string, {refs: Record<string, RoleRef>, frameSelector?: string, mode?: string}>} */
const roleRefsByTarget = new Map();
const MAX_ROLE_REFS_CACHE = 50;

const MAX_CONSOLE_MESSAGES = 500;
const MAX_PAGE_ERRORS = 200;
const MAX_NETWORK_REQUESTS = 500;

/** @type {{browser: object, cdpUrl: string} | null} */
let cached = null;

/** @type {Promise<{browser: object, cdpUrl: string}> | null} */
let connecting = null;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function normalizeCdpUrl(raw) {
  return raw.replace(/\/$/, '');
}

function roleRefsKey(cdpUrl, targetId) {
  return `${normalizeCdpUrl(cdpUrl)}::${targetId}`;
}

// ---------------------------------------------------------------------------
// Role Refs Management
// ---------------------------------------------------------------------------

export function rememberRoleRefsForTarget(opts) {
  const { cdpUrl, targetId, refs, frameSelector, mode } = opts;
  const tid = String(targetId || '').trim();
  if (!tid) return;

  roleRefsByTarget.set(roleRefsKey(cdpUrl, tid), {
    refs,
    ...(frameSelector ? { frameSelector } : {}),
    ...(mode ? { mode } : {}),
  });

  // LRU-like cleanup
  while (roleRefsByTarget.size > MAX_ROLE_REFS_CACHE) {
    const first = roleRefsByTarget.keys().next();
    if (first.done) break;
    roleRefsByTarget.delete(first.value);
  }
}

export function storeRoleRefsForTarget(opts) {
  const { page, cdpUrl, targetId, refs, frameSelector, mode } = opts;
  const state = ensurePageState(page);
  state.roleRefs = refs;
  state.roleRefsFrameSelector = frameSelector;
  state.roleRefsMode = mode;

  if (targetId?.trim()) {
    rememberRoleRefsForTarget({ cdpUrl, targetId, refs, frameSelector, mode });
  }
}

export function restoreRoleRefsForTarget(opts) {
  const { cdpUrl, targetId, page } = opts;
  const tid = String(targetId || '').trim();
  if (!tid) return;

  const cached = roleRefsByTarget.get(roleRefsKey(cdpUrl, tid));
  if (!cached) return;

  const state = ensurePageState(page);
  if (state.roleRefs) return; // Already have refs

  state.roleRefs = cached.refs;
  state.roleRefsFrameSelector = cached.frameSelector;
  state.roleRefsMode = cached.mode;
}

// ---------------------------------------------------------------------------
// Page State Management
// ---------------------------------------------------------------------------

export function ensurePageState(page) {
  const existing = pageStates.get(page);
  if (existing) return existing;

  /** @type {PageState} */
  const state = {
    console: [],
    errors: [],
    requests: [],
    requestIds: new WeakMap(),
    nextRequestId: 0,
  };
  pageStates.set(page, state);

  if (!observedPages.has(page)) {
    observedPages.add(page);

    page.on('console', (msg) => {
      state.console.push({
        type: msg.type(),
        text: msg.text(),
        timestamp: new Date().toISOString(),
        location: msg.location(),
      });
      if (state.console.length > MAX_CONSOLE_MESSAGES) {
        state.console.shift();
      }
    });

    page.on('pageerror', (err) => {
      state.errors.push({
        message: err?.message ? String(err.message) : String(err),
        name: err?.name ? String(err.name) : undefined,
        stack: err?.stack ? String(err.stack) : undefined,
        timestamp: new Date().toISOString(),
      });
      if (state.errors.length > MAX_PAGE_ERRORS) {
        state.errors.shift();
      }
    });

    page.on('request', (req) => {
      state.nextRequestId += 1;
      const id = `r${state.nextRequestId}`;
      state.requestIds.set(req, id);
      state.requests.push({
        id,
        timestamp: new Date().toISOString(),
        method: req.method(),
        url: req.url(),
        resourceType: req.resourceType(),
      });
      if (state.requests.length > MAX_NETWORK_REQUESTS) {
        state.requests.shift();
      }
    });

    page.on('response', (resp) => {
      const req = resp.request();
      const id = state.requestIds.get(req);
      if (!id) return;
      const rec = state.requests.findLast(r => r.id === id);
      if (rec) {
        rec.status = resp.status();
        rec.ok = resp.ok();
      }
    });

    page.on('requestfailed', (req) => {
      const id = state.requestIds.get(req);
      if (!id) return;
      const rec = state.requests.findLast(r => r.id === id);
      if (rec) {
        rec.failureText = req.failure()?.errorText;
        rec.ok = false;
      }
    });

    page.on('close', () => {
      pageStates.delete(page);
      observedPages.delete(page);
    });
  }

  return state;
}

export function getPageState(page) {
  return pageStates.get(page);
}

// ---------------------------------------------------------------------------
// Browser Connection
// ---------------------------------------------------------------------------

async function fetchWithTimeout(url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal });
    return res;
  } finally {
    clearTimeout(timer);
  }
}

async function getChromeWebSocketUrl(cdpUrl, timeoutMs = 5000) {
  try {
    const res = await fetchWithTimeout(`${cdpUrl}/json/version`, timeoutMs);
    if (!res.ok) return null;
    const info = await res.json();
    return info.webSocketDebuggerUrl || null;
  } catch {
    return null;
  }
}

export async function connectBrowser(cdpUrl) {
  const normalized = normalizeCdpUrl(cdpUrl);

  if (cached?.cdpUrl === normalized) {
    return cached;
  }

  if (connecting) {
    return await connecting;
  }

  const connectWithRetry = async () => {
    let lastErr;
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const timeout = 5000 + attempt * 2000;
        const wsUrl = await getChromeWebSocketUrl(normalized, timeout);
        const endpoint = wsUrl || normalized;
        const browser = await chromium.connectOverCDP(endpoint, { timeout });

        const connected = { browser, cdpUrl: normalized };
        cached = connected;

        // Observe all pages
        for (const context of browser.contexts()) {
          for (const page of context.pages()) {
            ensurePageState(page);
          }
          context.on('page', (page) => ensurePageState(page));
        }

        browser.on('disconnected', () => {
          if (cached?.browser === browser) {
            cached = null;
          }
        });

        return connected;
      } catch (err) {
        lastErr = err;
        const delay = 250 + attempt * 250;
        await new Promise((r) => setTimeout(r, delay));
      }
    }
    throw lastErr || new Error('CDP connect failed');
  };

  connecting = connectWithRetry().finally(() => {
    connecting = null;
  });

  return await connecting;
}

export async function disconnectBrowser() {
  const cur = cached;
  cached = null;
  if (cur?.browser) {
    await cur.browser.close().catch(() => {});
  }
}

export function getCachedBrowser() {
  return cached;
}

// ---------------------------------------------------------------------------
// Page Resolution
// ---------------------------------------------------------------------------

async function getAllPages(browser) {
  const contexts = browser.contexts();
  return contexts.flatMap((c) => c.pages());
}

async function pageTargetId(page) {
  const session = await page.context().newCDPSession(page);
  try {
    const info = await session.send('Target.getTargetInfo');
    return String(info?.targetInfo?.targetId || '').trim() || null;
  } finally {
    await session.detach().catch(() => {});
  }
}

async function findPageByTargetId(browser, targetId, cdpUrl) {
  const pages = await getAllPages(browser);

  // Try CDP session approach
  for (const page of pages) {
    const tid = await pageTargetId(page).catch(() => null);
    if (tid && tid === targetId) {
      return page;
    }
  }

  // Fallback: URL-based matching using /json/list
  if (cdpUrl) {
    try {
      const baseUrl = cdpUrl.replace(/\/+$/, '').replace(/^ws:/, 'http:').replace(/\/cdp$/, '');
      const res = await fetchWithTimeout(`${baseUrl}/json/list`, 3000);
      if (res.ok) {
        const targets = await res.json();
        const target = targets.find((t) => t.id === targetId);
        if (target) {
          const urlMatch = pages.filter((p) => p.url() === target.url);
          if (urlMatch.length === 1) return urlMatch[0];
          if (urlMatch.length > 1) {
            const sameUrlTargets = targets.filter((t) => t.url === target.url);
            if (sameUrlTargets.length === urlMatch.length) {
              const idx = sameUrlTargets.findIndex((t) => t.id === targetId);
              if (idx >= 0 && idx < urlMatch.length) return urlMatch[idx];
            }
          }
        }
      }
    } catch {
      // Ignore
    }
  }

  return null;
}

export async function getPageForTargetId(opts) {
  const { cdpUrl, targetId } = opts;
  const { browser } = await connectBrowser(cdpUrl);
  const pages = await getAllPages(browser);

  if (!pages.length) {
    throw new Error('No pages available in the connected browser.');
  }

  if (!targetId) {
    return pages[0];
  }

  const found = await findPageByTargetId(browser, targetId, cdpUrl);
  if (!found) {
    if (pages.length === 1) return pages[0];
    throw new Error('Tab not found');
  }
  return found;
}

// ---------------------------------------------------------------------------
// Ref Locator
// ---------------------------------------------------------------------------

export function refLocator(page, ref) {
  const normalized = ref.startsWith('@')
    ? ref.slice(1)
    : ref.startsWith('ref=')
      ? ref.slice(4)
      : ref;

  if (/^e\d+$/i.test(normalized)) {
    const state = pageStates.get(page);
    if (state?.roleRefsMode === 'aria') {
      const scope = state.roleRefsFrameSelector
        ? page.frameLocator(state.roleRefsFrameSelector)
        : page;
      return scope.locator(`aria-ref=${normalized}`);
    }

    const info = state?.roleRefs?.[normalized.toLowerCase()];
    if (!info) {
      throw new Error(
        `Unknown ref "${normalized}". Run a new snapshot to get current element refs.`
      );
    }

    const scope = state?.roleRefsFrameSelector
      ? page.frameLocator(state.roleRefsFrameSelector)
      : page;

    const locator = info.name
      ? scope.getByRole(info.role, { name: info.name, exact: true })
      : scope.getByRole(info.role);

    return info.nth !== undefined ? locator.nth(info.nth) : locator;
  }

  // Fallback: aria-ref
  return page.locator(`aria-ref=${normalized}`);
}

// ---------------------------------------------------------------------------
// Tab Operations via Playwright
// ---------------------------------------------------------------------------

export async function listPagesViaPlaywright(opts) {
  const { cdpUrl } = opts;
  const { browser } = await connectBrowser(cdpUrl);
  const pages = await getAllPages(browser);
  const results = [];

  for (const page of pages) {
    const tid = await pageTargetId(page).catch(() => null);
    if (tid) {
      results.push({
        targetId: tid,
        title: await page.title().catch(() => ''),
        url: page.url(),
        type: 'page',
      });
    }
  }
  return results;
}

export async function createPageViaPlaywright(opts) {
  const { cdpUrl, url } = opts;
  const { browser } = await connectBrowser(cdpUrl);
  const context = browser.contexts()[0] || (await browser.newContext());
  const page = await context.newPage();
  ensurePageState(page);

  const targetUrl = (url || '').trim() || 'about:blank';
  if (targetUrl !== 'about:blank') {
    await page.goto(targetUrl, { timeout: 30000 }).catch(() => {});
  }

  const tid = await pageTargetId(page).catch(() => null);
  if (!tid) {
    throw new Error('Failed to get targetId for new page');
  }

  return {
    targetId: tid,
    title: await page.title().catch(() => ''),
    url: page.url(),
    type: 'page',
  };
}

export async function closePageByTargetIdViaPlaywright(opts) {
  const { cdpUrl, targetId } = opts;
  const { browser } = await connectBrowser(cdpUrl);
  const page = await findPageByTargetId(browser, targetId, cdpUrl);
  if (!page) {
    throw new Error('Tab not found');
  }
  await page.close();
}

export async function focusPageByTargetIdViaPlaywright(opts) {
  const { cdpUrl, targetId } = opts;
  const { browser } = await connectBrowser(cdpUrl);
  const page = await findPageByTargetId(browser, targetId, cdpUrl);
  if (!page) {
    throw new Error('Tab not found');
  }
  await page.bringToFront();
}
