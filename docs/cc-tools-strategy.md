# CC Tools - Open Source Strategy Document

## Executive Summary

CenterConsulting Inc. (CC) is launching a suite of open source CLI tools for agentic coding workflows. These tools are rebranded from the existing `fred_tools` library, packaged as standalone executables, and released under the MIT license.

**Goal:** Build notoriety and brand recognition for CenterConsulting through valuable open source contributions to the AI/developer community.

**Repository:** github.com/CenterConsulting/cc-tools

---

## Strategic Vision

### What We're Doing

1. **Take existing fred_tools** - Working, battle-tested code from internal pipelines
2. **Rebrand with CC naming** - Consistent `cc-[function]` naming for brand recognition
3. **Package as standalone CLI executables** - Download and run, no installation
4. **Release open source on GitHub** - MIT license, free for everyone
5. **Create Claude Code skills** - Downloadable skills and plugins
6. **Campaign on social media** - Each release is a marketing opportunity

### Why This Strategy Works

| Factor | Benefit |
|--------|---------|
| **Existing Code** | No starting from scratch - tools are already working |
| **CLI for Agentic Coding** | Growing market with Claude Code, Cursor, Windsurf, etc. |
| **Open Source** | Builds trust, community, and visibility |
| **Multiple Tools** | Each release is content for social campaigns |
| **Tools Reinforce Each Other** | Users of cc-markdown discover cc-transcribe |
| **MIT License** | Maximum adoption - no GPL restrictions |

### Target Audience

**Primary:** Developers and power users working with AI coding assistants (Claude Code, etc.) who need CLI tools that "just work"

**Secondary:** Technical content creators, documentation teams, anyone automating document workflows

---

## Tool Inventory

### Current fred_tools Capabilities

| Module | Functions | Description |
|--------|-----------|-------------|
| **tts** | `tts()`, `tts_to_file()` | Text-to-speech via OpenAI |
| **stt** | `whisper()`, `whisper_timestamps()` | Audio transcription |
| **stt** | `transcribe_video()` | Video transcription + screenshot extraction |
| **image_gen** | `image_gen()`, `image_edit()` | DALL-E image generation |
| **vision** | `vision_describe()`, `vision_extract_text()` | GPT-4 Vision analysis and OCR |
| **video** | `extract_audio()`, `get_video_info()`, `extract_screenshots()` | Video utilities |
| **document** | `markdown_to_pdf()`, `markdown_to_word()` | Document conversion |

---

## Commercial Viability Analysis

### Tier 1 - High Value (Lead Releases)

These tools have clear market differentiation and high demand.

| Tool | Value Proposition | Market Gap |
|------|-------------------|------------|
| **Markdown to PDF/Word** | MIT-licensed, CSS-styled document conversion | Pandoc is GPL, complex, no built-in themes |
| **Video Transcribe** | Transcription + automatic screenshot extraction | No single tool does both well |
| **Image Toolkit** | Unified image tool: AI analysis, OCR, generation, resize | No single CLI does all of these |

### Tier 2 - Solid Utility

Useful tools with clear audiences, but more competition exists.

| Tool | Value Proposition | Notes |
|------|-------------------|-------|
| **TTS** | Simple text-to-speech CLI | Content creators, accessibility |
| **Whisper** | Audio transcription wrapper | Simpler than raw Whisper setup |

### Tier 3 - Niche/Supporting

Supporting utilities or very specific use cases.

| Tool | Notes |
|------|-------|
| **Video utilities** | Extract audio, info, screenshots - supporting functions |

---

## CC Tool Naming Convention

### Naming Pattern

All tools follow the pattern: `cc-[function]`

- **cc** = CenterConsulting brand prefix
- **[function]** = Clear, single-word descriptor of what the tool does

### Proposed Tool Names

| Current Function | CC Tool Name | CLI Command | Description |
|------------------|--------------|-------------|-------------|
| markdown_to_pdf/word | **cc-markdown** | `cc-markdown` | Markdown to PDF/Word/HTML with themes |
| transcribe_video | **cc-transcribe** | `cc-transcribe` | Video/audio transcription with timestamps |
| vision + image_gen + image manipulation | **cc-image** | `cc-image` | Image toolkit: generate, analyze, OCR, resize, convert |
| tts | **cc-voice** | `cc-voice` | Text-to-speech |
| whisper | **cc-whisper** | `cc-whisper` | Audio transcription |
| video utilities | **cc-video** | `cc-video` | Video info, extract audio, screenshots |

### Example CLI Usage

```bash
# Convert markdown to PDF with corporate theme
cc-markdown report.md -o report.pdf --theme Boardroom

# Transcribe a video with screenshots
cc-transcribe meeting.mp4 -o ./output/

# Image toolkit (unified)
cc-image describe photo.jpg                       # AI analysis
cc-image extract-text screenshot.png              # OCR
cc-image generate "A sunset over mountains" -o sunset.png  # DALL-E
cc-image resize photo.png -o thumb.jpg --width 800         # Resize (no API)
cc-image convert photo.png -o photo.webp          # Convert format (no API)
cc-image info photo.png                           # Get metadata (no API)

# Generate speech from text
cc-voice "Hello world" -o greeting.mp3

# Transcribe audio
cc-whisper interview.mp3 -o transcript.txt

# Get video info
cc-video info presentation.mp4
```

---

## Launch Strategy

### Phase 1: Foundation (Lead Tools)

| Order | Tool | Why First |
|-------|------|-----------|
| 1 | **cc-markdown** | Strongest differentiator, clear Pandoc alternative |
| 2 | **cc-transcribe** | Unique value, combines transcription + visual |
| 3 | **cc-image** | Unified image toolkit, broad utility |

### Phase 2: Audio Tools

| Order | Tool | Why |
|-------|------|-----|
| 4 | **cc-voice** | Content creators, accessibility |
| 5 | **cc-whisper** | Complements cc-transcribe |

### Phase 3: Utility Tools

| Order | Tool | Why |
|-------|------|-----|
| 6 | **cc-video** | Supporting utilities |

### Social Media Campaign

Each tool release is a content opportunity:

1. **Announcement post** - "Introducing cc-markdown: MIT-licensed Pandoc alternative"
2. **Demo video** - 60-second showing the tool in action
3. **Use case thread** - "5 ways to use cc-markdown with Claude Code"
4. **Comparison post** - "cc-markdown vs Pandoc: Why we built this"

Platforms: LinkedIn (primary for B2B/consulting), Twitter/X (developer community), GitHub (releases)

---

## Technical Requirements

### All CC Tools Must:

1. **Single executable** - Download and run, no installation
2. **Cross-platform** - Windows, Linux, macOS binaries
3. **Self-contained** - No runtime dependencies
4. **Language agnostic** - Use best language for the problem (Python, TypeScript, C#)
5. **MIT licensed** - Maximum adoption, no restrictions
6. **GitHub releases** - Easy download with release notes
7. **Consistent CLI patterns** - Similar flags and conventions across tools
8. **Claude Code skills** - Downloadable skill definitions for each tool

### Repository Structure

**Monorepo:** `github.com/CenterConsulting/cc-tools`

```
cc-tools/
    README.md                    # Overview of all tools
    LICENSE                      # MIT
    src/
        cc-markdown/             # Best language for the job
        cc-transcribe/
        cc-image/                # Unified image toolkit
        cc-voice/
        cc-whisper/
        cc-video/
    releases/                    # Compiled executables
    skills/                      # Claude Code skill definitions
    docs/
```

**Language Policy:** Use the best language for each tool (Python, TypeScript, C#). All tools compile to single executables.

---

## Success Metrics

### Awareness Goals (Year 1)

| Metric | Target |
|--------|--------|
| GitHub stars (total across tools) | 5,000 |
| Total downloads | 50,000 |
| Social media impressions | 500,000 |
| Backlinks/mentions | 100 |

### Quality Goals

| Metric | Target |
|--------|--------|
| Critical bugs | 0 |
| Average issue response time | < 48 hours |
| Documentation completeness | 100% |

### Business Goals

| Metric | Target |
|--------|--------|
| Inbound leads mentioning CC tools | Track and measure |
| Brand recognition in AI/dev community | Qualitative feedback |

---

## Decisions Made

1. **Repository name:** cc-tools
2. **Naming pattern:** cc-[function]
3. **Monorepo:** Yes, single repo for all tools
4. **Language policy:** Best fit per tool (not restricted to one language)
5. **License:** MIT
6. **Distribution:** GitHub releases + Claude Code skills

## Open Questions

1. **API keys** - Tools currently have keys baked in. For open source, users provide their own keys via environment variables or config file?
2. **Branding assets** - Do we need logos for each tool or just the CC brand?
3. **Documentation site** - Single site for all tools (cc-tools.centerconsulting.com) or per-tool READMEs?
4. **Community** - Discord/Slack for users? Or just GitHub issues?

---

## Next Steps

1. [x] Finalize tool naming (cc-[function] pattern) - DONE
2. [x] Decide monorepo vs separate repos - DONE (monorepo)
3. [x] Choose repository name - DONE (cc-tools)
4. [x] Create GitHub repository - DONE
5. [ ] Set up repository structure
6. [ ] Create cc-markdown as first release
7. [ ] Create release pipeline (GitHub Actions)
8. [ ] Plan social media campaign for first release

---

*Document Version: 1.1*
*Last Updated: 2026-02-12*
*Author: CenterConsulting Strategy Team*
