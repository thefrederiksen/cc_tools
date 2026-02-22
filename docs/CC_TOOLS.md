# CC Tools Reference

Command-line tools for document conversion, media processing, email, and AI workflows.

**Install location:** `C:\cc_tools\`

---

## Quick Reference

| Tool | Description | Requirements |
|------|-------------|--------------|
| cc_browser | Persistent browser automation with profiles | Node.js, Playwright |
| cc_click | Windows UI automation (click, type, inspect) | Windows, .NET |
| cc_comm_queue | Communication Manager queue CLI | None |
| cc_crawl4ai | AI-ready web crawler to clean markdown | Playwright browsers |
| cc_gmail | Gmail CLI: read, send, search emails | Google OAuth |
| cc_hardware | System hardware info (RAM, CPU, GPU, disk) | None (NVIDIA for GPU) |
| cc_image | Image generation/analysis/OCR | OpenAI API key |
| cc_linkedin | LinkedIn automation | Playwright browsers |
| cc_markdown | Markdown to PDF/Word/HTML | Chrome/Chromium |
| cc_outlook | Outlook CLI: email + calendar | Azure OAuth |
| cc_photos | Photo organization: duplicates, screenshots, AI | OpenAI API key |
| cc_reddit | Reddit automation | Playwright browsers |
| cc_transcribe | Video/audio transcription with screenshots | FFmpeg, OpenAI API key |
| cc_trisight | Windows screen detection and automation | Windows, .NET |
| cc_video | Video utilities | FFmpeg |
| cc_voice | Text-to-speech | OpenAI API key |
| cc_whisper | Audio transcription | OpenAI API key |
| cc_youtube_info | YouTube transcript/metadata extraction | None |

---

## cc_markdown

Convert Markdown to PDF, Word, or HTML with built-in themes.

```bash
# Convert to PDF
cc_markdown report.md -o report.pdf

# Use a theme
cc_markdown report.md -o report.pdf --theme boardroom

# Convert to Word
cc_markdown report.md -o report.docx

# Convert to HTML
cc_markdown report.md -o report.html

# List themes
cc_markdown --themes
```

**Themes:** boardroom, terminal, paper, spark, thesis, obsidian, blueprint

**Options:**
- `-o, --output` - Output file (format from extension)
- `--theme` - Theme name
- `--css` - Custom CSS file
- `--page-size` - a4 or letter (default: a4)
- `--margin` - Page margin (default: 1in)

---

## cc_transcribe

Transcribe video/audio with timestamps and extract screenshots at content changes.

```bash
# Basic transcription
cc_transcribe video.mp4

# Specify output directory
cc_transcribe video.mp4 -o ./output/

# Without screenshots
cc_transcribe video.mp4 --no-screenshots

# More frequent screenshots (lower threshold)
cc_transcribe video.mp4 --threshold 0.85

# Get video info only
cc_transcribe video.mp4 --info
```

**Output:** transcript.txt, transcript.json, screenshots/

**Options:**
- `-o, --output` - Output directory
- `--no-screenshots` - Skip screenshot extraction
- `--threshold` - SSIM 0.0-1.0 (default: 0.92, lower = more screenshots)
- `--interval` - Min seconds between screenshots (default: 1.0)
- `--language` - Force language code (e.g., en, es, fr)

---

## cc_gmail

Gmail CLI with multi-account support.

```bash
# Setup
cc_gmail accounts add personal --default
cc_gmail auth

# List inbox
cc_gmail list
cc_gmail list --unread
cc_gmail list -l SENT

# Read email
cc_gmail read <message_id>

# Send email
cc_gmail send -t "to@example.com" -s "Subject" -b "Body text"
cc_gmail send -t "to@example.com" -s "Subject" -f body.txt
cc_gmail send -t "to@example.com" -s "Subject" -b "See attached" -a file.pdf

# Search
cc_gmail search "from:someone@example.com"
cc_gmail search "subject:important is:unread"

# Draft
cc_gmail draft -t "to@example.com" -s "Subject" -b "Draft body"

# Profile
cc_gmail profile

# Use specific account
cc_gmail -a work list
```

**Search syntax:** `from:`, `to:`, `subject:`, `is:unread`, `has:attachment`, `after:YYYY/MM/DD`, `before:YYYY/MM/DD`

---

## cc_hardware

Query system hardware information: RAM, CPU, GPU, disk, OS, network, battery.

```bash
# Show all hardware info
cc_hardware

# Individual components
cc_hardware ram
cc_hardware cpu
cc_hardware gpu
cc_hardware disk
cc_hardware os
cc_hardware network
cc_hardware battery

# JSON output (for scripting)
cc_hardware --json
cc_hardware cpu --json

# Version
cc_hardware --version
```

**Commands:**
- `cc_hardware` - Show all hardware summary
- `cc_hardware ram` - RAM total/used/available
- `cc_hardware cpu` - CPU model, cores, usage
- `cc_hardware gpu` - NVIDIA GPU memory/load/temp
- `cc_hardware disk` - Per-drive storage info
- `cc_hardware os` - OS name, version, architecture
- `cc_hardware network` - Network interfaces and IPs
- `cc_hardware battery` - Battery charge and status

**Options:**
- `--json, -j` - Output as JSON
- `--version, -v` - Show version

**Notes:**
- GPU info requires NVIDIA GPU with drivers installed
- Battery info only available on laptops

---

## cc_outlook

Outlook CLI with email and calendar support.

```bash
# Setup
cc_outlook accounts add your@email.com --client-id YOUR_CLIENT_ID
cc_outlook auth

# List inbox
cc_outlook list
cc_outlook list --unread
cc_outlook list -f sent

# Read email
cc_outlook read <message_id>

# Send email
cc_outlook send -t "to@example.com" -s "Subject" -b "Body text"
cc_outlook send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf

# Search
cc_outlook search "project update"

# Calendar
cc_outlook calendar events          # Next 7 days
cc_outlook calendar events -d 14    # Next 14 days
cc_outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00

# Profile
cc_outlook profile
```

---

## cc_youtube_info

Extract transcripts, metadata, and chapters from YouTube videos.

```bash
# Get video metadata
cc_youtube_info info "https://www.youtube.com/watch?v=VIDEO_ID"

# Download transcript
cc_youtube_info transcript URL
cc_youtube_info transcript URL -o transcript.txt

# Download as SRT subtitles
cc_youtube_info transcript URL --format srt -o captions.srt

# List available languages
cc_youtube_info languages URL

# Get chapters
cc_youtube_info chapters URL

# Output as JSON
cc_youtube_info info URL --json
```

**Options:**
- `-o, --output` - Output file
- `-l, --lang` - Language code (default: en)
- `-f, --format` - txt, srt, or vtt
- `--json` - Output as JSON
- `--no-timestamps` - Remove timestamps

---

## cc_crawl4ai

AI-ready web crawler: crawl pages to clean markdown for LLM/RAG workflows.

```bash
# Crawl a URL
cc_crawl4ai crawl "https://example.com"
cc_crawl4ai crawl URL -o page.md

# Fit markdown (noise filtered)
cc_crawl4ai crawl URL --fit

# Batch crawl from file
cc_crawl4ai batch urls.txt -o ./output/

# Stealth mode (evade bot detection)
cc_crawl4ai crawl URL --stealth

# Wait for dynamic content
cc_crawl4ai crawl URL --wait-for ".content-loaded"

# Scroll full page (infinite scroll)
cc_crawl4ai crawl URL --scroll

# Extract specific CSS selector
cc_crawl4ai crawl URL --css "article.main"

# Take screenshot
cc_crawl4ai crawl URL --screenshot

# Authenticated sessions
cc_crawl4ai session create mysite -u "https://example.com/login" --interactive
cc_crawl4ai crawl URL --session mysite
```

---

## cc_browser

Persistent browser automation with profile management.

```bash
# Launch browser with profile
cc_browser launch --profile myprofile

# Navigate
cc_browser navigate "https://example.com"

# Take screenshot
cc_browser screenshot -o page.png

# Execute JavaScript
cc_browser eval "document.title"

# Close browser
cc_browser close
```

**Note:** Runs as a daemon for persistent browser sessions across commands.

---

## cc_photos

Photo organization tool: scan directories, detect duplicates and screenshots, AI descriptions.

```bash
# Add a source directory
cc_photos source add "D:\Photos" --category private --label "Family" --priority 1

# List sources
cc_photos source list

# Remove a source
cc_photos source remove "Family"

# Scan all sources
cc_photos scan

# Scan specific source
cc_photos scan --source "Family"

# Find duplicates
cc_photos dupes

# Auto-remove duplicates (keeps highest priority)
cc_photos dupes --cleanup

# Interactive duplicate review
cc_photos dupes --review

# List by category
cc_photos list --category private

# List screenshots
cc_photos list --screenshots

# AI analysis (generate descriptions)
cc_photos analyze
cc_photos analyze --limit 50
cc_photos analyze --provider openai

# Search descriptions
cc_photos search "beach vacation"

# Statistics
cc_photos stats
```

**Categories:** private, work, other

**Priority:** Lower number = higher priority (keeps that copy when removing duplicates)

**Config:** `~/.cc_tools/config.json`

**Database:** `~/.cc_tools/photos.db` (configurable)

---

## cc_click

Windows UI automation for clicking, typing, and inspecting elements.

```bash
# Click at coordinates
cc_click click 100 200

# Type text
cc_click type "Hello World"

# Inspect element at position
cc_click inspect 100 200

# List windows
cc_click windows

# Focus window by title
cc_click focus "Notepad"
```

---

## cc_comm_queue

CLI tool for adding content to the Communication Manager approval queue.

```bash
# Add LinkedIn post
cc_comm_queue add linkedin post "Process mining trends for 2024..." \
    --persona mindzie \
    --tags "process mining,trends"

# Add LinkedIn comment
cc_comm_queue add linkedin comment "Great insights!" \
    --persona personal \
    --context-url "https://linkedin.com/posts/..."

# Add email
cc_comm_queue add email email "Hi Sarah, following up..." \
    --persona mindzie \
    --email-to "sarah@techcorp.com" \
    --email-subject "Following up from Summit"

# Add Reddit post
cc_comm_queue add reddit post "How we reduced processing time..." \
    --persona personal \
    --reddit-subreddit "r/processimprovement" \
    --reddit-title "Case Study: 70% reduction"

# Add from JSON file
cc_comm_queue add-json content.json

# Add from stdin
cat content.json | cc_comm_queue add-json -

# List pending items
cc_comm_queue list --status pending

# Show queue stats
cc_comm_queue status

# Show specific item
cc_comm_queue show abc123

# JSON output (for agents)
cc_comm_queue add linkedin post "Hello" --json

# Configuration
cc_comm_queue config show
cc_comm_queue config set queue_path "D:/path/to/content"
cc_comm_queue config set default_persona mindzie
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

**Config:** `~/.cc_tools/config.json` (comm_manager section)

---

## cc_image

Image generation and analysis using OpenAI.

```bash
# Generate image from prompt
cc_image generate "A sunset over mountains" -o sunset.png

# Analyze/describe image
cc_image describe image.png

# OCR - extract text from image
cc_image ocr screenshot.png
```

---

## cc_voice

Text-to-speech using OpenAI TTS.

```bash
# Convert text to speech
cc_voice speak "Hello, world!" -o hello.mp3

# Use different voice
cc_voice speak "Hello" -o hello.mp3 --voice nova
```

**Voices:** alloy, echo, fable, nova, onyx, shimmer

---

## cc_whisper

Audio transcription using OpenAI Whisper.

```bash
# Transcribe audio
cc_whisper transcribe audio.mp3
cc_whisper transcribe audio.mp3 -o transcript.txt
```

---

## cc_video

Video utilities.

```bash
# Extract audio from video
cc_video extract-audio video.mp4 -o audio.mp3

# Get video info
cc_video info video.mp4
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
| cc_browser | Node.js, Playwright |
| cc_click | Windows, .NET runtime |
| cc_comm_queue | None |
| cc_crawl4ai | `playwright install chromium` |
| cc_gmail | OAuth credentials from Google Cloud Console |
| cc_hardware | None (NVIDIA drivers for GPU info) |
| cc_image | OPENAI_API_KEY |
| cc_markdown | Chrome/Chromium (auto-detected) |
| cc_outlook | Azure App Registration with OAuth |
| cc_photos | OPENAI_API_KEY (for AI analysis) |
| cc_transcribe | FFmpeg in PATH, OPENAI_API_KEY |
| cc_trisight | Windows, .NET runtime |
| cc_video | FFmpeg in PATH |
| cc_voice | OPENAI_API_KEY |
| cc_whisper | OPENAI_API_KEY |
| cc_youtube_info | None |

---

## Source Repository

GitHub: https://github.com/CenterConsulting/cc_tools
