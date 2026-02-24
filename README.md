# CC Tools

Open source CLI tools for agentic coding workflows. Download. Run. Done.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/CenterConsulting/cc-tools/workflows/Build/badge.svg)](https://github.com/CenterConsulting/cc-tools/actions)
[![Tests: 150 Passed](https://img.shields.io/badge/Tests-150%20Passed-brightgreen)](docs/TESTING.md)

---

## Quick Install

### Windows (Recommended)

Download and run the setup executable:

1. Download **[cc-tools-setup-windows-x64.exe](../../releases/latest)** from GitHub Releases
2. Double-click to run
3. Restart your terminal

The setup will:
- Download all available cc-tools to `%LOCALAPPDATA%\cc-tools\`
- Add to your PATH
- Install SKILL.md for Claude Code integration

### Alternative: Individual Downloads

Download specific tools from [GitHub Releases](../../releases):
- `cc-markdown-windows-x64.exe`
- `cc-transcribe-windows-x64.exe`
- *(more coming soon)*

Place in any directory in your PATH.

---

## What is CC Tools?

CC Tools is a suite of command-line utilities designed for AI-assisted development workflows. Each tool is a single executable - no installation, no dependencies, just download and run.

Built by [CenterConsulting Inc.](https://www.centerconsulting.com) and released under the MIT license.

---

## Tools

| Tool | Description | Status |
|------|-------------|--------|
| **cc-markdown** | Markdown to PDF/Word/HTML with themes | Available |
| **cc-transcribe** | Video/audio transcription with timestamps | In Development |
| **cc-image** | Image toolkit: generate, analyze, OCR, resize, convert | Coming Soon |
| **cc-voice** | Text-to-speech | Coming Soon |
| **cc-whisper** | Audio transcription | Coming Soon |
| **cc-video** | Video utilities | Coming Soon |

---

## Quick Start

### cc-markdown

Convert Markdown to beautifully styled documents:

```bash
# PDF with corporate theme
cc-markdown report.md -o report.pdf --theme boardroom

# Word document
cc-markdown report.md -o report.docx --theme paper

# HTML
cc-markdown report.md -o report.html

# Custom CSS
cc-markdown report.md -o report.pdf --css custom.css

# List themes
cc-markdown --themes
```

**Built-in Themes:**
- **boardroom** - Corporate, executive
- **terminal** - Technical, monospace
- **paper** - Minimal, elegant
- **spark** - Creative, colorful
- **thesis** - Academic, scholarly
- **obsidian** - Dark theme
- **blueprint** - Technical docs

### cc-transcribe

Transcribe video/audio with timestamps and screenshots:

```bash
# Basic transcription
cc-transcribe video.mp4

# Specify output directory
cc-transcribe video.mp4 -o ./output/

# Without screenshots
cc-transcribe video.mp4 --no-screenshots
```

Requires FFmpeg and `OPENAI_API_KEY` environment variable.

---

## Installation Details

### What Gets Installed

| File | Location | Purpose |
|------|----------|---------|
| `cc-*.exe` | `%LOCALAPPDATA%\cc-tools\` | The CLI tools |
| `SKILL.md` | `~/.claude/skills/cc-tools/` | Claude Code integration |

### Updating

Run `cc-tools-setup.exe` again to download the latest versions.

### Build from Source

```bash
# Clone the repo
git clone https://github.com/CenterConsulting/cc-tools.git
cd cc-tools

# Build all tools
scripts\build-all.bat

# Or build individual tools
scripts\build-setup.bat
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed build instructions.

---

## Why CC Tools?

**For Agentic Workflows:** Simple CLI interfaces that AI coding assistants can call directly.

**MIT Licensed:** Use anywhere - personal, commercial, no restrictions.

**Single Executables:** No runtime dependencies. Download and run.

**Modular:** Each tool is independent. Download only what you need.

---

## Test Status

All tools are thoroughly tested with 150 automated tests:

| Tool | Unit Tests | Integration | Status |
|------|------------|-------------|--------|
| cc-markdown | 13 | 12 | PASS |
| cc-transcribe | 33 | - | PASS |
| cc-image | 38 | - | PASS |
| cc-voice | 21 | - | PASS |
| cc-whisper | 9 | - | PASS |
| cc-video | 24 | - | PASS |

See [Testing Documentation](docs/TESTING.md) for details.

### Running Tests

```bash
# Run all unit tests for a tool
cd src/cc-markdown
python -m pytest tests/ -v

# Run integration tests
python -m pytest tests/integration/ -v
```

---

## Claude Code Integration

CC Tools are designed to work seamlessly with Claude Code and other AI coding assistants.

### Automatic Setup

The installer automatically installs `SKILL.md` to `~/.claude/skills/cc-tools/`, enabling Claude Code to use these tools directly.

### MCP Server Tools

CC Tools includes MCP server tools for direct integration:

| MCP Tool | Function |
|----------|----------|
| `fred_markdown_to_pdf` | Convert markdown to PDF |
| `fred_markdown_to_word` | Convert markdown to Word |
| `fred_transcribe_video` | Transcribe video with timestamps |
| `fred_tts` | Text-to-speech (OpenAI) |
| `fred_whisper` | Speech-to-text (OpenAI) |
| `fred_image_gen` | Generate images (DALL-E) |
| `fred_vision_describe` | Describe images (GPT-4V) |
| `fred_vision_extract_text` | OCR from images (GPT-4V) |
| `fred_llm` | Call OpenAI models |
| `fred_embed` | Generate embeddings |

### Example: Claude Code Usage

```
User: Convert my report.md to a PDF with the boardroom theme
Claude: [Uses cc-markdown tool to convert report.md to report.pdf with boardroom theme]

User: Transcribe this video and extract key screenshots
Claude: [Uses fred_transcribe_video to transcribe with timestamp extraction]
```

---

## Documentation

- [Testing Documentation](docs/TESTING.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Strategy Document](docs/CC_Tools_Strategy.md)
- [cc-markdown PRD](docs/cc-markdown_PRD.md)
- [Handover Document](docs/HANDOVER.md)

---

## Requirements

Some tools require an OpenAI API key for AI features:

```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/macOS
export OPENAI_API_KEY=your-key-here
```

Note: Some features (like cc-markdown) work without an API key.

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE)

---

## About

Built by [CenterConsulting Inc.](https://www.centerconsulting.com)

We build AI-powered tools for process mining, document automation, and business intelligence.
