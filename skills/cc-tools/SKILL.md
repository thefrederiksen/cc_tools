# cc-tools

A suite of command-line tools for document conversion, media processing, and AI-powered workflows.

**GitHub:** https://github.com/CenterConsulting/cc-tools

---

## Available Tools

| Tool | Description | Status |
|------|-------------|--------|
| cc_markdown | Markdown to PDF/Word/HTML | Available |
| cc_transcribe | Video/audio transcription | Available |
| cc_gmail | Gmail CLI: read, send, search emails | Available |
| cc_image | Image generation/analysis/OCR | Coming Soon |
| cc_voice | Text-to-speech | Coming Soon |
| cc_whisper | Audio transcription | Coming Soon |
| cc_video | Video utilities | Coming Soon |

---

## cc_markdown

Convert Markdown to beautifully styled PDF, Word, and HTML documents.

### Usage

```bash
# Convert to PDF with a theme
cc_markdown report.md -o report.pdf --theme boardroom

# Convert to Word
cc_markdown report.md -o report.docx --theme paper

# Convert to HTML
cc_markdown report.md -o report.html

# Use custom CSS
cc_markdown report.md -o report.pdf --css custom.css

# List available themes
cc_markdown --themes
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
cc_markdown README.md -o README.pdf

# Corporate report
cc_markdown quarterly-report.md -o report.pdf --theme boardroom

# Technical documentation
cc_markdown api-docs.md -o api-docs.pdf --theme blueprint

# Academic paper
cc_markdown thesis.md -o thesis.pdf --theme thesis --page-size letter
```

---

## cc_transcribe

Video and audio transcription with timestamps and automatic screenshot extraction.

**Requirements:**
- FFmpeg must be installed and in PATH
- OpenAI API key: set `OPENAI_API_KEY` environment variable

### Usage

```bash
# Basic transcription
cc_transcribe video.mp4

# Specify output directory
cc_transcribe video.mp4 -o ./output/

# Without screenshots
cc_transcribe video.mp4 --no-screenshots

# Adjust screenshot sensitivity (lower = more screenshots)
cc_transcribe video.mp4 --threshold 0.85 --interval 2.0

# Force language
cc_transcribe video.mp4 --language en

# Show video info only
cc_transcribe video.mp4 --info
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
cc_transcribe meeting.mp4 -o ./meeting-notes/

# Transcribe a tutorial with frequent screenshots
cc_transcribe tutorial.mp4 --threshold 0.85 --interval 0.5

# Quick transcription without images
cc_transcribe podcast.mp3 --no-screenshots

# Get video metadata
cc_transcribe video.mkv --info
```

---

## cc_gmail

Gmail CLI: read, send, search, and manage emails from the command line.
Supports **multiple Gmail accounts**.

**Requirements:**
- OAuth credentials from Google Cloud Console

### Setup

```bash
# 1. Add an account
cc_gmail accounts add personal

# 2. Follow setup instructions to get credentials.json from Google Cloud
# 3. Place credentials.json in ~/.cc_gmail/accounts/personal/
# 4. Authenticate
cc_gmail auth
```

See the [full README](https://github.com/CenterConsulting/cc-tools/tree/main/src/cc_gmail) for detailed Google Cloud setup steps.

### Multiple Accounts

```bash
# Add accounts
cc_gmail accounts add personal --default
cc_gmail accounts add work

# List accounts
cc_gmail accounts list

# Switch default
cc_gmail accounts default work

# Use specific account
cc_gmail --account work list
cc_gmail -a personal search "from:mom"
```

### Usage

```bash
# Authenticate
cc_gmail auth

# List inbox
cc_gmail list

# List sent messages
cc_gmail list -l SENT

# Show unread only
cc_gmail list --unread

# Read a specific email
cc_gmail read <message_id>

# Send email
cc_gmail send -t "recipient@example.com" -s "Subject" -b "Body text"

# Send with file body
cc_gmail send -t "recipient@example.com" -s "Subject" -f body.txt

# Send with attachments
cc_gmail send -t "to@example.com" -s "Subject" -b "See attached" -a file.pdf

# Create draft
cc_gmail draft -t "recipient@example.com" -s "Subject" -b "Draft body"

# Search emails
cc_gmail search "from:someone@example.com"
cc_gmail search "subject:important is:unread"

# List labels
cc_gmail labels

# Delete (move to trash)
cc_gmail delete <message_id>

# Show profile
cc_gmail profile
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

## Installation

### Quick Install (Recommended)

Download and run the setup executable:

1. Download `cc-tools-setup-windows-x64.exe` from [GitHub Releases](https://github.com/CenterConsulting/cc-tools/releases)
2. Run it - it downloads tools, adds to PATH, installs this skill file
3. Restart your terminal

### Manual Install

Download individual tools from [GitHub Releases](https://github.com/CenterConsulting/cc-tools/releases):
- `cc_markdown-windows-x64.exe`
- `cc_transcribe-windows-x64.exe`

Place in a directory in your PATH.

---

## Requirements

- **cc_markdown:** Chrome/Chromium for PDF generation (auto-detected)
- **cc_transcribe:** FFmpeg + OpenAI API key
- **cc_gmail:** OAuth credentials from Google Cloud Console

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
