# cc-voice

Convert text to speech using OpenAI TTS.

**Requirements:**
- `cc-voice.exe` must be in PATH
- OpenAI API key: set `OPENAI_API_KEY` environment variable

---

## Quick Reference

```bash
# Convert text to speech
cc-voice "Hello, this is a test" -o hello.mp3

# Use different voice
cc-voice "Welcome to the show" -o welcome.mp3 --voice nova

# Read from file
cc-voice notes.txt -o notes.mp3

# High definition model
cc-voice "Important announcement" -o announcement.mp3 --model tts-1-hd
```

---

## Commands

### Basic Text-to-Speech

```bash
# Convert text string
cc-voice "Your text here" -o output.mp3

# Read text from file
cc-voice document.txt -o document.mp3
cc-voice README.md -o readme.mp3
```

### Voice Selection

```bash
# Alloy - neutral, balanced
cc-voice "text" -o out.mp3 --voice alloy

# Echo - male, warm
cc-voice "text" -o out.mp3 --voice echo

# Fable - British accent
cc-voice "text" -o out.mp3 --voice fable

# Nova - female, friendly
cc-voice "text" -o out.mp3 --voice nova

# Onyx - male, deep (default)
cc-voice "text" -o out.mp3 --voice onyx

# Shimmer - female, expressive
cc-voice "text" -o out.mp3 --voice shimmer
```

### Quality Settings

```bash
# Standard quality (faster, cheaper)
cc-voice "text" -o out.mp3 --model tts-1

# High definition (better quality)
cc-voice "text" -o out.mp3 --model tts-1-hd
```

### Speed Control

```bash
# Normal speed (1.0)
cc-voice "text" -o out.mp3 --speed 1.0

# Slower (0.5x)
cc-voice "text" -o out.mp3 --speed 0.5

# Faster (1.5x)
cc-voice "text" -o out.mp3 --speed 1.5

# Maximum speed (4.0x)
cc-voice "text" -o out.mp3 --speed 4.0
```

### Raw Output

```bash
# Skip markdown cleaning (for plain text)
cc-voice "text" -o out.mp3 --raw
```

---

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output audio file path (required) |
| `-v, --voice` | Voice: alloy, echo, fable, nova, onyx, shimmer |
| `-m, --model` | Model: tts-1, tts-1-hd |
| `-s, --speed` | Speed: 0.25 to 4.0 (default: 1.0) |
| `--raw` | Don't clean markdown formatting |
| `--version` | Show version |

---

## Available Voices

| Voice | Description | Best For |
|-------|-------------|----------|
| `alloy` | Neutral, balanced | General purpose |
| `echo` | Male, warm | Narration |
| `fable` | British accent | Storytelling |
| `nova` | Female, friendly | Customer service |
| `onyx` | Male, deep | Announcements |
| `shimmer` | Female, expressive | Engaging content |

---

## Examples

### Create Audio from Notes

```bash
cc-voice meeting-notes.md -o meeting-notes.mp3 --voice nova
```

### Generate Announcement

```bash
cc-voice "Attention: The system will be under maintenance tonight at 10 PM." \
  -o announcement.mp3 --voice onyx --model tts-1-hd
```

### Create Audiobook Chapter

```bash
cc-voice chapter1.txt -o chapter1.mp3 --voice fable --speed 0.9
```

### Quick Voice Memo

```bash
cc-voice "Remember to call John tomorrow at 3 PM" -o reminder.mp3
```

---

## Tips

1. **Markdown files** - The tool automatically cleans markdown formatting for natural speech
2. **Long text** - Works with text files of any length
3. **Cost optimization** - Use `tts-1` for drafts, `tts-1-hd` for final versions
4. **Speed adjustment** - Slower speeds (0.8-0.9) often sound more natural for narration

---

## LLM Use Cases

1. **Text-to-speech** - "Convert this document to an audio file"
2. **Narration** - "Create an audio version of this article"
3. **Announcements** - "Generate an audio announcement for this message"
4. **Accessibility** - "Create an audio file of this README"
5. **Voice memos** - "Read this note aloud and save as MP3"
