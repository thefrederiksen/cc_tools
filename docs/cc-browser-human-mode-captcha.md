# cc-browser: Human Mode and CAPTCHA Solving

**Status:** Feature Proposal
**Date:** 2026-02-26
**Component:** cc-browser

---

## Problem Statement

cc-browser currently operates like a machine -- it navigates directly to URLs instantly, clicks elements with zero delay, never scrolls unnecessarily, and executes actions at superhuman speed. This makes it trivially detectable by anti-bot systems. When sites like Reddit present CAPTCHA challenges (reCAPTCHA, hCaptcha, drag puzzles, image selection), cc-browser has no ability to detect or solve them, requiring manual human intervention.

Two distinct problems need solving:

1. **Bot detection prevention** -- The browser needs to behave like a human by default so sites don't trigger CAPTCHAs and bot challenges in the first place.
2. **CAPTCHA solving** -- When challenges do appear, the browser needs to detect and solve them automatically using screenshot analysis and LLM vision capabilities.

---

## Feature 1: Browser Operating Modes

### Overview

cc-browser should support multiple operating modes that control how it interacts with pages. The default mode should be `human`, which mimics natural human browsing behavior.

### Modes

#### `human` (DEFAULT)

Mimics a real person browsing. Every action has natural variation and imprecision.

**Navigation behavior:**
- Random delay (800-2500ms) before navigating to a new URL
- Occasionally scrolls the current page slightly before clicking a link
- Mouse moves to the general area of a target before clicking (not pixel-perfect instant teleport)
- Slight random offset on click coordinates (humans don't click dead center)

**Typing behavior:**
- Characters typed one at a time with random inter-key delays (50-200ms)
- Occasional brief pauses mid-word (like thinking)
- Sometimes a small delay before starting to type (reading the field label)

**Scrolling behavior:**
- Smooth scroll with variable speed (not instant jumps)
- Occasional small scroll adjustments (overshoot then correct)
- Random idle pauses between scroll actions (500-1500ms)
- Sometimes scrolls past the target slightly then scrolls back

**Click behavior:**
- Mouse movement follows a natural curve path (not straight line teleport)
- Small random delay before click (100-400ms)
- Occasional hover before clicking (200-600ms)
- Random slight offset from element center

**Idle behavior:**
- Between sequences of actions, random pauses (1-4 seconds)
- Occasional mouse micro-movements during "reading" time
- Variable wait times that look like a person reading content

**Page load behavior:**
- Does not immediately interact after page load -- waits 1-3 seconds like a human would
- May scroll down slightly to "look at" the page before taking action

#### `fast`

Machine-speed execution with no artificial delays. For trusted sites, internal tools, and development/testing where speed matters and bot detection is not a concern.

- Instant navigation
- Instant clicks
- Bulk text input (no character-by-character typing)
- No unnecessary scrolling or mouse movement
- No idle pauses

This is how cc-browser operates today.

#### `stealth`

Maximum anti-detection. Human mode plus additional browser fingerprint protections.

- All human mode behaviors
- Navigator/WebDriver property masking
- WebGL fingerprint randomization
- Canvas fingerprint protection
- Timezone and locale consistency
- Realistic User-Agent strings
- Plugin and mime type spoofing
- Proper screen resolution reporting

### CLI Interface

```bash
# Start browser in human mode (default)
cc-browser start --workspace personal

# Explicitly set mode
cc-browser start --workspace personal --mode human
cc-browser start --workspace personal --mode fast
cc-browser start --workspace personal --mode stealth

# Change mode mid-session
cc-browser mode human
cc-browser mode fast

# Check current mode
cc-browser status   # Should show active mode in output
```

### Workspace Configuration

Mode can be set per-workspace in `workspace.json`:

```json
{
  "name": "Personal Chrome",
  "browser": "chrome",
  "workspace": "chrome-personal",
  "mode": "human",
  "humanMode": {
    "typingSpeed": "normal",
    "scrollBehavior": "natural",
    "clickDelay": "medium"
  }
}
```

---

## Feature 2: CAPTCHA Detection and Solving

### Overview

Using cc-browser's existing screenshot capability combined with LLM vision (Claude), the browser can detect when a CAPTCHA is present and attempt to solve it automatically.

### CAPTCHA Types and Strategies

#### Type 1: reCAPTCHA v2 ("I'm not a robot" checkbox)

**Detection:**
- Screenshot the page, send to LLM: "Is there a reCAPTCHA checkbox on this page?"
- Look for iframe with src containing `google.com/recaptcha`
- Check for elements with class `g-recaptcha`

**Solving:**
- Click the checkbox
- If image challenge appears, proceed to Type 2

#### Type 2: Image Selection ("Select all images with traffic lights")

**Detection:**
- Screenshot shows a grid of images with a text prompt
- LLM identifies the challenge type and instruction

**Solving:**
- Take screenshot of the challenge grid
- Send to LLM with prompt: "This is a CAPTCHA image grid. The instruction says '[instruction text]'. Which grid squares match? Return the row,column positions."
- Click the identified squares
- Click verify
- If new images appear (the "fade in" replacement), repeat

**Implementation notes:**
- Grid is typically 3x3 or 4x4
- Need to map grid positions to click coordinates
- May need multiple rounds as images refresh
- Success rate depends on LLM vision accuracy

#### Type 3: hCaptcha (Similar to reCAPTCHA image challenges)

**Detection:**
- iframe with src containing `hcaptcha.com`
- Similar grid-based image challenges

**Solving:**
- Same approach as reCAPTCHA image selection
- Different grid layouts possible

#### Type 4: Drag/Slide Puzzles ("Drag the piece to complete the image")

**Detection:**
- Screenshot shows a puzzle piece that needs to be dragged to a position
- LLM identifies the puzzle type

**Solving:**
- Take screenshot
- Send to LLM: "This is a slider CAPTCHA. Where does the puzzle piece need to go? Identify the x-coordinate offset."
- Use `cc-browser drag` with human-like movement (not a straight line)
- Simulate natural drag behavior: slight wobble, variable speed, overshoot-correct

**Implementation notes:**
- This is the hardest type -- requires precise coordinate detection
- The drag movement MUST look human (acceleration, deceleration, slight y-axis wobble)
- May need multiple attempts with slightly different positions

#### Type 5: Text-based CAPTCHAs (Distorted text)

**Detection:**
- Screenshot shows distorted text with an input field

**Solving:**
- Send screenshot to LLM: "What text do you see in this CAPTCHA image?"
- Type the recognized text into the input field
- These are increasingly rare but still exist

#### Type 6: Cloudflare Turnstile / "Just a moment..."

**Detection:**
- Page shows Cloudflare challenge screen
- Text: "Checking your browser..." or "Just a moment..."

**Solving:**
- Often resolves automatically with proper browser fingerprint (stealth mode)
- If checkbox appears, click it
- If it persists, may need stealth mode improvements

### CAPTCHA Solver Architecture

```
Page Load / Navigation
       |
       v
  Auto-Screenshot
       |
       v
  CAPTCHA Detector (LLM Vision)
       |
       +---> No CAPTCHA detected -> Continue normally
       |
       +---> CAPTCHA detected
                |
                v
          Identify CAPTCHA type
                |
                v
          Run type-specific solver
                |
                +---> Solved -> Continue with original action
                |
                +---> Failed -> Retry (max 3 attempts)
                |
                +---> Unsolvable -> Notify user, pause for manual solve
```

### CLI Interface

```bash
# Auto-solve CAPTCHA on current page
cc-browser captcha solve

# Detect without solving (diagnostic)
cc-browser captcha detect

# Configure auto-solve behavior
cc-browser captcha --auto          # Enable auto-detection after every navigate
cc-browser captcha --auto=off      # Disable auto-detection

# Solve with screenshot debug output
cc-browser captcha solve --debug   # Saves annotated screenshots showing what was detected
```

### Integration with Navigation

When `--mode human` is active and a CAPTCHA is detected after navigation:

1. Take a screenshot automatically
2. Detect CAPTCHA presence via LLM vision
3. If found, attempt to solve before returning control
4. If solve fails after retries, return an error with instruction: "CAPTCHA detected but could not be solved automatically. Manual intervention required."

---

## Feature 3: LLM Vision Integration

### Overview

The CAPTCHA solver and human-mode intelligence both require LLM vision capability. cc-browser needs a way to send screenshots to an LLM and get structured responses.

### Approach

Use Claude Code CLI as the LLM backend (consistent with cc-image OCR pattern):

```bash
# Internal: pipe screenshot to Claude for analysis
cat screenshot.png | claude --model haiku "Analyze this screenshot. Is there a CAPTCHA? If yes, what type?"
```

Or via the Anthropic API directly for lower latency:

```javascript
// Direct API call from daemon
const response = await anthropic.messages.create({
  model: "claude-haiku-4-5-20251001",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      { type: "image", source: { type: "base64", media_type: "image/png", data: screenshotBase64 } },
      { type: "text", text: "Is there a CAPTCHA on this page? If yes, identify the type and describe what needs to be done to solve it." }
    ]
  }]
});
```

### Model Selection

- **Detection**: Use Haiku for speed (just needs to identify presence/type)
- **Solving**: Use Sonnet for image selection accuracy (needs to identify correct grid squares)
- **Drag puzzles**: Use Sonnet for precise coordinate estimation

### Cost Considerations

- Each CAPTCHA solve attempt = 1-3 LLM calls
- Haiku detection call is cheap (~$0.001)
- Sonnet solving call is moderate (~$0.01)
- Auto-detection on every page load could add up -- consider rate limiting or only detecting when navigation seems blocked

---

## Testing Strategy

### Where to Find CAPTCHAs Consistently

For development and testing, we need reliable CAPTCHA sources:

1. **Google reCAPTCHA demo page**: https://www.google.com/recaptcha/api2/demo
2. **hCaptcha demo**: https://dashboard.hcaptcha.com/welcome_accessibility
3. **Sites that trigger on new browsers**: Reddit, LinkedIn (when cookies cleared)
4. **reCAPTCHA test keys**: Google provides test site keys that always show the challenge
5. **Custom test page**: Build a local HTML page with embedded reCAPTCHA/hCaptcha using test keys

### Test Cases

| Test | Input | Expected |
|------|-------|----------|
| Detect reCAPTCHA checkbox | Page with reCAPTCHA v2 | Returns: type=recaptcha_v2, action=click_checkbox |
| Solve reCAPTCHA checkbox | reCAPTCHA demo page | Clicks checkbox, reports success |
| Detect image grid | reCAPTCHA image challenge | Returns: type=image_grid, instruction="Select all [X]" |
| Solve image grid | Image challenge screenshot | Identifies correct squares, clicks, verifies |
| Detect hCaptcha | Page with hCaptcha | Returns: type=hcaptcha |
| Detect Cloudflare | Cloudflare challenge page | Returns: type=cloudflare_turnstile |
| Detect drag puzzle | Slider CAPTCHA | Returns: type=slider, estimated_offset=NNpx |
| No CAPTCHA present | Normal page | Returns: type=none |
| Human mode delays | Navigate + click sequence | Measurable random delays between actions |
| Human mode typing | Type into search box | Character-by-character with visible delays |
| Human mode scrolling | Scroll down page | Smooth scroll with natural speed variation |

### Test Automation

```bash
# Run CAPTCHA detection tests
cc-browser test captcha-detection

# Run human mode timing validation
cc-browser test human-mode

# Full integration test (requires network)
cc-browser test captcha-solve --live
```

---

## Implementation Priority

### Phase 1: Human Mode (High Impact, Lower Complexity)

1. Add `--mode` flag to `start` command and `mode` subcommand
2. Implement delay injection layer in `interactions.mjs`
3. Add human-like mouse movement curves
4. Add natural typing simulation
5. Add smooth scrolling with variation
6. Add random idle pauses between action sequences
7. Set `human` as default mode
8. Add mode to workspace.json configuration

### Phase 2: CAPTCHA Detection (Foundation for Solving)

1. Add LLM vision integration (Anthropic API from daemon)
2. Implement screenshot-to-LLM pipeline
3. Build CAPTCHA type classifier
4. Add `captcha detect` command
5. Add auto-detection option after navigation

### Phase 3: CAPTCHA Solving - Simple Types

1. Implement reCAPTCHA v2 checkbox solver
2. Implement Cloudflare Turnstile handler
3. Implement text CAPTCHA reader
4. Add `captcha solve` command
5. Add retry logic and failure reporting

### Phase 4: CAPTCHA Solving - Complex Types

1. Implement image grid solver (reCAPTCHA, hCaptcha)
2. Implement drag/slider puzzle solver
3. Build coordinate mapping for grid and slider challenges
4. Add debug/diagnostic screenshot output
5. Performance tuning and accuracy improvements

### Phase 5: Stealth Mode

1. Navigator/WebDriver property masking
2. Browser fingerprint randomization
3. Canvas and WebGL protection
4. Consistent timezone/locale/screen reporting

---

## Open Questions

1. **API key management** -- Where should the Anthropic API key live for daemon-side LLM calls? Environment variable? Workspace config?
2. **Cost budget** -- Should there be a configurable limit on LLM calls per session for CAPTCHA solving?
3. **Solver accuracy thresholds** -- At what confidence level should we attempt a solve vs. ask for human help?
4. **Drag puzzle precision** -- How accurate does the LLM need to be on pixel coordinates? Do we need iterative correction?
5. **Multi-step CAPTCHAs** -- Some image grids require solving 3-4 rounds. What's our max retry budget?

---

## Related Files

- `src/cc-browser/src/interactions.mjs` -- Where human-mode delays would be injected
- `src/cc-browser/src/daemon.mjs` -- Where mode state and LLM integration would live
- `src/cc-browser/src/session.mjs` -- Browser connection and page state management
- `src/cc-browser/src/snapshot.mjs` -- Screenshot and element labeling (used for CAPTCHA detection)
- `src/cc-browser/src/cli.mjs` -- CLI argument parsing for new commands
