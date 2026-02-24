# cc_tool_audit: cc_whisper

## Summary

- **Tool**: cc_whisper
- **API**: OpenAI Whisper API (audio/transcriptions, audio/translations)
- **Current Commands**: `transcribe`, `translate`
- **API Coverage**: ~80% of audio transcription capabilities
- **Quick Wins Implemented**: 4

---

## Implementation Status

The cc_whisper tool provides basic transcription functionality but misses several valuable API features.

| Capability | Status | Notes |
|------------|--------|-------|
| Basic transcription | DONE | Uses whisper-1 model |
| Language specification | DONE | --lang flag |
| Word-level timestamps | DONE | --timestamps flag |
| Segment timestamps | DONE | Included with --timestamps |
| JSON output | DONE | --json flag |
| Translation to English | DONE | `translate` command |
| Temperature control | DONE | --temp flag |
| Prompt/context | DONE | --prompt flag |
| SRT/VTT formats | DONE | --format srt/vtt |
| Newer models | MISSING | gpt-4o-transcribe, diarize |

---

## Current Implementation Map

### transcribe.py - API Parameters Used

```
client.audio.transcriptions.create()
  PARAMS USED: model, file, language, response_format, timestamp_granularities
  PARAMS IGNORED: temperature, prompt
  RESPONSE USED: text, words[], segments[], duration
  RESPONSE IGNORED: task, language (response field)
```

### cli.py - Commands Available

```
main()
  OPTIONS: audio, output, language, timestamps, json_output
  MISSING: temperature, prompt, format (srt/vtt), translate mode, model selection
```

---

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Status |
|----------|---------|--------|-----------|--------|
| 1 | `translate` command | Small | High | DONE |
| 2 | `--prompt` flag | Trivial | High | DONE |
| 3 | `--format srt/vtt` | Trivial | Medium | DONE |
| 4 | `--temperature` flag | Trivial | Low | DONE |
| 5 | Model selection | Small | Medium | Pending |

---

## Quick Wins

### 1. `translate` command - Translate audio to English

**API Feature**: `client.audio.translations.create()`
**Current Status**: Not implemented
**Implementation**: Add translate function and CLI command
**LLM Use Case**: "What is this French/Spanish/German audio saying in English?"

**Code Sketch** (transcribe.py):
```python
def translate(
    audio_path: Path,
    temperature: Optional[float] = None,
    prompt: Optional[str] = None,
) -> dict:
    """
    Translate audio to English text.

    Args:
        audio_path: Path to audio file
        temperature: Sampling temperature (0-1)
        prompt: Context to guide translation style

    Returns:
        Dict with 'text' containing English translation
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = OpenAI(api_key=get_api_key())

    with open(audio_path, "rb") as f:
        kwargs = {
            "model": "whisper-1",
            "file": f,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        if prompt:
            kwargs["prompt"] = prompt

        response = client.audio.translations.create(**kwargs)

    return {"text": response.text}
```

**CLI command**:
```python
@app.command()
def translate(
    audio: Path = typer.Argument(..., help="Audio file to translate"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file"),
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="Context hint"),
):
    """Translate audio from any language to English."""
    result = translate_audio(audio, prompt=prompt)

    if output:
        output.write_text(result["text"], encoding="utf-8")
        console.print(f"[green]Saved:[/green] {output}")
    else:
        print(result["text"])
```

---

### 2. `--prompt` flag - Improve transcription accuracy

**API Feature**: `prompt` parameter on transcriptions.create()
**Current Status**: Not exposed
**Implementation**: Add prompt parameter to transcribe function
**LLM Use Case**: "Transcribe this meeting about Kubernetes" -> use prompt "Kubernetes, kubectl, pods, deployments"

The prompt parameter allows providing context that improves accuracy for:
- Technical terms and jargon
- Proper nouns and names
- Domain-specific vocabulary
- Continuing from previous audio

**Code Sketch** (modify transcribe.py):
```python
def transcribe(
    audio_path: Path,
    language: Optional[str] = None,
    timestamps: bool = False,
    prompt: Optional[str] = None,  # ADD THIS
) -> dict:
    # ...
    kwargs = {
        "model": "whisper-1",
        "file": f,
    }

    if language:
        kwargs["language"] = language
    if prompt:  # ADD THIS
        kwargs["prompt"] = prompt
    # ...
```

**CLI addition**:
```python
prompt: Optional[str] = typer.Option(
    None, "-p", "--prompt",
    help="Context hint for accuracy (names, terms, jargon)"
)
```

---

### 3. `--format srt/vtt` - Native subtitle formats

**API Feature**: `response_format` parameter supports "srt" and "vtt"
**Current Status**: Only using json/verbose_json
**Implementation**: Add format option to get native subtitle output
**LLM Use Case**: "Create subtitles for this video" -> direct SRT/VTT output

**Code Sketch** (transcribe.py):
```python
def transcribe_formatted(
    audio_path: Path,
    format: str = "txt",  # txt, srt, vtt, json
    language: Optional[str] = None,
) -> str:
    """Transcribe with specific output format."""
    client = OpenAI(api_key=get_api_key())

    format_map = {
        "txt": "text",
        "srt": "srt",
        "vtt": "vtt",
        "json": "verbose_json",
    }

    with open(audio_path, "rb") as f:
        kwargs = {
            "model": "whisper-1",
            "file": f,
            "response_format": format_map.get(format, "text"),
        }
        if language:
            kwargs["language"] = language

        response = client.audio.transcriptions.create(**kwargs)

    # srt/vtt/text return string directly
    if format in ("srt", "vtt", "txt"):
        return response  # Already a string
    return response.text
```

**CLI addition**:
```python
format: str = typer.Option(
    "txt", "-f", "--format",
    help="Output format: txt, srt, vtt, json"
)
```

---

### 4. `--temperature` flag - Control output randomness

**API Feature**: `temperature` parameter (0-1)
**Current Status**: Not exposed (uses API default)
**Implementation**: Add temperature option
**LLM Use Case**: "Transcribe with high accuracy" -> temperature=0

Temperature 0 = deterministic, most focused
Temperature 1 = more variation, creative interpretation

**Code Sketch**:
```python
temperature: Optional[float] = typer.Option(
    None, "-t", "--temperature",
    help="Sampling temperature 0-1 (0=deterministic)"
)

# In transcribe():
if temperature is not None:
    kwargs["temperature"] = temperature
```

---

## Medium-Effort Improvements

### 1. Model Selection - Use newer, better models

**API Feature**: Multiple model options available
**Current Status**: Hardcoded to "whisper-1"
**Implementation**: Add --model flag with choices

Available models:
- `whisper-1` - Current default, good general purpose
- `gpt-4o-transcribe` - Higher quality, more accurate
- `gpt-4o-mini-transcribe` - Faster, cheaper, still good
- `gpt-4o-transcribe-diarize` - Speaker identification (who said what)

**Code Sketch**:
```python
model: str = typer.Option(
    "whisper-1", "-m", "--model",
    help="Model: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe"
)
```

Note: gpt-4o-transcribe-diarize requires special handling for speaker labels.

---

### 2. Speaker Diarization - Identify who is speaking

**API Feature**: `gpt-4o-transcribe-diarize` model
**Current Status**: Not implemented
**Implementation**: Add diarize command/flag

This would enable:
- Meeting transcripts with speaker labels
- Interview transcriptions
- Multi-person audio identification

Requires chunking_strategy parameter for audio > 30 seconds.

---

## API Endpoints Not Used

| Endpoint | Purpose | Potential Use Case |
|----------|---------|-------------------|
| `audio/translations` | Translate any language to English | "What does this foreign audio say?" |
| gpt-4o-transcribe | Higher quality transcription | Better accuracy for important content |
| gpt-4o-transcribe-diarize | Speaker identification | Meeting transcripts with names |

---

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | "Transcribe audio files using OpenAI Whisper" |
| What it does NOT do | Missing | Should clarify: no translation, no speaker ID |
| Supported formats | OK | Lists audio formats |
| LLM use cases | Missing | Should add common scenarios |

### Recommendations

1. Add "What It Does NOT Do" section:
   - Does not translate (yet) - only transcribes in source language
   - Does not identify speakers (yet)
   - Does not process video (extract audio first)
   - 25MB file size limit from OpenAI API

2. Add "LLM Use Cases" section:
   - "Transcribe this audio file" -> `cc_whisper audio.mp3`
   - "Transcribe with timestamps" -> `cc_whisper audio.mp3 --timestamps`
   - "Transcribe this Spanish audio" -> `cc_whisper audio.mp3 --lang es`

---

## Notes

1. **Translation is a major gap** - The API supports translating any language to English with one call. This is highly valuable for LLM use cases.

2. **Prompt parameter is underutilized** - This can dramatically improve accuracy for domain-specific content without any model change.

3. **Native SRT/VTT is free** - The API already returns these formats, we just don't expose them. Zero-effort feature.

4. **25MB limit** - OpenAI API has a 25MB file limit. For larger files, audio must be chunked (not currently handled).

5. **Newer models exist** - gpt-4o-transcribe offers better quality. Worth exposing as an option.

---

## Sources

- [OpenAI Audio API Reference](https://platform.openai.com/docs/api-reference/audio)
- [Create Transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription)
- [Create Translation](https://platform.openai.com/docs/api-reference/audio/createTranslation)
- [Speech to Text Guide](https://platform.openai.com/docs/guides/speech-to-text)
- [Whisper Model Info](https://platform.openai.com/docs/models/whisper-1)

---

**Audit Date**: 2026-02-17
**Audited By**: Claude (cc_tool_audit skill)
