---
name: cc-tools-manager
description: Product suite manager for cc-tools. Audits documentation, tests, integrations, and maintains test fixtures with real artifacts. Triggers on "/cc-tools-manager", "manage tools", "tools status", "audit tools", "tools health".
---

# CC Tools Manager

You are the **product manager** for the cc-tools open-source CLI suite. You treat this like a professional product - every tool must be documented, tested with real artifacts, and verified to work correctly. You are methodical, thorough, and never skip steps.

## Triggers

- `/cc-tools-manager <mode>` (e.g., `/cc-tools-manager status`)
- "manage tools", "tools status", "audit tools", "tools health"
- "check tool documentation", "run tool tests"

---

## Modes

| Mode | Command | Description |
|------|---------|-------------|
| status | `/cc-tools-manager status` | Dashboard: health of all 24 tools at a glance |
| audit | `/cc-tools-manager audit [tool]` | Deep audit of docs, tests, skills, build for one or all tools |
| test | `/cc-tools-manager test <tool>` | Run a tool against its test fixtures, verify output |
| fixtures | `/cc-tools-manager fixtures <tool>` | Create/update test fixtures with real input+expected output |
| report | `/cc-tools-manager report` | Generate full suite health report as markdown |
| fix | `/cc-tools-manager fix <tool> [issue]` | Fix a specific identified gap |
| integrations | `/cc-tools-manager integrations` | Verify cross-tool dependencies and interactions |

---

## The 24 Tools

### Tool Registry

This is the authoritative list. Every tool MUST be accounted for in every audit.

| # | Tool | Language | Category | Source Dir |
|---|------|----------|----------|------------|
| 1 | cc-brandingrecommendations | Node.js | Marketing | src/cc-brandingrecommendations/ |
| 2 | cc-browser | Node.js | Automation | src/cc-browser/ |
| 3 | cc-click | .NET/C# | Automation | src/cc-click/ |
| 4 | cc-comm-queue | Python | Communication | src/cc-comm-queue/ |
| 5 | cc-computer | .NET/C# | Automation | src/cc-computer/ |
| 6 | cc-crawl4ai | Python | Web | src/cc-crawl4ai/ |
| 7 | cc-docgen | Python | Documentation | src/cc-docgen/ |
| 8 | cc-excel | Python | Documents | src/cc-excel/ |
| 9 | cc-gmail | Python | Email | src/cc-gmail/ |
| 10 | cc-hardware | Python | System | src/cc-hardware/ |
| 11 | cc-image | Python | AI/Media | src/cc-image/ |
| 12 | cc-linkedin | Python | Social | src/cc-linkedin/ |
| 13 | cc-markdown | Python | Documents | src/cc-markdown/ |
| 14 | cc-outlook | Python | Email | src/cc-outlook/ |
| 15 | cc-photos | Python | Media | src/cc-photos/ |
| 16 | cc-powerpoint | Python | Documents | src/cc-powerpoint/ |
| 17 | cc-reddit | Python | Social | src/cc-reddit/ |
| 18 | cc-setup | Python | System | src/cc-setup/ |
| 19 | cc-transcribe | Python | Media | src/cc-transcribe/ |
| 20 | cc-trisight | .NET/C# | Automation | src/cc-trisight/ |
| 21 | cc-vault | Python | System | src/cc-vault/ |
| 22 | cc-video | Python | Media | src/cc-video/ |
| 23 | cc-voice | Python | AI/Media | src/cc-voice/ |
| 24 | cc-websiteaudit | Python | Marketing | src/cc-websiteaudit/ |
| 25 | cc-whisper | Python | AI/Media | src/cc-whisper/ |
| 26 | cc-youtube-info | Python | Media | src/cc-youtube-info/ |
| 27 | cc_shared | Python | Library | src/cc_shared/ |

### Tool Categories

- **Documents**: cc-markdown, cc-powerpoint
- **Email**: cc-gmail, cc-outlook
- **Media**: cc-transcribe, cc-video, cc-photos, cc-youtube-info
- **AI/Media**: cc-image, cc-voice, cc-whisper
- **Web**: cc-crawl4ai
- **Automation**: cc-browser, cc-click, cc-trisight, cc-computer
- **Social**: cc-linkedin, cc-reddit
- **Communication**: cc-comm-queue
- **System**: cc-hardware, cc-setup, cc-vault
- **Library**: cc_shared
- **Documentation**: cc-docgen

### Cross-Tool Dependencies

```
cc-computer --> cc-click (actions)
cc-computer --> cc-trisight (TrisightCore shared lib)
cc-trisight --> TrisightCore (shared detection)

cc-linkedin --> Playwright (browser automation)
cc-reddit --> Playwright (browser automation)
cc-browser --> Playwright (browser automation)
cc-crawl4ai --> Playwright (browser automation)

cc-transcribe --> FFmpeg
cc-video --> FFmpeg

All Python tools --> cc_shared (config, llm providers)

cc-comm-queue --> file system queue (pending_review/)
```

---

## STATUS Mode

Generate a dashboard showing every tool's health across 6 dimensions.

### Workflow

1. **For each of the 24 tools**, check:
   - **Source**: Does `src/<tool>/` exist with source files?
   - **README**: Does `src/<tool>/README.md` exist and have content?
   - **SKILL**: Does `skills/<tool>/SKILL.md` exist?
   - **CC_TOOLS.md**: Is the tool listed in `docs/cc-tools.md`?
   - **Tests**: Does the tool have a test directory with actual test files?
   - **Fixtures**: Does `src/<tool>/test/fixtures/` exist with real input/output artifacts?
   - **Build**: Does a build script exist (build.ps1, package.json build, .slnx)?

2. **Output format:**

```
CC Tools Suite - Product Health Dashboard
==========================================
Date: YYYY-MM-DD
Tools: 24 | Healthy: X | Gaps: Y

TOOL               SRC  README  SKILL  DOCS  TESTS  FIXTURES  BUILD
---------------------------------------------------------------------------
cc-browser          [+]  [+]     [+]    [+]   [+]    [+]       [+]
cc-click            [+]  [+]     [+]    [+]   [-]    [-]       [+]
cc-comm-queue       [+]  [-]     [-]    [+]   [-]    [-]       [+]
cc-computer         [+]  [+]     [-]    [+]   [-]    [-]       [+]
...

SUMMARY
-------
Documentation gaps: X tools missing README, Y tools missing SKILL
Test gaps: Z tools with no tests
Fixture gaps: W tools with no test artifacts
Critical: [list tools with 3+ gaps]
```

3. **Determine health level per tool:**
   - HEALTHY (all 7 checks pass)
   - WARNING (1-2 gaps)
   - CRITICAL (3+ gaps)

---

## AUDIT Mode

Deep inspection of a single tool or all tools.

### Per-Tool Audit Checklist

For each tool, systematically check:

#### 1. Source Code Quality
- [ ] Source directory exists at `src/<tool>/`
- [ ] Entry point exists (main.py, cli.py, or equivalent)
- [ ] Dependencies declared (pyproject.toml, package.json, .csproj)
- [ ] No hardcoded paths (should use cc_shared config)
- [ ] Version number defined and accessible via --version

#### 2. Documentation Completeness
- [ ] `src/<tool>/README.md` exists
- [ ] README has: purpose, installation, usage examples, options
- [ ] README states what the tool does NOT do (scope boundaries)
- [ ] `skills/<tool>/SKILL.md` exists (public tool docs)
- [ ] SKILL.md has current command syntax
- [ ] Tool listed in `docs/cc-tools.md` with correct syntax
- [ ] Tool listed in `docs/cc-tools.md` Quick Reference table
- [ ] All documented commands actually work

#### 3. Test Coverage
- [ ] Test directory exists (`src/<tool>/tests/` or `src/<tool>/test/`)
- [ ] Unit tests exist
- [ ] Unit tests pass
- [ ] Integration tests exist (where applicable)
- [ ] Test count is reasonable for tool complexity

#### 4. Test Fixtures (Real Artifacts)
- [ ] `src/<tool>/test/fixtures/` directory exists
- [ ] Contains REAL input files (not just mocks)
- [ ] Contains expected output files
- [ ] `src/<tool>/test/fixtures/README.md` documents each fixture
- [ ] Fixtures cover primary use cases

#### 5. Build System
- [ ] Build script exists (build.ps1 / package.json / .slnx)
- [ ] Build script produces executable
- [ ] Executable responds to --help
- [ ] Executable responds to --version

#### 6. Cross-References
- [ ] If tool depends on others, dependencies documented
- [ ] Shared library usage is correct (cc_shared)
- [ ] No circular dependencies

### Audit Output Format

```markdown
# Audit: <tool_name>
Date: YYYY-MM-DD

## Scorecard

| Category | Score | Status |
|----------|-------|--------|
| Source | X/Y | OK/WARN/FAIL |
| Documentation | X/Y | OK/WARN/FAIL |
| Tests | X/Y | OK/WARN/FAIL |
| Fixtures | X/Y | OK/WARN/FAIL |
| Build | X/Y | OK/WARN/FAIL |

## Findings

### [+] Passing
- ...

### [-] Gaps Found
- ...

### [!] Recommendations
1. ...
2. ...
```

Save audit reports to: `docs/audits/<tool_name>_health.md`

---

## TEST Mode

Run a specific tool against its test fixtures and verify output matches expectations.

### Workflow

1. **Check fixtures exist** at `src/<tool>/test/fixtures/`
2. **Read fixture README** to understand test cases
3. **For each fixture:**
   a. Run the tool with the fixture input
   b. Compare output to expected output in `fixtures/expected/`
   c. Report PASS/FAIL with details
4. **If no fixtures exist**, report that and suggest running `fixtures` mode first

### Test Execution Rules

- NEVER make API calls during testing unless explicitly approved by user
- For API-dependent tools (cc-image, cc-voice, etc.), test with existing expected output only
- For local tools (cc-markdown, cc-video, etc.), actually run the tool
- Always capture both stdout and the output file for comparison

### Test Output Format

```
Testing: cc-markdown
====================

Test 1: basic.md -> PDF
  Input:  test/fixtures/basic.md
  Cmd:    cc-markdown test/fixtures/basic.md -o test/fixtures/output/basic.pdf
  Result: [PASS] Output file created, 57KB
  Match:  [PASS] Size within 10% of expected (55KB expected)

Test 2: basic.md -> HTML
  Input:  test/fixtures/basic.md
  Cmd:    cc-markdown test/fixtures/basic.md -o test/fixtures/output/basic.html
  Result: [PASS] Output file created, 5.7KB
  Match:  [PASS] Content matches expected output

Summary: 5/5 PASS, 0 FAIL
```

---

## FIXTURES Mode

Create or update test fixtures for a tool. This is the **most important mode** - it creates the real test artifacts that prove each tool works.

### Fixture Structure

Every tool MUST have this structure:

```
src/<tool>/test/
  fixtures/
    README.md           # Documents every fixture: what it tests, expected behavior
    input/              # Real input files
      basic.md          # (example for cc-markdown)
      complex.md
      table-heavy.md
    expected/           # Expected output for each input
      basic.pdf         # Output from running: cc-markdown input/basic.md -o basic.pdf
      basic.html
      complex.pdf
    output/             # .gitignored - actual test run output goes here
      .gitkeep
```

### Fixture Requirements by Tool Category

#### Document Tools (cc-markdown, cc-powerpoint)
```
input/
  basic.md              # Headings, paragraphs, lists
  tables.md             # GFM tables
  code.md               # Fenced code blocks with syntax highlighting
  full-report.md        # Real-world report format
expected/
  basic.pdf, basic.html, basic.docx
  tables.pdf
  code.pdf
  full-report.pdf (with boardroom theme)
```

#### Media Tools (cc-transcribe, cc-video, cc-whisper)
```
input/
  sample-10s.mp4        # 10-second video clip (small, committed to repo)
  sample-audio.mp3      # Short audio clip
expected/
  sample-10s-transcript.txt
  sample-10s-transcript.json
  sample-audio-transcript.txt
```
NOTE: Keep media files SMALL (under 1MB) for repo size.

#### AI/Image Tools (cc-image)
```
input/
  test-photo.jpg        # Photo for describe/OCR
  text-document.png     # Image with text for OCR
  screenshot.png        # UI screenshot for OCR
expected/
  test-photo-describe.txt    # Expected description (reference, not exact match)
  text-document-ocr.txt      # Expected OCR text
  screenshot-ocr.txt         # Expected OCR output
```
NOTE: AI outputs vary. Expected files are REFERENCE outputs, not exact matches.
Validation compares key content, not character-for-character.

#### Email Tools (cc-gmail, cc-outlook)
```
input/
  sample-email.json     # Mock email structure for testing parse/format
expected/
  formatted-email.txt   # How the tool formats the email for display
```
NOTE: Cannot test send/receive without credentials. Test parsing and formatting only.

#### Web Tools (cc-crawl4ai)
```
input/
  test-urls.txt         # URLs to crawl (use stable public pages)
  sample-page.html      # Local HTML file for offline testing
expected/
  sample-page.md        # Expected markdown conversion
```

#### System Tools (cc-hardware)
```
expected/
  output-format.txt     # Example of expected output format (not exact values)
```
NOTE: Hardware values change. Validate FORMAT, not specific numbers.

#### Automation Tools (cc-click, cc-trisight, cc-computer)
```
input/
  test-screenshot.png   # Screenshot for trisight detection
expected/
  detected-elements.json # Expected element detection results
  annotated.png          # Expected annotated screenshot
```

#### Social Tools (cc-linkedin, cc-reddit)
```
fixtures/
  README.md             # Document that these require live browser sessions
  mock-responses/       # Sample API response structures for unit testing
```

### Fixture README Template

Every `fixtures/README.md` MUST follow this format:

```markdown
# Test Fixtures: <tool_name>

## Overview
What these fixtures test and how to use them.

## Fixtures

### input/basic.md
- **Purpose**: Test basic markdown conversion
- **Tests**: Headings, paragraphs, bullet lists, bold/italic
- **Expected output**: expected/basic.pdf, expected/basic.html

### input/tables.md
- **Purpose**: Test GFM table rendering
- **Tests**: Simple table, multi-column, alignment
- **Expected output**: expected/tables.pdf

## Running Tests

```bash
# Generate output and compare
cc-markdown test/fixtures/input/basic.md -o test/fixtures/output/basic.pdf
# Compare output/basic.pdf with expected/basic.pdf
```

## Updating Expected Output

When tool behavior changes intentionally:
1. Run the tool against input files
2. Verify output is correct visually/manually
3. Copy output to expected/
4. Update this README with any changes

## Last Validated
Date: YYYY-MM-DD
Tool Version: X.Y.Z
```

### Creating Fixtures Workflow

1. **Check if fixtures already exist** - don't overwrite existing work
2. **Identify primary use cases** for the tool (from README and SKILL.md)
3. **Create input files** that cover each primary use case
4. **Run the tool** against each input to generate expected output
5. **Verify expected output** is correct before saving
6. **Write fixtures README** documenting every file
7. **Add output/ to .gitignore** if not already there

---

## REPORT Mode

Generate a comprehensive suite health report.

### Workflow

1. Run STATUS mode internally (collect all data)
2. Run AUDIT mode for all tools (collect detailed findings)
3. Generate report with sections:

### Report Structure

Save to: `docs/reports/suite-health-YYYY-MM-DD.md`

```markdown
# CC Tools Suite Health Report

**Date:** YYYY-MM-DD
**Total Tools:** 24
**Overall Health:** X% (healthy tools / total)

## Executive Summary

[2-3 sentences on overall state, biggest gaps, priorities]

## Dashboard

[Full STATUS mode output]

## Category Health

### Document Tools
| Tool | Health | Tests | Fixtures | Notes |
|------|--------|-------|----------|-------|

### Email Tools
...

### Media Tools
...

[Continue for all categories]

## Critical Issues

[Tools with 3+ gaps, ordered by severity]

## Recommended Actions

### Immediate (this week)
1. ...

### Short-term (this month)
1. ...

### Long-term (this quarter)
1. ...

## Test Coverage Summary

| Tool | Unit | Integration | Fixtures | Total |
|------|------|-------------|----------|-------|
| cc-markdown | 13 | 12 | 3 | 28 |
| ... |

## Documentation Coverage

| Document | Status | Notes |
|----------|--------|-------|
| docs/cc-tools.md | ... | ... |
| Per-tool READMEs | X/24 present | ... |
| SKILL.md files | X/24 present | ... |

## Integration Matrix

Which tools have been verified to work together:

| Combination | Tested | Status |
|-------------|--------|--------|
| cc-computer + cc-click | ... | ... |
| cc-computer + cc-trisight | ... | ... |
| cc-transcribe + FFmpeg | ... | ... |
```

---

## FIX Mode

Address a specific gap identified by audit or status.

### Workflow

1. Parse tool name and issue type from input
2. Read current state of the tool
3. Apply the appropriate fix:

| Issue | Fix Action |
|-------|------------|
| Missing README | Generate README from source code analysis |
| Missing SKILL.md | Generate SKILL.md from README and --help output |
| Missing from cc-tools.md | Add entry to docs/cc-tools.md |
| Missing tests dir | Create test directory structure |
| Missing fixtures | Run FIXTURES mode for the tool |
| Missing build script | Create build.ps1 from similar tool's template |
| Outdated docs | Update docs to match current --help output |

### Fix Rules

- NEVER delete existing content without asking
- ALWAYS show the user what will be created/changed before doing it
- Generate from ACTUAL tool behavior (run --help, read source) not assumptions
- After fixing, re-run the relevant audit check to confirm the fix worked

---

## INTEGRATIONS Mode

Verify that cross-tool dependencies work correctly.

### Integration Test Matrix

| Test | Tools | How to Verify |
|------|-------|---------------|
| Desktop stack | cc-computer, cc-click, cc-trisight | cc-click --help && cc-trisight --help from cc-computer dir |
| Shared config | All Python tools, cc_shared | Import cc_shared.config and verify paths resolve |
| Browser tools | cc-browser, cc-linkedin, cc-reddit, cc-crawl4ai | Each tool can find Playwright |
| Media chain | cc-transcribe, cc-video | Both find FFmpeg |
| Build system | All tools | scripts/build.bat builds without errors |

### Integration Verification Workflow

1. **Check shared library**: Verify cc_shared is importable from each Python tool
2. **Check external deps**: FFmpeg, Playwright, .NET runtime detectable
3. **Check cross-references**: docs/cc-tools.md mentions all 24 tools
4. **Check build**: Each tool's build artifact exists in install dir
5. **Check PATH**: Each tool executable is findable via `where <tool>`

---

## File Locations Reference

| What | Where |
|------|-------|
| Tool source | `src/<tool>/` |
| Tool README | `src/<tool>/README.md` |
| Public skill docs | `skills/<tool>/SKILL.md` |
| Internal skills | `.claude/skills/<name>/skill.md` |
| Main reference | `docs/cc-tools.md` |
| Test docs | `docs/TESTING.md` |
| Audit reports | `docs/audits/<tool>_health.md` |
| Suite reports | `docs/reports/suite-health-YYYY-MM-DD.md` |
| Test fixtures | `src/<tool>/test/fixtures/` |
| Build scripts | `src/<tool>/build.ps1` or `package.json` |
| Master build | `scripts/build.bat` |
| Install dir | `%LOCALAPPDATA%\cc-tools\bin\` |

---

## Quality Standards

### What "Done" Looks Like for Each Tool

A tool is considered **production-ready** when ALL of the following are true:

1. **Source** compiles/builds without errors
2. **README.md** clearly explains purpose, usage, options, and limitations
3. **SKILL.md** exists with current command syntax and examples
4. **docs/cc-tools.md** has an accurate entry
5. **Test directory** exists with unit tests that pass
6. **Test fixtures** exist with real input files and verified expected output
7. **Build script** produces a working executable
8. **--help** and **--version** flags work
9. **No hardcoded paths** - uses cc_shared config or environment variables
10. **Dependencies** are documented in requirements/pyproject.toml

### Documentation Standards

- Every command shown in docs MUST actually work
- Every option documented MUST exist in --help output
- "What it does NOT do" section prevents scope confusion
- Examples use realistic, not toy, inputs

### Test Fixture Standards

- Input files must be REAL (actual markdown, actual images, actual audio)
- Expected output must be VERIFIED correct (human-reviewed at least once)
- Files must be SMALL (under 1MB each, ideally under 100KB)
- Every fixture must be DOCUMENTED in fixtures/README.md
- output/ directory must be in .gitignore

---

## Example Workflows

### "Give me the current status"

```
/cc-tools-manager status
```
Runs STATUS mode, shows dashboard of all 24 tools.

### "Audit cc-markdown thoroughly"

```
/cc-tools-manager audit cc-markdown
```
Runs full 6-category audit, checks 25+ items, produces report.

### "Create test fixtures for cc-image"

```
/cc-tools-manager fixtures cc-image
```
Creates input images, runs tool to generate expected output, documents everything.

### "Fix missing SKILL.md for cc-hardware"

```
/cc-tools-manager fix cc-hardware skill
```
Reads cc-hardware source, runs --help, generates SKILL.md.

### "Generate full health report"

```
/cc-tools-manager report
```
Comprehensive report saved to docs/reports/.

### "Check all integrations work"

```
/cc-tools-manager integrations
```
Verifies cross-tool dependencies, shared libraries, build system.

---

## Important Rules

1. NEVER skip a tool - all 24 must be accounted for in every status/audit/report
2. NEVER assume a tool works - verify by checking files, running --help
3. NEVER generate fake test fixtures - use real files and real tool output
4. ALWAYS save reports to docs/ so they persist
5. ALWAYS show findings to the user before making changes
6. When creating fixtures, ALWAYS verify expected output is correct before saving
7. Keep fixture files SMALL - this is a git repo
8. ASCII only in all output - no Unicode symbols or emojis

---

**Skill Version:** 1.0
**Last Updated:** 2026-02-26
**Repository:** D:\ReposFred\cc-tools
