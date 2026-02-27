# cc-browser: Human Mode + CAPTCHA Solving

## Context

cc-browser currently operates at machine speed -- instant clicks, instant navigation, no delays. This makes it trivially detectable by anti-bot systems. When CAPTCHAs appear, there's no way to detect or solve them. Two problems to solve: (1) prevent bot detection with human-like behavior, (2) detect and solve CAPTCHAs automatically using LLM vision.

The user's priorities: **testing first** (reliable CAPTCHA sources, comprehensive type coverage), sliders in Phase 2 (not deferred), and covering all major CAPTCHA types.

## Architecture

Current: `CLI (cli.mjs) --HTTP--> Daemon (daemon.mjs) --Playwright--> Chrome`

Key facts:
- All interaction functions are in `interactions.mjs` (~550 lines, 15 exported functions)
- No human-like delays exist today (only `slowly` typing at fixed 75ms)
- Screenshot infrastructure already works (returns Buffer)
- `navigator.webdriver` already masked in `session.mjs`
- Zero npm dependencies beyond `playwright-core`
- No test infrastructure exists for cc-browser

---

## Phase 0: Test Harness (Build First)

### 0A. Local CAPTCHA test pages

Create `src/cc-browser/test/fixtures/captcha-pages/` with static HTML pages using official test keys that reliably trigger CAPTCHAs:

| Page | CAPTCHA Type | Test Key / Approach |
|------|-------------|-------------------|
| `recaptcha-v2.html` | reCAPTCHA v2 checkbox | Sitekey: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI` (always shows, always passes) |
| `hcaptcha.html` | hCaptcha checkbox | Sitekey: `10000000-ffff-ffff-ffff-000000000001` (always passes) |
| `turnstile.html` | Cloudflare Turnstile | Sitekey: `2x00000000000000000000AB` (always challenges) |
| `slider.html` | Slider/drag puzzle | Custom canvas-based slider (pure HTML/CSS/JS, no external deps) |
| `image-grid.html` | Simulated 3x3 grid | Static images with known correct answers for validation |
| `text-captcha.html` | Distorted text | Canvas-rendered distorted text with known answer |
| `no-captcha.html` | None | Normal page for false-positive testing |
| `cloudflare-wait.html` | CF interstitial | Simulated "Just a moment..." page |

Create `test/fixtures/captcha-pages/test-server.mjs` -- minimal HTTP server on port 9999 serving these pages.

### 0B. External CAPTCHA URL registry

Create `test/fixtures/captcha-urls.json` with live demo URLs for opt-in integration testing:

- reCAPTCHA v2: `https://www.google.com/recaptcha/api2/demo`
- hCaptcha: `https://accounts.hcaptcha.com/demo`
- Turnstile: `https://seleniumbase.io/apps/turnstile`
- GeeTest slider: `https://www.geetest.com/en/adaptive-captcha-demo`
- Multi-type: `https://2captcha.com/demo`

### 0C. Test framework setup

Use Node.js built-in `node:test` (zero dependencies). Add to `package.json`:

```json
"scripts": {
  "test": "node --test test/**/*.test.mjs",
  "test:unit": "node --test test/unit/**/*.test.mjs",
  "test:captcha": "node --test test/captcha/**/*.test.mjs"
}
```

Create `test/mocks.mjs` -- mock Playwright page objects that record method calls with timestamps (for verifying delay injection without a real browser).

### 0D. Screenshot fixtures

Capture and save static screenshots of each CAPTCHA type in `test/fixtures/screenshots/`. These allow unit-testing detection logic without making LLM calls or launching a browser.

---

## Phase 1: Human Mode

### 1A. Delay engine -- NEW file: `src/human-mode.mjs`

Pure utility module, fully unit-testable:

- `sleep(ms)` -- promise-based delay
- `randomInt(min, max)`, `gaussianRandom(mean, stddev)` -- randomization
- `navigationDelay()` -> 800-2500ms
- `preClickDelay()` -> 100-400ms
- `preTypeDelay()` -> 200-600ms
- `interKeyDelay()` -> gaussian(100, 40)ms
- `preScrollDelay()` -> 500-1500ms
- `postLoadDelay()` -> 1000-3000ms
- `idleDelay()` -> 1000-4000ms
- `humanMousePath(startX, startY, endX, endY)` -> array of {x,y} along a Bezier curve
- `clickOffset(maxPx)` -> small random offset from element center
- `typingDelays(text)` -> per-character delay array with natural variation

### 1B. Mode state -- MODIFY: `src/session.mjs`

Add module-level mode tracking:

```javascript
let currentMode = 'human';
export function getCurrentMode() { return currentMode; }
export function setCurrentMode(mode) { /* validate: fast|human|stealth */ }
```

### 1C. Inject delays -- MODIFY: `src/interactions.mjs`

Wrap each exported function with mode-aware delays. Pattern:

```javascript
const mode = getCurrentMode();
if (mode !== 'fast') {
  // Pre-action delay
  // Curved mouse movement to target (for click/hover/drag)
  // Random click offset
}
// ... existing Playwright call unchanged ...
```

Functions to modify: `navigateViaPlaywright`, `clickViaPlaywright`, `hoverViaPlaywright`, `dragViaPlaywright`, `typeViaPlaywright`, `pressKeyViaPlaywright`, `scrollViaPlaywright`, `fillFormViaPlaywright`

The `dragViaPlaywright` enhancement is critical -- it needs human-like mouse-down, curved path with y-wobble, overshoot-correct, mouse-up. This is reused by the slider CAPTCHA solver.

### 1D. Mode routes -- MODIFY: `src/daemon.mjs`

- `GET /mode` -- return current mode
- `POST /mode` -- set mode (`{mode: "human"}`)
- Modify `POST /start` to accept `mode` from request body or workspace.json
- Include mode in `GET /` status response

### 1E. Mode CLI -- MODIFY: `src/cli.mjs`

- `cc-browser mode` -- show current mode
- `cc-browser mode human|fast|stealth` -- switch mode
- `cc-browser start --workspace x --mode human` -- start with mode

### 1F. Workspace config -- extend workspace.json schema

Add optional `"mode": "human"` field (defaults to `human` if absent).

### Phase 1 tests

- `test/unit/human-delays.test.mjs` -- verify all delay functions return values in expected ranges, mouse paths have correct endpoints and aren't straight lines, typing delays vary per character
- `test/integration/human-mode.test.mjs` -- start daemon, navigate + click + type, measure that total time exceeds minimum human delays. Switch to fast mode, verify same actions are near-instant.

---

## Phase 2: CAPTCHA Detection + Solving (All Types Including Sliders)

### 2A. LLM vision -- NEW file: `src/vision.mjs`

Direct `fetch()` to Anthropic API (no SDK dependency needed):

```javascript
export async function analyzeScreenshot(base64, prompt, { model, maxTokens }) {
  // Uses ANTHROPIC_API_KEY env var
  // POST to https://api.anthropic.com/v1/messages with image content
  // Returns text response
}
```

Model selection: Haiku for detection (fast, ~$0.001/call), Sonnet for solving (accurate, ~$0.01/call).

### 2B. CAPTCHA detection -- NEW file: `src/captcha.mjs`

Two-tier detection:

1. **Quick DOM check** (free, no LLM): `page.evaluate()` looking for `.g-recaptcha`, `iframe[src*="recaptcha"]`, `.h-captcha`, `.cf-turnstile`, title containing "Just a moment"
2. **LLM vision check**: Screenshot -> Haiku with structured prompt -> JSON response with `{detected, type, description}`

Supported types: `recaptcha_v2_checkbox`, `recaptcha_v2_image`, `hcaptcha_checkbox`, `hcaptcha_image`, `cloudflare_turnstile`, `cloudflare_interstitial`, `slider`, `geetest`, `text_captcha`, `none`

### 2C. CAPTCHA solvers (in `src/captcha.mjs`)

Each solver is a separate async function:

**reCAPTCHA v2 checkbox** -- Find iframe, click checkbox with human delay. If image challenge appears, escalate to image grid solver.

**Image grid** (reCAPTCHA + hCaptcha) -- Screenshot challenge -> Sonnet with structured prompt asking for grid positions -> click identified cells with delays -> click verify. Handle multi-round challenges (images refresh).

**Slider/drag puzzle** -- Screenshot -> Sonnet estimates slider handle position and target x-coordinate -> execute drag using the human-mode `dragViaPlaywright` with Bezier path, y-wobble, overshoot-correct. If first attempt fails, screenshot again, ask LLM "how many pixels off?", adjust, retry.

**Text CAPTCHA** -- Screenshot -> Sonnet reads distorted text -> type into input field with human-like typing.

**Cloudflare Turnstile** -- Usually auto-resolves with webdriver masking (already in place). Wait 3-5s, check for checkbox, click if visible.

**Orchestrator**: `solveCaptcha(page, maxAttempts=3)` -- detect type, dispatch to solver, retry on failure with backoff.

### 2D. CAPTCHA routes -- MODIFY: `src/daemon.mjs`

- `POST /captcha/detect` -- run detection, return `{detected, type, description}`
- `POST /captcha/solve` -- detect + solve, return `{solved, message, attempts}`

### 2E. CAPTCHA CLI -- MODIFY: `src/cli.mjs`

- `cc-browser captcha detect` -- detect CAPTCHA on current page
- `cc-browser captcha solve` -- attempt to solve
- `cc-browser captcha solve --attempts 5` -- custom retry count

### Phase 2 tests

- `test/unit/captcha-detect.test.mjs` -- test detection with saved screenshots (requires ANTHROPIC_API_KEY)
- `test/unit/vision-mock.test.mjs` -- test vision.mjs error handling with mocked fetch
- `test/integration/captcha-local.test.mjs` -- full cycle against local test pages: navigate -> detect -> verify type -> solve -> check success element
- `test/captcha/captcha-live.test.mjs` -- opt-in tests against external demo URLs (may be flaky)

---

## Phase 3: Stealth Mode + Auto-Detection

### 3A. Stealth scripts -- MODIFY: `src/session.mjs`

When mode is `stealth`, inject additional init scripts:
- WebGL vendor/renderer spoofing
- Canvas fingerprint noise
- Plugin array spoofing
- Languages/timezone consistency
- `window.chrome.runtime` existence

### 3B. Auto-detection after navigation -- MODIFY: `src/interactions.mjs`

When mode is `human` or `stealth`, after `page.goto()` completes:
1. Quick DOM check for CAPTCHA presence
2. If detected, auto-solve before returning
3. Return captcha result alongside navigation result

### Phase 3 tests

- Stealth: navigate to `bot.sannysoft.com`, screenshot, verify fingerprint properties pass
- Auto-detect: navigate to local CAPTCHA page, verify solve happens automatically

---

## Files Summary

### New files (8)

| File | Purpose |
|------|---------|
| `src/human-mode.mjs` | Delay engine, mouse curves, typing simulation |
| `src/vision.mjs` | Anthropic API vision integration |
| `src/captcha.mjs` | CAPTCHA detection + all solvers |
| `test/mocks.mjs` | Mock Playwright objects |
| `test/fixtures/captcha-pages/test-server.mjs` | Local CAPTCHA test server |
| `test/fixtures/captcha-pages/*.html` (8 pages) | CAPTCHA test pages |
| `test/fixtures/captcha-urls.json` | External URL registry |
| `test/unit/*.test.mjs` + `test/integration/*.test.mjs` | Tests |

### Modified files (5)

| File | Changes |
|------|---------|
| `src/interactions.mjs` | Import human-mode, inject delays into 8 functions, enhance drag |
| `src/daemon.mjs` | Add mode routes, captcha routes |
| `src/session.mjs` | Mode state (get/set), stealth scripts |
| `src/cli.mjs` | Mode command, captcha commands |
| `package.json` | Add test scripts |

### No new npm dependencies

- LLM calls use native `fetch()` (available in Node 18+)
- Tests use `node:test` (built-in)
- All randomization is custom (no lodash/chance)

---

## Verification Plan

1. **Unit tests**: `npm run test:unit` -- delay ranges, mouse paths, typing delays, mode validation
2. **Local CAPTCHA tests**: Start test server + daemon, run `npm run test:captcha` against local pages
3. **Manual smoke test**:
   - `cc-browser start --workspace personal --mode human`
   - `cc-browser navigate --url https://www.google.com` -- observe visible delays
   - `cc-browser mode fast` -- verify instant behavior restored
   - `cc-browser navigate --url https://www.google.com/recaptcha/api2/demo`
   - `cc-browser captcha detect` -- verify reCAPTCHA detected
   - `cc-browser captcha solve` -- verify checkbox clicked
4. **Live CAPTCHA tests** (opt-in): Navigate to external demo pages, run solve
