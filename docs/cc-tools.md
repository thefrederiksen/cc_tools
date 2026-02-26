# CC Tools Reference

Command-line tools for document conversion, media processing, email, and AI workflows.

**Install location:** `C:\cc-tools\`

---

## Quick Reference

| Tool | Description | Requirements |
|------|-------------|--------------|
| cc-browser | Persistent browser automation with profiles | Node.js, Playwright |
| cc-click | Windows UI automation (click, type, inspect) | Windows, .NET |
| cc-comm-queue | Communication Manager queue CLI | None |
| cc-computer | AI desktop automation agent with TriSight detection | Windows, .NET, OPENAI_API_KEY |
| cc-crawl4ai | AI-ready web crawler to clean markdown | Playwright browsers |
| cc-gmail | Gmail CLI: read, send, search emails | Google OAuth |
| cc-hardware | System hardware info (RAM, CPU, GPU, disk) | None (NVIDIA for GPU) |
| cc-image | Image generation/analysis/OCR | OpenAI API key |
| cc-linkedin | LinkedIn automation | Playwright browsers |
| cc-markdown | Markdown to PDF/Word/HTML | Chrome/Chromium |
| cc-outlook | Outlook CLI: email + calendar | Azure OAuth |
| cc-photos | Photo organization: duplicates, screenshots, AI | OpenAI API key |
| cc-reddit | Reddit automation | Playwright browsers |
| cc-transcribe | Video/audio transcription with screenshots | FFmpeg, OpenAI API key |
| cc-trisight | Windows screen detection and automation | Windows, .NET |
| cc-video | Video utilities | FFmpeg |
| cc-voice | Text-to-speech | OpenAI API key |
| cc-whisper | Audio transcription | OpenAI API key |
| cc-youtube-info | YouTube transcript/metadata extraction | None |

---

## Desktop Automation Stack

Three tools work together to provide AI-powered desktop automation:

```
cc-computer (AI Agent - the "brain")
    |-- Decides what to do next based on screen state
    |-- LLM-powered (GPT via Semantic Kernel)
    |-- Screenshot-in-the-loop verification
    |-- Evidence chain logging for audit
    |
    +-- uses TrisightCore (shared detection library)
    |       |-- 3-tier detection: UI Automation + OCR + Pixel Analysis
    |       +-- 98.9% element clickability accuracy
    |
    +-- calls cc-click for actions

cc-trisight (Detection CLI - the "eyes")
    |-- Standalone tool for UI element detection
    |-- Takes screenshot, returns element list with coordinates
    |-- Outputs annotated screenshots with bounding boxes
    +-- uses TrisightCore (same shared library)

cc-click (Automation CLI - the "hands")
    |-- Click at coordinates
    |-- Type text, send keystrokes
    |-- List windows, focus windows
    +-- Low-level Windows UI automation
```

**When to use which:**
- `cc-click` - Direct automation when you know exactly what to click/type
- `cc-trisight` - Inspect UI elements, get coordinates for scripting
- `cc-computer` - Natural language tasks: "Open Notepad and save a file called test.txt"

---

## cc-markdown

Convert Markdown to PDF, Word, or HTML with built-in themes.

```bash
# Convert to PDF
cc-markdown report.md -o report.pdf

# Use a theme
cc-markdown report.md -o report.pdf --theme boardroom

# Convert to Word
cc-markdown report.md -o report.docx

# Convert to HTML
cc-markdown report.md -o report.html

# List themes
cc-markdown --themes
```

**Themes:** boardroom, terminal, paper, spark, thesis, obsidian, blueprint

**Options:**
- `-o, --output` - Output file (format from extension)
- `--theme` - Theme name
- `--css` - Custom CSS file
- `--page-size` - a4 or letter (default: a4)
- `--margin` - Page margin (default: 1in)

---

## cc-transcribe

Transcribe video/audio with timestamps and extract screenshots at content changes.

```bash
# Basic transcription
cc-transcribe video.mp4

# Specify output directory
cc-transcribe video.mp4 -o ./output/

# Without screenshots
cc-transcribe video.mp4 --no-screenshots

# More frequent screenshots (lower threshold)
cc-transcribe video.mp4 --threshold 0.85

# Get video info only
cc-transcribe video.mp4 --info
```

**Output:** transcript.txt, transcript.json, screenshots/

**Options:**
- `-o, --output` - Output directory
- `--no-screenshots` - Skip screenshot extraction
- `--threshold` - SSIM 0.0-1.0 (default: 0.92, lower = more screenshots)
- `--interval` - Min seconds between screenshots (default: 1.0)
- `--language` - Force language code (e.g., en, es, fr)

---

## cc-gmail

Gmail CLI with multi-account support.

```bash
# Setup
cc-gmail accounts add personal --default
cc-gmail auth

# List inbox
cc-gmail list
cc-gmail list --unread
cc-gmail list -l SENT

# Read email
cc-gmail read <message_id>

# Send email
cc-gmail send -t "to@example.com" -s "Subject" -b "Body text"
cc-gmail send -t "to@example.com" -s "Subject" -f body.txt
cc-gmail send -t "to@example.com" -s "Subject" -b "See attached" -a file.pdf

# Search
cc-gmail search "from:someone@example.com"
cc-gmail search "subject:important is:unread"

# Draft
cc-gmail draft -t "to@example.com" -s "Subject" -b "Draft body"

# Profile
cc-gmail profile

# Use specific account
cc-gmail -a work list
```

**Search syntax:** `from:`, `to:`, `subject:`, `is:unread`, `has:attachment`, `after:YYYY/MM/DD`, `before:YYYY/MM/DD`

---

## cc-hardware

Query system hardware information: RAM, CPU, GPU, disk, OS, network, battery.

```bash
# Show all hardware info
cc-hardware

# Individual components
cc-hardware ram
cc-hardware cpu
cc-hardware gpu
cc-hardware disk
cc-hardware os
cc-hardware network
cc-hardware battery

# JSON output (for scripting)
cc-hardware --json
cc-hardware cpu --json

# Version
cc-hardware --version
```

**Commands:**
- `cc-hardware` - Show all hardware summary
- `cc-hardware ram` - RAM total/used/available
- `cc-hardware cpu` - CPU model, cores, usage
- `cc-hardware gpu` - NVIDIA GPU memory/load/temp
- `cc-hardware disk` - Per-drive storage info
- `cc-hardware os` - OS name, version, architecture
- `cc-hardware network` - Network interfaces and IPs
- `cc-hardware battery` - Battery charge and status

**Options:**
- `--json, -j` - Output as JSON
- `--version, -v` - Show version

**Notes:**
- GPU info requires NVIDIA GPU with drivers installed
- Battery info only available on laptops

---

## cc-outlook

Outlook CLI with email and calendar support.

```bash
# Setup
cc-outlook accounts add your@email.com --client-id YOUR_CLIENT_ID
cc-outlook auth

# List inbox
cc-outlook list
cc-outlook list --unread
cc-outlook list -f sent

# Read email
cc-outlook read <message_id>

# Send email
cc-outlook send -t "to@example.com" -s "Subject" -b "Body text"
cc-outlook send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf

# Search
cc-outlook search "project update"

# Calendar
cc-outlook calendar events          # Next 7 days
cc-outlook calendar events -d 14    # Next 14 days
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00

# Profile
cc-outlook profile
```

---

## cc-youtube-info

Extract transcripts, metadata, and chapters from YouTube videos.

```bash
# Get video metadata
cc-youtube-info info "https://www.youtube.com/watch?v=VIDEO_ID"

# Download transcript
cc-youtube-info transcript URL
cc-youtube-info transcript URL -o transcript.txt

# Download as SRT subtitles
cc-youtube-info transcript URL --format srt -o captions.srt

# List available languages
cc-youtube-info languages URL

# Get chapters
cc-youtube-info chapters URL

# Output as JSON
cc-youtube-info info URL --json
```

**Options:**
- `-o, --output` - Output file
- `-l, --lang` - Language code (default: en)
- `-f, --format` - txt, srt, or vtt
- `--json` - Output as JSON
- `--no-timestamps` - Remove timestamps

---

## cc-crawl4ai

AI-ready web crawler: crawl pages to clean markdown for LLM/RAG workflows.

```bash
# Crawl a URL
cc-crawl4ai crawl "https://example.com"
cc-crawl4ai crawl URL -o page.md

# Fit markdown (noise filtered)
cc-crawl4ai crawl URL --fit

# Batch crawl from file
cc-crawl4ai batch urls.txt -o ./output/

# Stealth mode (evade bot detection)
cc-crawl4ai crawl URL --stealth

# Wait for dynamic content
cc-crawl4ai crawl URL --wait-for ".content-loaded"

# Scroll full page (infinite scroll)
cc-crawl4ai crawl URL --scroll

# Extract specific CSS selector
cc-crawl4ai crawl URL --css "article.main"

# Take screenshot
cc-crawl4ai crawl URL --screenshot

# Authenticated sessions
cc-crawl4ai session create mysite -u "https://example.com/login" --interactive
cc-crawl4ai crawl URL --session mysite
```

---

## cc-browser

Persistent browser automation with workspace management.

```bash
# Launch browser with workspace
cc-browser start --workspace myworkspace

# Navigate
cc-browser navigate "https://example.com"

# Take screenshot
cc-browser screenshot -o page.png

# Execute JavaScript
cc-browser eval "document.title"

# Close browser
cc-browser close
```

**Note:** Runs as a daemon for persistent browser sessions across commands.

---

## cc-photos

Photo organization tool: scan directories, detect duplicates and screenshots, AI descriptions.

```bash
# Add a source directory
cc-photos source add "D:\Photos" --category private --label "Family" --priority 1

# List sources
cc-photos source list

# Remove a source
cc-photos source remove "Family"

# Scan all sources
cc-photos scan

# Scan specific source
cc-photos scan --source "Family"

# Find duplicates
cc-photos dupes

# Auto-remove duplicates (keeps highest priority)
cc-photos dupes --cleanup

# Interactive duplicate review
cc-photos dupes --review

# List by category
cc-photos list --category private

# List screenshots
cc-photos list --screenshots

# AI analysis (generate descriptions)
cc-photos analyze
cc-photos analyze --limit 50
cc-photos analyze --provider openai

# Search descriptions
cc-photos search "beach vacation"

# Statistics
cc-photos stats
```

**Categories:** private, work, other

**Priority:** Lower number = higher priority (keeps that copy when removing duplicates)

**Config:** `~/.cc-tools/config.json`

**Database:** `~/.cc-tools/photos.db` (configurable)

---

## cc-click

Windows UI automation for clicking, typing, and inspecting elements.

```bash
# Click at coordinates
cc-click click 100 200

# Type text
cc-click type "Hello World"

# Inspect element at position
cc-click inspect 100 200

# List windows
cc-click windows

# Focus window by title
cc-click focus "Notepad"
```

---

## cc-comm-queue

CLI tool for adding content to the Communication Manager approval queue.

```bash
# Add LinkedIn post
cc-comm-queue add linkedin post "Process mining trends for 2024..." \
    --persona mindzie \
    --tags "process mining,trends"

# Add LinkedIn comment
cc-comm-queue add linkedin comment "Great insights!" \
    --persona personal \
    --context-url "https://linkedin.com/posts/..."

# Add email
cc-comm-queue add email email "Hi Sarah, following up..." \
    --persona mindzie \
    --email-to "sarah@techcorp.com" \
    --email-subject "Following up from Summit"

# Add Reddit post
cc-comm-queue add reddit post "How we reduced processing time..." \
    --persona personal \
    --reddit-subreddit "r/processimprovement" \
    --reddit-title "Case Study: 70% reduction"

# Add from JSON file
cc-comm-queue add-json content.json

# Add from stdin
cat content.json | cc-comm-queue add-json -

# List pending items
cc-comm-queue list --status pending

# Show queue stats
cc-comm-queue status

# Show specific item
cc-comm-queue show abc123

# JSON output (for agents)
cc-comm-queue add linkedin post "Hello" --json

# Configuration
cc-comm-queue config show
cc-comm-queue config set queue_path "D:/path/to/content"
cc-comm-queue config set default_persona mindzie
```

**Platforms:** linkedin, twitter, reddit, youtube, email, blog

**Types:** post, comment, reply, message, article, email

**Personas:**
- `mindzie` - CTO of mindzie
- `center_consulting` - President of Center Consulting
- `personal` - Soren Frederiksen

**Options:**
- `--persona, -p` - Persona to use
- `--destination, -d` - Where to post (URL)
- `--context-url, -c` - What we're responding to
- `--tags, -t` - Comma-separated tags
- `--notes, -n` - Notes for reviewer
- `--json` - JSON output for agents
- `--linkedin-visibility` - public or connections
- `--reddit-subreddit` - Target subreddit
- `--reddit-title` - Reddit post title
- `--email-to` - Recipient email
- `--email-subject` - Email subject

**Config:** `~/.cc-tools/config.json` (comm_manager section)

---

## cc-computer

AI desktop automation agent using TriSight 3-tier visual detection (98.9% element clickability).

```bash
# Run a task in CLI mode
cc-computer "Open Notepad and type Hello World"

# Interactive REPL mode
cc-computer

# Launch GUI mode
cc-computer-gui
```

**Features:**
- Screenshot-in-the-loop verification after every action
- TriSight 3-tier detection: UI Automation + OCR + Pixel Analysis
- Evidence chain logging with timestamps and screenshots
- Semantic Kernel LLM orchestration

**How it works:**
1. Takes a screenshot
2. Detects UI elements (buttons, text fields, etc.)
3. Overlays numbered bounding boxes on screenshot
4. LLM sees annotated screenshot + element list
5. LLM issues action (click, type, shortcut)
6. Agent executes action, captures new screenshot
7. Loop until task complete

**Configuration:** Edit `appsettings.json` in install directory

```json
{
  "LLM": {
    "ModelId": "gpt-5.2",
    "ApiKey": "your-key-or-set-OPENAI_API_KEY"
  },
  "Desktop": {
    "CcClickPath": "C:\\cc-tools\\cc-click\\cc-click.exe"
  }
}
```

**Dependencies:**
- cc-click (for UI automation actions)
- cc-trisight (shared detection library)

---

## cc-image

Image generation and analysis using OpenAI.

```bash
# Generate image from prompt
cc-image generate "A sunset over mountains" -o sunset.png

# Analyze/describe image
cc-image describe image.png

# OCR - extract text from image
cc-image ocr screenshot.png
```

---

## cc-voice

Text-to-speech using OpenAI TTS.

```bash
# Convert text to speech
cc-voice speak "Hello, world!" -o hello.mp3

# Use different voice
cc-voice speak "Hello" -o hello.mp3 --voice nova
```

**Voices:** alloy, echo, fable, nova, onyx, shimmer

---

## cc-whisper

Audio transcription using OpenAI Whisper.

```bash
# Transcribe audio
cc-whisper transcribe audio.mp3
cc-whisper transcribe audio.mp3 -o transcript.txt
```

---

## cc-video

Video utilities.

```bash
# Extract audio from video
cc-video extract-audio video.mp4 -o audio.mp3

# Get video info
cc-video info video.mp4
```

---

## Environment Variables

```bash
# Required for AI-powered tools
set OPENAI_API_KEY=your-key-here
```

---

## Requirements Summary

| Tool | Requirements |
|------|--------------|
| cc-browser | Node.js, Playwright |
| cc-click | Windows, .NET runtime |
| cc-comm-queue | None |
| cc-computer | Windows, .NET runtime, OPENAI_API_KEY |
| cc-crawl4ai | `playwright install chromium` |
| cc-gmail | OAuth credentials from Google Cloud Console |
| cc-hardware | None (NVIDIA drivers for GPU info) |
| cc-image | OPENAI_API_KEY |
| cc-markdown | Chrome/Chromium (auto-detected) |
| cc-outlook | Azure App Registration with OAuth |
| cc-photos | OPENAI_API_KEY (for AI analysis) |
| cc-transcribe | FFmpeg in PATH, OPENAI_API_KEY |
| cc-trisight | Windows, .NET runtime |
| cc-video | FFmpeg in PATH |
| cc-voice | OPENAI_API_KEY |
| cc-whisper | OPENAI_API_KEY |
| cc-youtube-info | None |

---

## Source Repository

GitHub: https://github.com/CenterConsulting/cc-tools
