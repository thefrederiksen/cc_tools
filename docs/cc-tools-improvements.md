# CC Tools API Feature Mining Guide

## Overview

### What is API Feature Mining?

API Feature Mining is the practice of auditing CLI tools against their underlying APIs to discover unexposed capabilities. Many APIs return more data than we use, or support operations that our wrappers don't expose. These are "free features" - the API already supports them, we just need to surface them.

### The Insight

**APIs often return more data than we use.** Services like Gmail, Microsoft Graph, OpenAI, and YouTube have extensive capabilities. Our CLI wrappers may only use a fraction of what's available. By systematically comparing our implementation against the API documentation, we can identify low-effort improvements.

### Types of Opportunities

| Type | Effort | Description | Example |
|------|--------|-------------|---------|
| **Free Field** | Trivial | API already returns data we discard | Gmail's `resultSizeEstimate` |
| **Simple Endpoint** | Small | One API call, no complex logic | OpenAI moderation endpoint |
| **Parameter Exposure** | Small | Existing call has unused parameters | Gmail's `includeSpamTrash` |
| **New Method** | Medium | Requires new logic or state management | Thread-based operations |

---

## The Process

### Step 1: Identify the Underlying API

Before auditing a tool, know what API it wraps:

```
Tool           -> API                    -> Documentation
cc-gmail       -> Gmail API v1           -> developers.google.com/gmail/api
cc-outlook     -> Microsoft Graph        -> learn.microsoft.com/graph/api
cc-image       -> OpenAI Images + Vision -> platform.openai.com/docs/api-reference
cc-voice       -> OpenAI TTS             -> platform.openai.com/docs/api-reference/audio
cc-whisper     -> OpenAI Whisper         -> platform.openai.com/docs/api-reference/audio
cc-youtube     -> yt-dlp (wrapper)       -> github.com/yt-dlp/yt-dlp
```

### Step 2: Read Current Implementation

1. Find the API wrapper module (usually `*_api.py` or `api.py`)
2. List all methods and what endpoints they call
3. For each API call, note:
   - What parameters are passed
   - What fields are extracted from the response
   - What fields are IGNORED

Example analysis from `cc-gmail/src/gmail_api.py`:

```python
# list_messages() calls messages.list()
# USES: messages (list of IDs)
# IGNORES: resultSizeEstimate, nextPageToken
```

### Step 3: Fetch API Documentation

For each endpoint used, check the official docs for:
- Response fields not being used
- Request parameters not being exposed
- Related endpoints that could add value

Use WebFetch or direct browser access:
```
cc-gmail uses: users.messages.list
Docs: https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list

Response includes:
- messages[] - WE USE
- nextPageToken - WE IGNORE (pagination)
- resultSizeEstimate - WE IGNORED -> NOW count command!
```

### Step 4: Gap Analysis

Create a comparison table:

| API Feature | Current Status | Effort | Value |
|-------------|---------------|--------|-------|
| resultSizeEstimate | Not exposed | Trivial | High - instant counts |
| nextPageToken | Not exposed | Small | Medium - pagination |
| format=minimal | Not used | Trivial | Low - perf optimization |

### Step 5: Document Opportunities

For each opportunity, document:
1. What API feature is unexposed
2. How it would benefit users
3. Estimated implementation effort
4. Code location for implementation

### Step 6: Implement (Optional)

Start with trivial wins that provide clear user value.

---

## Case Study: cc-gmail count Command

### Discovery

While reading the Gmail API docs, we noticed that `users.messages.list` returns a `resultSizeEstimate` field. This provides an instant server-side count without fetching actual messages.

The existing `list_messages()` method was calling this endpoint:

```python
# BEFORE: Discarding useful data
def list_messages(self, ...) -> List[Dict[str, Any]]:
    results = self.service.users().messages().list(**kwargs).execute()
    return results.get("messages", [])  # resultSizeEstimate ignored!
```

### Implementation

**1. Add method to API wrapper** (`gmail_api.py`):

```python
def count_messages(
    self,
    label_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
) -> int:
    """
    Get estimated count of messages matching criteria.

    Uses Gmail's resultSizeEstimate for instant server-side count.
    No pagination required - returns immediately.
    """
    kwargs = {"userId": self.user_id}
    if label_ids:
        kwargs["labelIds"] = label_ids
    if query:
        kwargs["q"] = query
    results = self.service.users().messages().list(**kwargs).execute()
    return int(results.get("resultSizeEstimate", 0))
```

**2. Add CLI command** (`cli.py`):

```python
@app.command()
def count(
    query: str = typer.Argument(None, help="Gmail search query (optional)"),
    label: str = typer.Option(None, "-l", "--label", help="Label to count"),
):
    """Count emails matching a query (fast server-side estimate)."""
    client = get_client()
    label_ids = [label.upper()] if label else None
    result = client.count_messages(label_ids=label_ids, query=query)
    console.print(f"{result}")
```

### Result

- ~20 lines of code added
- New `cc-gmail count` command
- Instant results (no pagination delay)
- Works with any Gmail search query

### Usage

```bash
cc-gmail count                           # Total inbox
cc-gmail count -l INBOX                  # Inbox messages
cc-gmail count "is:unread"               # Unread count
cc-gmail count "from:boss@company.com"   # Messages from person
```

### Lessons Learned

1. Always check what API responses contain beyond what you use
2. Small implementations can add significant value
3. Server-side operations (like counts) are faster than client-side alternatives

---

## Tool Reference

### API-Backed Tools (Priority for Mining)

| Tool | API | Documentation |
|------|-----|---------------|
| cc-gmail | Google Gmail API v1 | https://developers.google.com/gmail/api/reference/rest |
| cc-outlook | Microsoft Graph | https://learn.microsoft.com/en-us/graph/api/overview |
| cc-image | OpenAI DALL-E 3 + Vision | https://platform.openai.com/docs/api-reference/images |
| cc-voice | OpenAI TTS | https://platform.openai.com/docs/api-reference/audio/createSpeech |
| cc-whisper | OpenAI Whisper | https://platform.openai.com/docs/api-reference/audio/createTranscription |
| cc-youtube | yt-dlp | https://github.com/yt-dlp/yt-dlp#options |

### Local Processing Tools (No External APIs)

These tools don't wrap external APIs - improvements come from FFmpeg/library capabilities:

- cc-markdown (Pandoc, html2pdf)
- cc-video (FFmpeg)
- cc-browser (Playwright/CDP)
- cc-crawl4ai (local crawler)
- cc-click (Windows automation)
- cc-setup (installer)

---

## Audit Checklist

Use this checklist when auditing any cc-tool:

### Preparation

- [ ] Identify the underlying API and locate official documentation
- [ ] Find the API wrapper file in the tool's source (e.g., `gmail_api.py`)
- [ ] List all methods and their corresponding API endpoints

### For Each API Endpoint Used

- [ ] Read the official docs for that endpoint
- [ ] Compare request parameters: which ones are we NOT using?
- [ ] Compare response fields: which ones are we discarding?
- [ ] Check for related endpoints we're not using at all

### Gap Analysis

For each unexposed feature:

- [ ] Is it useful for CLI users?
- [ ] What's the implementation effort? (Trivial/Small/Medium)
- [ ] Are there any dependencies or prerequisites?
- [ ] Document in the opportunities table below

### Implementation Planning

- [ ] Sort opportunities by value/effort ratio
- [ ] Start with trivial wins
- [ ] Follow existing patterns in the codebase
- [ ] Test with real API calls

---

## Opportunity Template

When documenting a feature opportunity, use this format:

```markdown
### [Tool Name]: [Feature Name]

**API Endpoint:** `endpoint.method()`
**Current Status:** [Not used / Partially used / Parameter ignored]
**Effort:** [Trivial / Small / Medium]

**What:**
Brief description of the API capability

**Why:**
How this would benefit CLI users

**Implementation:**
- File: `path/to/file.py`
- Add method: `method_name()`
- Add CLI command: `tool command`

**Code Sketch:**
```python
# Key implementation details
```
```

---

## Quick Reference: API Documentation URLs

### Gmail API v1
- Messages: https://developers.google.com/gmail/api/reference/rest/v1/users.messages
- Labels: https://developers.google.com/gmail/api/reference/rest/v1/users.labels
- Drafts: https://developers.google.com/gmail/api/reference/rest/v1/users.drafts
- Threads: https://developers.google.com/gmail/api/reference/rest/v1/users.threads

### Microsoft Graph (Outlook)
- Mail: https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview
- Messages: https://learn.microsoft.com/en-us/graph/api/resources/message
- Folders: https://learn.microsoft.com/en-us/graph/api/resources/mailfolder

### OpenAI
- Images: https://platform.openai.com/docs/api-reference/images
- Audio/TTS: https://platform.openai.com/docs/api-reference/audio/createSpeech
- Audio/Whisper: https://platform.openai.com/docs/api-reference/audio/createTranscription
- Vision: https://platform.openai.com/docs/guides/vision

### yt-dlp
- Options: https://github.com/yt-dlp/yt-dlp#options
- Output Template: https://github.com/yt-dlp/yt-dlp#output-template
- Format Selection: https://github.com/yt-dlp/yt-dlp#format-selection

---

## Example Prompts for Claude

When starting an audit session, use prompts like:

**For exploration:**
```
I want to audit cc-gmail for unexposed Gmail API features.
1. Read the current gmail_api.py implementation
2. Fetch the Gmail API documentation for users.messages endpoints
3. Create a gap analysis table showing what we use vs what's available
```

**For specific features:**
```
Check if the Gmail API's messages.list endpoint has parameters
we're not using in cc-gmail. I want to know about pagination
(nextPageToken), includeSpamTrash, and any useful response fields.
```

**For implementation:**
```
Based on the gap analysis, implement the highest-value trivial
feature following the existing cc-gmail patterns.
```
