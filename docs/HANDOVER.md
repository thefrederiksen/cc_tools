# CC Tools - Handover Document

This document captures the full context of the cc-tools project for anyone continuing this work.

---

## Project Overview

**What:** A suite of open source CLI tools for agentic coding workflows, branded under CenterConsulting (CC).

**Why:**
1. Open source valuable internal tools to build brand recognition
2. Fill gaps in the market (e.g., MIT-licensed Pandoc alternative)
3. Create content opportunities for social media campaigns
4. Support the growing agentic coding ecosystem (Claude Code, Cursor, etc.)

**Repository:** github.com/CenterConsulting/cc-tools

---

## Origin Story

These tools originated from `fred_tools` (D:\ReposFred\fred_tools), an internal Python library used by CenterConsulting for AI-powered workflows. The library wraps OpenAI APIs and provides utilities for:

- LLM calls
- Text-to-speech
- Audio transcription (Whisper)
- Video transcription with screenshot extraction
- Image generation (DALL-E)
- Vision/OCR (GPT-4 Vision)
- Text embeddings
- Document conversion (Markdown to PDF/Word)

The decision was made to rebrand and open source these tools to:
1. Give back to the developer community
2. Build CenterConsulting's reputation
3. Create marketing content through tool releases

---

## Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Repository name | `cc-tools` | Short, memorable, brand-forward |
| Tool naming | `cc_[function]` | Consistent, clear, branded |
| Repo structure | Monorepo | Easier management, shared docs |
| License | MIT | Maximum adoption, no GPL restrictions |
| Language policy | Best fit per tool | Python, TypeScript, C# all acceptable |
| First tool | cc-markdown | Strongest differentiator vs Pandoc |

---

## The Tools

### Planned Tools (6 total)

| Tool | Function | Source in fred_tools | Priority |
|------|----------|---------------------|----------|
| **cc-markdown** | Markdown to PDF/Word/HTML | `document/` | 1 - Lead |
| **cc-transcribe** | Video/audio transcription | `stt/transcribe_video` | 2 - Lead |
| **cc-image** | Image toolkit: generate, analyze, OCR, resize, convert | `vision/` + `image_gen/` + `image/` | 3 - Lead |
| **cc-voice** | Text-to-speech | `tts/` | 4 |
| **cc-whisper** | Audio transcription | `stt/whisper` | 5 |
| **cc-video** | Video utilities | `video/` | 6 |

### cc-markdown Details

This is the first tool to build. Full PRD is in `docs/cc-markdown_PRD.md`.

**Key features:**
- Markdown to PDF, Word, HTML
- CSS-based styling (works for all formats, including Word)
- 7 built-in themes: Boardroom, Terminal, Paper, Spark, Thesis, Obsidian, Blueprint
- Custom CSS via `--css` flag
- Single executable, cross-platform

**Competitive advantage over Pandoc:**
- MIT license (Pandoc is GPL)
- CSS styling for Word (Pandoc requires template docs)
- Built-in themes (Pandoc has none)
- Simpler CLI (Pandoc is complex)

**CLI interface:**
```bash
cc-markdown input.md -o output.pdf --theme Boardroom
cc-markdown input.md -o output.docx
cc-markdown input.md -o output.html --css custom.css
cc-markdown --themes
cc-markdown --help
```

### cc-image Details

Unified image toolkit combining AI capabilities with local processing.

**Subcommands:**
| Command | Function | API Required |
|---------|----------|--------------|
| `generate` | Create images with DALL-E | Yes (OpenAI) |
| `describe` | Analyze/describe image content | Yes (OpenAI) |
| `classify` | Classify image into categories | Yes (OpenAI) |
| `extract-text` | OCR - extract text from image | Yes (OpenAI) |
| `resize` | Resize with quality preservation | No |
| `convert` | Convert between formats (PNG/JPG/WEBP) | No |
| `info` | Get image metadata | No |

**CLI interface:**
```bash
cc-image generate "A sunset over mountains" -o sunset.png
cc-image describe photo.jpg
cc-image classify photo.jpg --categories "cat,dog,bird"
cc-image extract-text screenshot.png
cc-image resize photo.png -o thumb.jpg --width 800
cc-image convert photo.png -o photo.webp
cc-image info photo.png
```

**Source modules:** `vision/`, `image_gen/`, `image/`

---

## Technical Architecture

### Conversion Pipeline (cc-markdown)

```
Markdown --> HTML (with CSS) --> Output
                                   |
                                   +--> PDF (headless browser)
                                   +--> Word (Open XML)
                                   +--> HTML (standalone)
```

### Language Choices

No single language is mandated. Choose based on:

| Language | Good For | Executable Method |
|----------|----------|-------------------|
| C# | Document processing, Windows-native | dotnet publish single-file |
| Python | AI/ML, rapid prototyping | PyInstaller, Nuitka |
| TypeScript | Web-related tools | pkg, Bun compile |

### Existing Code Reference

The `fred_tools` library at `D:\ReposFred\fred_tools` contains working implementations:

- `src/fred_tools/document/` - Markdown to PDF/Word (cc-markdown)
- `src/fred_tools/stt/` - Whisper + video transcription (cc-transcribe, cc-whisper)
- `src/fred_tools/vision/` - GPT-4 Vision analysis and OCR (cc-image)
- `src/fred_tools/image_gen/` - DALL-E generation (cc-image)
- `src/fred_tools/image/` - Image manipulation/resize (cc-image)
- `src/fred_tools/tts/` - Text-to-speech (cc-voice)
- `src/fred_tools/video/` - Video utilities (cc-video)
- `src/fred_tools/mcp_server.py` - MCP server exposing all tools

---

## Repository Structure

```
cc-tools/
    README.md                    # Overview, quick start, tool list
    LICENSE                      # MIT license
    CONTRIBUTING.md              # How to contribute (future)
    src/
        cc-markdown/
            README.md            # Tool-specific docs
            src/                 # Source code
            themes/              # CSS theme files
        cc-transcribe/
        cc-image/                # Unified: generate, analyze, OCR, resize, convert
        cc-voice/
        cc-whisper/
        cc-video/
    releases/                    # Compiled executables (gitignored, in GitHub Releases)
    skills/                      # Claude Code skill definitions
    docs/
        CC_Tools_Strategy.md     # Strategy document
        cc-markdown_PRD.md       # cc-markdown requirements
        HANDOVER.md              # This document
```

---

## Claude Code Integration

Each tool should have:

1. **CLI executable** - Download and run
2. **Claude Code skill** - YAML/JSON skill definition in `skills/`

The existing `fred_tools/mcp_server.py` shows how these tools are exposed as MCP tools. Similar patterns can be used for Claude Code skills.

---

## Marketing Strategy

### Launch Order

1. cc-markdown (strongest differentiator)
2. cc-transcribe (unique video+transcript combo)
3. cc-image (unified image toolkit)
4. cc-voice, cc-whisper
5. cc-video

### Content Per Release

- Announcement post (LinkedIn, Twitter/X)
- Demo video (60 seconds)
- Use case thread
- Comparison post (e.g., vs Pandoc)

### Success Metrics (Year 1)

- 5,000 GitHub stars
- 50,000 downloads
- 500,000 social impressions

---

## Open Questions (Need Decisions)

1. **API Keys:** fred_tools has keys baked in. For open source, users need to provide their own. Options:
   - Environment variables (OPENAI_API_KEY)
   - Config file (~/.cc-tools/config)
   - CLI flag (--api-key)

   **Recommendation:** Environment variables (standard practice)

2. **Branding:** Do we need logos?
   - Tool-specific logos
   - Just the CC brand

   **Recommendation:** CC brand only, simple text marks for tools

3. **Documentation Site:**
   - Single site (cc-tools.centerconsulting.com)
   - Per-tool READMEs

   **Recommendation:** Start with READMEs, add site if traction warrants

4. **Community:**
   - Discord/Slack
   - GitHub Issues only

   **Recommendation:** GitHub Issues only initially

---

## Immediate Next Steps

1. [ ] Create folder structure in cc-tools repo
2. [ ] Add README.md with tool overview
3. [ ] Add MIT LICENSE
4. [ ] Start cc-markdown implementation
5. [ ] Set up GitHub Actions for releases
6. [ ] Create first Claude Code skill definition

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `docs/CC_Tools_Strategy.md` | Full strategy document |
| `docs/cc-markdown_PRD.md` | cc-markdown requirements |
| `docs/HANDOVER.md` | This document |
| `D:\ReposFred\fred_tools\` | Original source code |
| `D:\ReposFred\fred_tools\src\fred_tools\mcp_server.py` | MCP server reference |

---

## Contact

**Company:** CenterConsulting Inc.
**Website:** www.centerconsulting.com
**Repository:** github.com/CenterConsulting/cc-tools

---

*Document Version: 1.0*
*Created: 2026-02-12*
*Purpose: Full context handover for cc-tools project*
