# cc-video

Video utilities: info, extract audio, screenshots, and frame capture.

**Requirements:**
- `cc-video.exe` must be in PATH
- FFmpeg installed and in PATH

---

## Quick Reference

```bash
# Show video info
cc-video info video.mp4

# Extract audio
cc-video audio video.mp4 -o audio.mp3

# Extract screenshots at content changes
cc-video screenshots video.mp4 -o ./frames/

# Extract single frame at timestamp
cc-video frame video.mp4 -t 30.5 -o frame.png
```

---

## Commands

### Info

```bash
# Show video metadata
cc-video info video.mp4
```

Output:
```
+------------+---------------+
| Property   | Value         |
+------------+---------------+
| Duration   | 10:30         |
| Size       | 245.3 MB      |
| Format     | mp4           |
| Resolution | 1920 x 1080   |
+------------+---------------+
```

### Audio Extraction

```bash
# Extract as MP3 (default)
cc-video audio video.mp4 -o audio.mp3

# Different formats
cc-video audio video.mp4 -o audio.wav --format wav
cc-video audio video.mp4 -o audio.aac --format aac
cc-video audio video.mp4 -o audio.flac --format flac
cc-video audio video.mp4 -o audio.ogg --format ogg

# Custom bitrate
cc-video audio video.mp4 -o audio.mp3 --bitrate 320k
```

### Screenshots (Content Change Detection)

```bash
# Extract screenshots when content changes
cc-video screenshots video.mp4 -o ./frames/

# More screenshots (lower threshold = more sensitive)
cc-video screenshots video.mp4 -o ./frames/ --threshold 0.85

# Less screenshots (higher threshold)
cc-video screenshots video.mp4 -o ./frames/ --threshold 0.95

# Minimum interval between screenshots
cc-video screenshots video.mp4 -o ./frames/ --interval 2.0

# Maximum number of screenshots
cc-video screenshots video.mp4 -o ./frames/ --max 20
```

### Frame at Timestamp

```bash
# Extract frame at 30 seconds
cc-video frame video.mp4 -t 30 -o frame.png

# Extract frame at 1 minute 15.5 seconds
cc-video frame video.mp4 -t 75.5 -o frame.png
```

---

## Options

| Command | Option | Description |
|---------|--------|-------------|
| audio | `-o, --output` | Output path |
| audio | `-f, --format` | Format: mp3, wav, aac, flac, ogg |
| audio | `-b, --bitrate` | Audio bitrate (default: 192k) |
| screenshots | `-o, --output` | Output directory (required) |
| screenshots | `-t, --threshold` | Sensitivity 0-1 (default: 0.92) |
| screenshots | `-i, --interval` | Min seconds between shots |
| screenshots | `-n, --max` | Maximum screenshots |
| frame | `-t, --time` | Timestamp in seconds (required) |
| frame | `-o, --output` | Output path (required) |

---

## Supported Formats

| Input | Audio Output |
|-------|--------------|
| .mp4, .mkv, .avi, .mov, .webm | .mp3, .wav, .aac, .flac, .ogg |

---

## Examples

### Extract Audio from Meeting Recording

```bash
cc-video audio meeting.mp4 -o meeting-audio.mp3
```

### Get Key Frames from a Tutorial

```bash
cc-video screenshots tutorial.mp4 -o ./tutorial-frames/ --threshold 0.88 --interval 1.0
```

### Extract Thumbnail at Specific Time

```bash
cc-video frame promo.mp4 -t 5.0 -o thumbnail.png
```

### Quick Video Check

```bash
cc-video info unknown-video.mkv
```

---

## LLM Use Cases

1. **Audio extraction** - "Extract the audio track from this video"
2. **Key frames** - "Get screenshots of important moments in this video"
3. **Thumbnail creation** - "Extract a frame at the 10 second mark for a thumbnail"
4. **Video analysis** - "Show me the video metadata"
5. **Podcast conversion** - "Convert this video to an MP3 audio file"
