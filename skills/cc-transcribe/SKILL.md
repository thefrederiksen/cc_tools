# cc-transcribe

Video and audio transcription with timestamps and automatic screenshot extraction.

**Requirements:**
- `cc-transcribe.exe` must be in PATH
- FFmpeg installed and in PATH
- OpenAI API key: set `OPENAI_API_KEY` environment variable

---

## Quick Reference

```bash
# Basic transcription
cc-transcribe video.mp4

# Specify output directory
cc-transcribe video.mp4 -o ./output/

# Without screenshots
cc-transcribe video.mp4 --no-screenshots

# Show video info only
cc-transcribe video.mp4 --info
```

---

## Commands

### Basic Transcription

```bash
# Transcribe with default settings
cc-transcribe video.mp4

# Custom output directory
cc-transcribe video.mp4 -o ./transcripts/

# Transcribe audio file
cc-transcribe podcast.mp3 -o ./podcast/
```

### Screenshot Control

```bash
# Disable screenshot extraction
cc-transcribe video.mp4 --no-screenshots

# More screenshots (lower threshold = more sensitive)
cc-transcribe video.mp4 --threshold 0.85

# Less screenshots (higher threshold)
cc-transcribe video.mp4 --threshold 0.95

# Minimum interval between screenshots
cc-transcribe video.mp4 --interval 2.0
```

### Language Options

```bash
# Force English
cc-transcribe video.mp4 --language en

# Force Spanish
cc-transcribe video.mp4 --language es

# Force German
cc-transcribe video.mp4 --language de
```

### Video Info

```bash
# Show video metadata without transcribing
cc-transcribe video.mp4 --info
```

---

## Output Structure

```
output_directory/
    transcript.txt      # Timestamped transcript
    transcript.json     # Detailed segments with timing
    screenshots/        # Extracted frames (optional)
        screenshot_00-00-00.png
        screenshot_00-01-23.png
        ...
```

---

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory |
| `--screenshots/--no-screenshots` | Extract screenshots (default: on) |
| `-t, --threshold` | SSIM threshold 0.0-1.0 (default: 0.92, lower = more) |
| `-i, --interval` | Min seconds between screenshots (default: 1.0) |
| `-l, --language` | Force language code (e.g., en, es, de) |
| `--info` | Show video info and exit |
| `-v, --version` | Show version |

---

## Supported Formats

| Type | Formats |
|------|---------|
| Video | .mp4, .mkv, .avi, .mov, .webm |
| Audio | .mp3, .wav, .m4a, .ogg, .flac |

---

## Examples

### Transcribe a Meeting Recording

```bash
cc-transcribe meeting.mp4 -o ./meeting-notes/
```

Output:
- `meeting-notes/transcript.txt` - Full transcript with timestamps
- `meeting-notes/screenshots/` - Key frames from the meeting

### Transcribe a Tutorial with More Screenshots

```bash
cc-transcribe tutorial.mp4 -o ./tutorial/ --threshold 0.85 --interval 0.5
```

### Quick Audio Transcription

```bash
cc-transcribe podcast.mp3 --no-screenshots -o ./podcast/
```

### Check Video Info First

```bash
cc-transcribe video.mkv --info
```

Output:
```
File: video.mkv
Duration: 45m 30s
Size: 1.2 GB
Format: matroska
```

---

## LLM Use Cases

1. **Meeting notes** - "Transcribe this meeting recording"
2. **Video analysis** - "Extract the transcript and key frames from this video"
3. **Podcast processing** - "Transcribe this podcast episode"
4. **Tutorial documentation** - "Create a text version of this tutorial video"
