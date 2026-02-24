# cc_tool_audit: cc-youtube-info

## Summary

- **Tool**: cc-youtube-info
- **APIs**: yt-dlp (video metadata) + youtube-transcript-api (transcripts)
- **Current Commands**: `info`, `transcript`, `languages`, `chapters`
- **API Coverage**: ~55% of available capabilities
- **Quick Wins Implemented**: 4 (categories/tags, live_status, channel_follower_count, age_limit)

## Implementation Status

The following features have been implemented:

| Feature | Status | Notes |
|---------|--------|-------|
| `languages` command | DONE | Lists available subtitle languages |
| `description` field | DONE | Included in info output |
| `chapters` command | DONE | Lists video chapters with timestamps |
| `srt`/`vtt` export | DONE | --format option on transcript command |
| `stats` in info | DONE | view_count, like_count, comment_count |
| `upload_date` | DONE | Formatted as YYYY-MM-DD |
| `categories`/`tags` | DONE | Included in info output (table + JSON) |
| `live_status` | DONE | Shows live/upcoming/was_live status |
| `channel_follower_count` | DONE | Shows subscriber count |
| `age_limit` | DONE | Warning for age-restricted videos |

---

## Current Implementation Map

### yt-dlp Usage (get_video_info)

```
PARAMS USED:
  - quiet, no_warnings, extract_flat (options)

RESPONSE FIELDS USED:
  - id, title, channel, uploader, duration, thumbnail
  - subtitles (for has_captions check)
  - automatic_captions (for has_auto_captions check)
  - description, upload_date, view_count, like_count
  - comment_count, chapters
  - categories, tags
  - channel_follower_count
  - live_status
  - age_limit

RESPONSE FIELDS IGNORED:
  - is_live, was_live (redundant with live_status)
  - availability
  - release_timestamp, modified_timestamp
  - playlist_count, entries (playlist fields)
```

### youtube-transcript-api Usage

```
METHODS USED:
  - YouTubeTranscriptApi().list()
  - find_manually_created_transcript()
  - find_generated_transcript()
  - transcript.translate()
  - transcript.fetch()
  - SRTFormatter, WebVTTFormatter

FROM FETCHED TRANSCRIPT:
  - snippet.text (used)
  - snippet.start (used for timestamps)
  - snippet.duration (IGNORED)

FEATURES NOT USED:
  - Batch/multi-video operations
  - translation_languages property
  - JSONFormatter (we build JSON manually)
  - preserve_formatting option
```

---

## Remaining Recommendations

| Priority | Feature | Effort | LLM Value | Use Case |
|----------|---------|--------|-----------|----------|
| 1 | `search` command | Small | High | "Find where they talk about X" |
| 2 | `playlist` support | Medium | High | "Get transcripts for all videos in playlist" |

---

## Quick Wins (IMPLEMENTED)

All quick wins have been implemented:

| Feature | Status | Implementation |
|---------|--------|----------------|
| `categories`/`tags` | DONE | Added to VideoInfo, shown in table and JSON |
| `live_status` | DONE | Shows 'Is Live', 'Was Live', 'Is Upcoming' in table |
| `channel_follower_count` | DONE | Shows subscriber count in table |
| `age_limit` | DONE | Warning displayed for age-restricted videos |

---

## Small-Effort Improvements

### 1. `search` command - Search within transcript

**API Feature**: None (local processing)
**Current Status**: Not available
**Implementation**: Add `search` command to find text in transcript with timestamps
**LLM Use Case**: "Find where they talk about machine learning"

**Code Sketch**:
```python
@app.command()
def search(
    url: str = typer.Argument(..., help="YouTube video URL"),
    query: str = typer.Argument(..., help="Text to search for"),
    context: int = typer.Option(1, "-c", "--context", help="Lines of context around match"),
    language: str = typer.Option("en", "-l", "--lang", help="Subtitle language code"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Search transcript for text and show timestamps."""
    try:
        text = download_transcript(url, language=language, include_timestamps=True)
        lines = text.split("\n")
        matches = []

        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                start = max(0, i - context)
                end = min(len(lines), i + context + 1)
                context_lines = lines[start:end]
                matches.append({
                    "line_number": i,
                    "match": line,
                    "context": context_lines,
                })

        if json_output:
            console.print(json.dumps({"query": query, "matches": matches}, indent=2))
        else:
            console.print(f"[cyan]Found {len(matches)} matches for '{query}':[/cyan]\n")
            for m in matches:
                for j, ctx_line in enumerate(m["context"]):
                    marker = ">>>" if query.lower() in ctx_line.lower() else "   "
                    console.print(f"{marker} {ctx_line}")
                console.print()

    except (InvalidURLError, VideoNotFoundError, NoSubtitlesError, YouTubeError) as e:
        _handle_youtube_error(e, use_stderr=True)
        raise typer.Exit(1)
```

---

## Medium-Effort Improvements

### 1. Playlist support

**API Feature**: yt-dlp supports playlist extraction with `extract_flat: True`
**Current Status**: Not supported
**Implementation**: Detect playlist URLs, iterate over videos
**LLM Use Case**: "Get transcripts for all videos in this playlist"

This requires significant work:
- Detect playlist URLs vs single video URLs
- Extract video list with `extract_flat: True`
- Iterate and download transcripts/info
- Handle batch output (separate files or combined JSON)
- Progress indication for multi-video operations

Consider implementing as a separate `batch` subcommand:

```bash
cc-youtube-info batch transcript "PLAYLIST_URL" -o transcripts/
cc-youtube-info batch info "PLAYLIST_URL" --json > playlist_info.json
```

---

## API Endpoints/Features Not Used

| Feature | API | Purpose | Potential Use Case |
|---------|-----|---------|-------------------|
| `translation_languages` | transcript-api | List what languages transcript can be translated to | "What languages can I get this in?" |
| `preserve_formatting` | transcript-api | Keep HTML formatting in transcript | "Keep bold/italic formatting" |
| `release_timestamp` | yt-dlp | Exact release time | "When exactly was this released?" |
| `availability` | yt-dlp | Video access status | "Is this video public?" |
| Batch fetch | transcript-api | Fetch multiple transcripts | Playlist support |

---

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | "Extract transcripts, metadata, and information from YouTube videos" |
| What it does NOT do | OK | Explicitly lists: no uploads, no video downloads, no modifications |
| Descriptive name | OK | `cc-youtube-info` - clearly indicates information extraction |
| LLM use cases | OK | Documented in README with specific examples |

The documentation is comprehensive and well-structured after the recent rename from `cc-youtube`.

---

## Notes

1. **yt-dlp can be slow** - The current `get_video_info` call is somewhat slow. Adding more fields to extract is free (no additional API calls), but be mindful of user experience.

2. **Transcript API is reliable** - The youtube-transcript-api handles most edge cases well. The formatters work correctly for SRT/VTT export.

3. **Playlist support is valuable but complex** - Consider implementing as a separate command with progress indication, or a separate `cc-youtube_batch` tool.

4. **Description often contains timestamps** - Many videos have manual chapter markers in the description. Could potentially parse these as fallback when `chapters` is empty.

5. **Age-restricted videos** - The transcript-api cannot access age-restricted videos without authentication, which is currently broken in the library.

---

## Sources

- [yt-dlp GitHub Repository](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp extractor common.py (field documentation)](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/common.py)
- [youtube-transcript-api PyPI](https://pypi.org/project/youtube-transcript-api/)
- [youtube-transcript-api GitHub](https://github.com/jdepoix/youtube-transcript-api)

---

**Audit Date**: 2026-02-17
**Audited By**: Claude (cc_tool_audit skill)
