# cc-tools

A suite of command-line tools for document conversion, media processing, and AI-powered workflows.

**GitHub:** https://github.com/CenterConsulting/cc-tools

---

## Available Tools

| Tool | Description | Status |
|------|-------------|--------|
| cc-crawl4ai | AI-ready web crawler | Available |
| cc-gmail | Gmail CLI: read, send, search emails | Available |
| cc-image | Image generation/analysis/OCR | Coming Soon |
| cc-markdown | Markdown to PDF/Word/HTML | Available |
| cc-outlook | Outlook CLI: read, send, search emails, calendar | Available |
| cc-transcribe | Video/audio transcription | Available |
| cc-video | Video utilities | Coming Soon |
| cc-voice | Text-to-speech | Coming Soon |
| cc-whisper | Audio transcription | Coming Soon |
| cc-youtube-info | YouTube transcript/metadata extraction | Available |

---

## cc-markdown

Convert Markdown to beautifully styled PDF, Word, and HTML documents.

### Usage

```bash
# Convert to PDF with a theme
cc-markdown report.md -o report.pdf --theme boardroom

# Convert to Word
cc-markdown report.md -o report.docx --theme paper

# Convert to HTML
cc-markdown report.md -o report.html

# Use custom CSS
cc-markdown report.md -o report.pdf --css custom.css

# List available themes
cc-markdown --themes
```

### Available Themes

- **boardroom** - Corporate, executive style
- **terminal** - Technical, monospace
- **paper** - Minimal, clean
- **spark** - Creative, colorful
- **thesis** - Academic, scholarly
- **obsidian** - Dark theme
- **blueprint** - Technical documentation

### Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path (format detected from extension) |
| `--theme` | Built-in theme name |
| `--css` | Path to custom CSS file |
| `--page-size` | Page size: a4, letter (default: a4) |
| `--margin` | Page margin (default: 1in) |
| `--themes` | List available themes |
| `--version` | Show version |
| `--help` | Show help |

### Examples

```bash
# Basic PDF
cc-markdown README.md -o README.pdf

# Corporate report
cc-markdown quarterly-report.md -o report.pdf --theme boardroom

# Technical documentation
cc-markdown api-docs.md -o api-docs.pdf --theme blueprint

# Academic paper
cc-markdown thesis.md -o thesis.pdf --theme thesis --page-size letter
```

---

## cc-transcribe

Video and audio transcription with timestamps and automatic screenshot extraction.

**Requirements:**
- FFmpeg must be installed and in PATH
- OpenAI API key: set `OPENAI_API_KEY` environment variable

### Usage

```bash
# Basic transcription
cc-transcribe video.mp4

# Specify output directory
cc-transcribe video.mp4 -o ./output/

# Without screenshots
cc-transcribe video.mp4 --no-screenshots

# Adjust screenshot sensitivity (lower = more screenshots)
cc-transcribe video.mp4 --threshold 0.85 --interval 2.0

# Force language
cc-transcribe video.mp4 --language en

# Show video info only
cc-transcribe video.mp4 --info
```

### Output Structure

```
output_directory/
    transcript.txt      # Timestamped transcript
    transcript.json     # Detailed segments with timing
    screenshots/        # Extracted frames
        screenshot_00-00-00.png
        screenshot_00-01-23.png
        ...
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory |
| `--no-screenshots` | Skip screenshot extraction |
| `--threshold` | SSIM threshold 0.0-1.0 (default: 0.92, lower = more screenshots) |
| `--interval` | Minimum seconds between screenshots (default: 1.0) |
| `--language` | Force language code (e.g., en, es, fr) |
| `--info` | Show video info and exit |
| `--help` | Show help |

### Examples

```bash
# Transcribe a meeting recording
cc-transcribe meeting.mp4 -o ./meeting-notes/

# Transcribe a tutorial with frequent screenshots
cc-transcribe tutorial.mp4 --threshold 0.85 --interval 0.5

# Quick transcription without images
cc-transcribe podcast.mp3 --no-screenshots

# Get video metadata
cc-transcribe video.mkv --info
```

---

## cc-gmail

Gmail CLI: read, send, search, and manage emails from the command line.
Supports **multiple Gmail accounts**.

**Requirements:**
- OAuth credentials from Google Cloud Console

### Setup

```bash
# 1. Add an account
cc-gmail accounts add personal

# 2. Follow setup instructions to get credentials.json from Google Cloud
# 3. Place credentials.json in ~/.cc-gmail/accounts/personal/
# 4. Authenticate
cc-gmail auth
```

See the [full README](https://github.com/CenterConsulting/cc-tools/tree/main/src/cc-gmail) for detailed Google Cloud setup steps.

### Multiple Accounts

```bash
# Add accounts
cc-gmail accounts add personal --default
cc-gmail accounts add work

# List accounts
cc-gmail accounts list

# Switch default
cc-gmail accounts default work

# Use specific account
cc-gmail --account work list
cc-gmail -a personal search "from:mom"
```

### Usage

```bash
# Authenticate
cc-gmail auth

# List inbox
cc-gmail list

# List sent messages
cc-gmail list -l SENT

# Show unread only
cc-gmail list --unread

# Read a specific email
cc-gmail read <message_id>

# Send email
cc-gmail send -t "recipient@example.com" -s "Subject" -b "Body text"

# Send with file body
cc-gmail send -t "recipient@example.com" -s "Subject" -f body.txt

# Send with attachments
cc-gmail send -t "to@example.com" -s "Subject" -b "See attached" -a file.pdf

# Create draft
cc-gmail draft -t "recipient@example.com" -s "Subject" -b "Draft body"

# Search emails
cc-gmail search "from:someone@example.com"
cc-gmail search "subject:important is:unread"

# List labels
cc-gmail labels

# Delete (move to trash)
cc-gmail delete <message_id>

# Show profile
cc-gmail profile
```

### Search Syntax

| Query | Description |
|-------|-------------|
| `from:email` | Messages from sender |
| `to:email` | Messages to recipient |
| `subject:word` | Subject contains word |
| `is:unread` | Unread messages |
| `has:attachment` | Has attachments |
| `after:YYYY/MM/DD` | After date |
| `before:YYYY/MM/DD` | Before date |

### Options

| Option | Description |
|--------|-------------|
| `-t, --to` | Recipient email |
| `-s, --subject` | Email subject |
| `-b, --body` | Email body text |
| `-f, --file` | Read body from file |
| `-l, --label` | Label/folder name |
| `-n, --count` | Number of results |
| `-a, --attach` | Attachment file |
| `--cc` | CC recipients |
| `--bcc` | BCC recipients |
| `--html` | Body is HTML |

---

## cc-outlook

Outlook CLI: read, send, search emails and manage calendar from the command line.
Supports **multiple Outlook accounts** (personal and work).

**Requirements:**
- Azure App Registration with OAuth credentials

### Setup

```bash
# 1. Create Azure App at https://portal.azure.com -> App registrations
# 2. Add redirect URIs: http://localhost AND https://login.microsoftonline.com/common/oauth2/nativeclient
# 3. Enable "Allow public client flows"
# 4. Add API permissions: Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, User.Read

# Add account with your Client ID
cc-outlook accounts add your@email.com --client-id YOUR_CLIENT_ID

# Authenticate (browser opens, copy URL back when you see "not the right page")
cc-outlook auth
```

### Usage

```bash
# List inbox
cc-outlook list

# List sent/drafts/unread
cc-outlook list -f sent
cc-outlook list --unread

# Read email
cc-outlook read <message_id>

# Send email
cc-outlook send -t "to@example.com" -s "Subject" -b "Body text"

# Send with attachments
cc-outlook send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf

# Search
cc-outlook search "project update"

# Calendar events (next 7 days)
cc-outlook calendar events

# Calendar events (next 14 days)
cc-outlook calendar events -d 14

# Create calendar event
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00

# Show profile
cc-outlook profile

# Multiple accounts
cc-outlook accounts list
cc-outlook -a work list
```

---

## cc-youtube-info

Extract transcripts, metadata, chapters, and information from YouTube videos.

### Usage

```bash
# Get video metadata
cc-youtube-info info "https://www.youtube.com/watch?v=VIDEO_ID"

# Download transcript
cc-youtube-info transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# Save transcript to file
cc-youtube-info transcript URL -o transcript.txt

# Download as SRT subtitles
cc-youtube-info transcript URL --format srt -o captions.srt

# List available languages
cc-youtube-info languages URL

# Get chapters
cc-youtube-info chapters URL

# Output as JSON
cc-youtube-info info URL --json
cc-youtube-info transcript URL --json
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `-l, --lang` | Language code (default: en) |
| `-f, --format` | Output format: txt, srt, vtt |
| `-p, --paragraphs` | Format as paragraphs (txt only) |
| `--json` | Output as JSON |
| `--auto-only` | Use only auto-generated captions |
| `--no-timestamps` | Remove timestamps (txt only) |

---

## cc-crawl4ai

AI-ready web crawler: crawl pages to clean markdown for LLM/RAG workflows.

### Usage

```bash
# Crawl a single URL
cc-crawl4ai crawl "https://example.com"

# Save to file
cc-crawl4ai crawl URL -o page.md

# Use fit markdown (noise filtered)
cc-crawl4ai crawl URL --fit

# Batch crawl from URL list
cc-crawl4ai batch urls.txt -o ./output/

# Stealth mode (evade bot detection)
cc-crawl4ai crawl URL --stealth

# Wait for dynamic content
cc-crawl4ai crawl URL --wait-for ".content-loaded"

# Scroll full page (for infinite scroll)
cc-crawl4ai crawl URL --scroll

# Extract specific CSS selector
cc-crawl4ai crawl URL --css "article.main"

# Take screenshot
cc-crawl4ai crawl URL --screenshot

# Session management (for authenticated crawling)
cc-crawl4ai session create mysite -u "https://example.com/login" --interactive
cc-crawl4ai crawl URL --session mysite
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `-f, --format` | Output format: markdown, json, html, raw |
| `--fit` | Use fit markdown (noise filtered) |
| `--stealth` | Enable stealth mode |
| `--wait-for` | CSS selector to wait for |
| `--scroll` | Scroll full page |
| `--css` | CSS selector for extraction |
| `--screenshot` | Capture screenshot |
| `-s, --session` | Use saved session |

---

## Installation

### Quick Install (Recommended)

Download and run the setup executable:

1. Download `cc-tools-setup-windows-x64.exe` from [GitHub Releases](https://github.com/CenterConsulting/cc-tools/releases)
2. Run it - it downloads tools, adds to PATH, installs this skill file
3. Restart your terminal

### Manual Install

Download individual tools from [GitHub Releases](https://github.com/CenterConsulting/cc-tools/releases):
- `cc-crawl4ai.exe`
- `cc-gmail.exe`
- `cc-markdown.exe`
- `cc-outlook.exe`
- `cc-transcribe.exe`
- `cc-youtube-info.exe`

Place in a directory in your PATH (e.g., `C:\cc-tools`).

---

## Requirements

- **cc-crawl4ai:** Playwright browsers (`playwright install chromium`)
- **cc-gmail:** OAuth credentials from Google Cloud Console
- **cc-markdown:** Chrome/Chromium for PDF generation (auto-detected)
- **cc-outlook:** Azure App Registration with OAuth credentials
- **cc-transcribe:** FFmpeg + OpenAI API key
- **cc-youtube-info:** No special requirements

Set API key:
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/macOS
export OPENAI_API_KEY=your-key-here
```

---

## License

MIT License - https://github.com/CenterConsulting/cc-tools/blob/main/LICENSE
