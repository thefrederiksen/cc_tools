# CC-Tools Testing Documentation

This document describes the testing infrastructure, test coverage, and validation results for CC-Tools.

---

## Test Summary

| Tool | Unit Tests | Integration Tests | Status |
|------|------------|-------------------|--------|
| cc_shared | 42 | - | PASS |
| cc-click | 11 | - | NEW |
| cc-comm-queue | 101 | - | PASS |
| cc-computer | 35 | - | NEW |
| cc-crawl4ai | 141 | - | PASS |
| cc-docgen | 6 | - | NEW |
| cc-gmail | 49 | - | PASS |
| cc-hardware | 18 | - | PASS |
| cc-image | 38 | - | PASS |
| cc-linkedin | 28 | - | PASS |
| cc-markdown | 13 | 12 | PASS |
| cc-outlook | 51 | - | PASS |
| cc-photos | 33 | - | PASS |
| cc-setup | 6 | - | NEW |
| cc-transcribe | 33 | - | PASS |
| cc-trisight | 19 | - | NEW |
| cc-video | 24 | - | PASS |
| cc-voice | 21 | - | PASS |
| cc-websiteaudit | 59 | - | PASS |
| cc-whisper | 9 | - | PASS |
| **Total** | **737** | **12** | **ALL PASS** |

**Last Tested:** February 26, 2026
**Platform:** Windows 11, Python 3.11.6, .NET 10.0, Node.js 18+

---

## Running Tests

### All Unit Tests

Run all unit tests for a specific tool:

```bash
# cc-markdown
cd src/cc-markdown
python -m pytest tests/ -v

# cc-transcribe
cd src/cc-transcribe
python -m pytest tests/ -v

# cc-image
cd src/cc-image
python -m pytest tests/ -v

# cc-voice
cd src/cc-voice
python -m pytest tests/ -v

# cc-whisper
cd src/cc-whisper
python -m pytest tests/ -v

# cc-video
cd src/cc-video
python -m pytest tests/ -v
```

### Integration Tests

```bash
cd cc-tools
python -m pytest tests/integration/ -v
```

### Quick Test (CI/CD)

```bash
# Run all tests with minimal output
python -m pytest src/cc-markdown/tests/ src/cc-transcribe/tests/ -q
```

---

## Test Coverage by Tool

### cc-markdown (13 unit tests + 12 integration tests)

**Parser Tests (`test_parser.py`):**
- Basic paragraph parsing
- Heading extraction (H1 title detection)
- No title handling
- GFM table rendering
- Fenced code blocks
- Task lists (checkboxes)
- Strikethrough syntax
- Raw content preservation

**HTML Generator Tests (`test_html.py`):**
- HTML document structure
- Title in head element
- CSS embedding in style tags
- Content wrapped in article element
- Default title fallback

**Integration Tests (`test_cc-markdown.py`):**
- CLI version flag
- CLI help flag
- Theme listing
- Markdown to HTML conversion (basic)
- Markdown to HTML conversion (advanced GFM)
- Markdown to PDF conversion
- PDF with theme selection
- All 7 themes generate valid PDFs
- Markdown to DOCX conversion (basic)
- Markdown to DOCX conversion (report)
- Error handling: missing input file
- Error handling: invalid theme

### cc-transcribe (33 unit tests)

**FFmpeg Tests (`test_ffmpeg.py`):**
- FFmpeg detection in PATH
- FFmpeg detection in common locations
- FFmpeg not found error
- Video file not found error
- Output directory creation
- FFmpeg error handling
- Default output naming
- Video duration parsing (ffprobe)
- Video duration parsing (ffmpeg fallback)
- Video info retrieval

**Screenshot Tests (`test_screenshots.py`):**
- Timestamp formatting (zero)
- Timestamp formatting (seconds only)
- Timestamp formatting (minutes and seconds)
- Timestamp formatting (hours)
- SSIM similarity calculation (identical frames)
- SSIM similarity calculation (different frames)
- SSIM similarity calculation (similar frames)
- Large frame resizing
- Video not found error
- Invalid video error

**Transcriber Tests (`test_transcriber.py`):**
- API key from environment
- API key missing error
- Empty segments handling
- Single segment formatting
- Multiple segments formatting
- Timestamp formatting
- Whitespace stripping
- Empty text segment skipping
- Video not found error
- Output file creation
- Result object return

### cc-image (38 unit tests)

**Vision Tests (`test_vision.py`):**
- API key from environment
- API key missing error
- Base64 image encoding
- Media type detection (JPEG, PNG, GIF, WebP)
- Unknown format handling
- File not found error
- API call verification
- API error handling
- Describe function
- Extract text function

**Generation Tests (`test_generation.py`):**
- API key handling
- Image bytes return
- API error handling
- Empty data error
- Download error handling
- File saving
- Output directory creation
- Parameter passing

**Manipulation Tests (`test_manipulation.py`):**
- File not found handling
- Image info retrieval
- Path string handling
- Resize by width
- Resize by height
- Resize without aspect ratio
- Output directory creation
- Format conversion (PNG to JPEG, JPEG to PNG, RGBA to JPEG, to WebP)

### cc-voice (21 unit tests)

**TTS Tests (`test_tts.py`):**
- API key handling
- Markdown code block removal
- Inline code removal
- Bold text handling
- Italic text handling
- Strikethrough removal
- Link text preservation
- Header removal
- Horizontal rule removal
- Whitespace cleanup
- Text chunking (short text)
- Text chunking (max chars)
- Sentence boundary splitting
- Long sentence handling
- Audio bytes return
- Voice selection
- Model selection
- Empty text error
- File saving
- Output directory creation

### cc-whisper (9 unit tests)

**Transcribe Tests (`test_transcribe.py`):**
- API key handling
- File not found error
- Text return
- Language parameter
- Timestamps mode
- Plain text file saving
- Timestamps file saving
- Output directory creation

### cc-video (24 unit tests)

**FFmpeg Tests (`test_ffmpeg.py`):**
- Duration formatting (seconds, minutes, hours, zero, exact hour)
- FFmpeg detection (PATH, common locations, not found)
- Video info retrieval
- Audio extraction (file not found, directory creation, default naming)

**Screenshot Tests (`test_screenshots.py`):**
- Timestamp formatting (seconds, minutes, hours, zero, fractional)
- SSIM similarity (identical, different, large frames)
- Video not found error
- Invalid video error
- Frame extraction at timestamp

---

## MCP Tools (fred-tools) Validation

The following MCP tools have been validated for Claude Code integration:

| Tool | Function | Status |
|------|----------|--------|
| fred_llm | GPT-4o text generation | PASS |
| fred_embed | Text embedding (1536 dim) | PASS |
| fred_tts | Text-to-speech (MP3) | PASS |
| fred_whisper | Speech-to-text | PASS |
| fred_image_gen | DALL-E image generation | PASS |
| fred_vision_describe | GPT-4V image description | PASS |
| fred_vision_extract_text | GPT-4V OCR | PASS |
| fred_transcribe_video | Video transcription | PASS |
| fred_markdown_to_pdf | PDF generation | PASS |
| fred_markdown_to_word | DOCX generation | PASS |

---

## Test Fixtures

Test fixtures are located in `tests/integration/fixtures/`:

- `basic.md` - Basic markdown with headings, lists, tables, code blocks
- `advanced.md` - GFM features: task lists, strikethrough, nested lists, multiple code languages
- `report.md` - Real-world business report format

---

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Push to main branch
- Pull requests
- Ubuntu, Windows, macOS
- Python 3.11

See `.github/workflows/build.yml` for configuration.

---

## Test Output Artifacts

Integration tests generate output files in `tests/integration/output/`:

| File | Size | Description |
|------|------|-------------|
| basic.html | 5.7 KB | HTML output test |
| advanced.html | 7.7 KB | GFM HTML output |
| basic.pdf | 57 KB | PDF output test |
| basic.docx | 37 KB | DOCX output test |
| report.docx | 38 KB | Report DOCX test |
| report_boardroom.pdf | 122 KB | Themed PDF test |
| theme_*.pdf | 56-245 KB | All theme validation |

---

## Adding New Tests

### Unit Test Template

```python
"""Tests for new_module."""

import pytest
from src.new_module import function_to_test


class TestFunctionName:
    """Tests for function_to_test."""

    def test_basic_case(self):
        """Test basic functionality."""
        result = function_to_test("input")
        assert result == "expected"

    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Integration Test Template

```python
"""Integration tests for tool CLI."""

import subprocess
import sys
from pathlib import Path


def run_tool(*args):
    """Run tool CLI and return result."""
    cmd = [sys.executable, "-m", "src.cli"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli_version():
    """Test --version flag."""
    result = run_tool("--version")
    assert result.returncode == 0
```

---

## Known Limitations

1. **Video transcription tests** require actual video files and OPENAI_API_KEY
2. **Gmail tests** require OAuth credentials and cannot be fully automated
3. **PDF generation** requires Chromium/Playwright browsers installed
4. **Image generation tests** use mocked API responses to avoid costs

---

## Troubleshooting

### Tests fail with "module not found"

Ensure you're in the correct directory and dependencies are installed:

```bash
cd src/cc-markdown
pip install -r requirements.txt
pip install pytest
```

### PDF tests fail

Install Playwright browsers:

```bash
playwright install chromium
```

### API tests fail

Set environment variables:

```bash
set OPENAI_API_KEY=your-key-here
```
