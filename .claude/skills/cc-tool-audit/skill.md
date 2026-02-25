---
name: cc-tool-audit
description: Audit cc-tools against their underlying APIs to find unexposed features. Triggers on "/audit <tool_name>" or "audit cc-gmail for improvements".
---

# CC Tool Audit Skill

Audit a cc-tool against its underlying API to discover unexposed capabilities, ignored response fields, and missing endpoints. Prioritize findings by LLM utility.

## Triggers

- `/audit <tool_name>` (e.g., `/audit cc-gmail`)
- "audit cc-gmail for improvements"
- "review cc-youtube-info for missing features"
- "find gaps in cc-outlook"

## Overview

cc-tools are CLI wrappers that make APIs accessible to LLMs. APIs often return more data than we use, or support operations we don't expose. This skill systematically finds these "free features" - capabilities the API already supports that we just need to surface.

The key insight: **LLM utility** is the primary metric, not API completeness. Focus on features that would let an LLM accomplish tasks with simple commands rather than writing code.

---

## Workflow

### STEP 1: Identify and Locate the Tool

Parse the tool name from user input. Accept formats like:
- `cc-gmail` or `gmail`
- `cc-youtube` or `youtube`

Locate the tool directory at `src/<tool_name>/`.

If the tool doesn't exist, list available tools and ask the user which one to audit:

```
Available tools: cc-gmail, cc-outlook, cc-youtube-info, cc-image, cc-voice, cc-whisper, cc-video, cc-markdown, cc-transcribe, cc-crawl4ai
```

### STEP 2: Identify the Underlying API

Read the tool's source files to identify what API/library it wraps:

1. Check for `*_api.py` files (e.g., `gmail_api.py`, `outlook_api.py`)
2. Read `cli.py` to understand commands and their implementations
3. Check `requirements.txt` or pyproject.toml for API client libraries

Use this reference table:

| Tool | API | Documentation |
|------|-----|---------------|
| cc-gmail | Google Gmail API v1 | https://developers.google.com/gmail/api/reference/rest |
| cc-outlook | Microsoft Graph | https://learn.microsoft.com/en-us/graph/api/overview |
| cc-image | OpenAI DALL-E 3 + Vision | https://platform.openai.com/docs/api-reference/images |
| cc-voice | OpenAI TTS | https://platform.openai.com/docs/api-reference/audio/createSpeech |
| cc-whisper | OpenAI Whisper | https://platform.openai.com/docs/api-reference/audio/createTranscription |
| cc-youtube-info | yt-dlp + youtube-transcript-api | https://github.com/yt-dlp/yt-dlp |
| cc-crawl4ai | crawl4ai library | https://github.com/unclecode/crawl4ai |

For local-processing tools (cc-markdown, cc-video, cc-transcribe), note that improvements come from FFmpeg/library capabilities rather than web APIs.

### STEP 3: Analyze Current Implementation

Read all source files in the tool's `src/` directory. For each API call found:

1. **What endpoint/method is called?**
2. **What parameters are passed?**
3. **What response fields are used?**
4. **What response fields are IGNORED?**

Build a usage map. Example for cc-gmail:

```
gmail_api.py:
  - messages.list()
    PARAMS USED: userId, labelIds, q, maxResults
    PARAMS IGNORED: includeSpamTrash, pageToken
    RESPONSE USED: messages[]
    RESPONSE IGNORED: resultSizeEstimate, nextPageToken

  - messages.get()
    PARAMS USED: userId, id, format
    PARAMS IGNORED: metadataHeaders
    RESPONSE USED: snippet, payload
    RESPONSE IGNORED: historyId, internalDate
```

### STEP 4: Fetch API Documentation

Use WebFetch or WebSearch to get official API documentation for each endpoint used.

For each endpoint, document:
- All available request parameters (compare to what we use)
- All response fields (compare to what we extract)
- Related endpoints in the same API that we don't use

Example search queries:
- "Gmail API messages.list reference"
- "Microsoft Graph mail API send message"
- "OpenAI images API parameters"

### STEP 5: Gap Analysis

For each gap found (unused parameter, ignored response field, missing endpoint), assess:

| Criteria | Options |
|----------|---------|
| **Effort** | Trivial (< 20 lines) / Small (< 50 lines) / Medium (< 200 lines) |
| **LLM Value** | High / Medium / Low |
| **Type** | Free Field / Parameter Exposure / Simple Endpoint / New Method |

**LLM Value Assessment:**

- **HIGH**: Enables a common LLM task with a single command
  - "How many unread emails?" -> instant answer
  - "Archive all emails from X" -> batch operation
  - "Get the video duration" -> metadata access

- **MEDIUM**: Useful but less common, or requires some follow-up
  - "List all labels" -> requires user to pick one
  - "Get message headers" -> technical use case

- **LOW**: Niche use case or mostly for humans
  - "Change label color" -> UI-focused
  - "Export to specific format" -> preference-based

### STEP 6: Generate Report

Produce a structured markdown report with this format:

```markdown
# cc-tool-audit: <tool_name>

## Summary

- **Tool**: <tool_name>
- **API**: <api_name>
- **Current Commands**: <list of CLI commands>
- **API Coverage**: ~X% (rough estimate based on endpoints used)
- **Quick Wins Found**: <count of trivial-effort, high-value items>

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Use Case |
|----------|---------|--------|-----------|----------|
| 1 | ... | Trivial | High | "..." |
| 2 | ... | Small | High | "..." |
| 3 | ... | Medium | Medium | "..." |

## Quick Wins (Trivial Effort, High LLM Value)

### 1. <feature_name>

**API Feature**: <endpoint or field>
**Current Status**: <Not exposed / Field ignored / Parameter not used>
**Implementation**: <Brief description>
**LLM Use Case**: <What task this enables>

**Code Sketch**:
```python
# Key implementation code
```

[Repeat for each quick win]

## Medium-Effort Improvements

[Similar format for small/medium effort items]

## API Endpoints Not Used

List any API endpoints that could add value but aren't currently wrapped:

| Endpoint | Purpose | Potential Use Case |
|----------|---------|-------------------|
| ... | ... | ... |

## Notes

Any caveats, dependencies, or considerations for implementation.

## Documentation Review

<documentation_checklist>
- [ ] README clearly states what tool does
- [ ] README clarifies what tool does NOT do
- [ ] Tool name is descriptive (not ambiguous)
- [ ] LLM use cases are documented
</documentation_checklist>
```

### STEP 7: Documentation Review

After the technical audit, review the tool's documentation quality:

| Question | Why It Matters |
|----------|----------------|
| Does the README clearly state what the tool does? | Users (and LLMs) need to quickly understand purpose |
| Does it clarify what the tool does NOT do? | Prevents confusion (e.g., "cc-youtube" vs video download) |
| Is the tool name descriptive? | Avoid ambiguous names like "cc-youtube" (upload? download? info?) |
| Are LLM use cases documented? | Shows how an LLM agent would use this tool |

Include a Documentation section in the audit report:

```markdown
## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK / Needs work | ... |
| What it does NOT do | OK / Missing | ... |
| Descriptive name | OK / Ambiguous | ... |
| LLM use cases | OK / Missing | ... |

### Recommendations

- [If name is ambiguous, suggest rename]
- [If missing "does NOT do" section, suggest adding]
- [If missing LLM use cases, provide examples]
```

---

## Output Location

Save the audit report to: `docs/audits/<tool_name>_audit.md`

Also display a summary to the user in the conversation.

---

## Example: cc-gmail Audit

Here's what a partial audit might look like:

```markdown
# cc-tool-audit: cc-gmail

## Summary

- **Tool**: cc-gmail
- **API**: Google Gmail API v1
- **Current Commands**: send, list, read, count, archive-before
- **API Coverage**: ~35%
- **Quick Wins Found**: 3

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Use Case |
|----------|---------|--------|-----------|----------|
| 1 | batch archive | Small | High | "Archive all emails from X" |
| 2 | thread view | Medium | High | "Show me the conversation with Y" |
| 3 | label management | Small | Medium | "Create a label called Z" |

## Quick Wins

### 1. includeSpamTrash parameter

**API Feature**: `includeSpamTrash` param on messages.list()
**Current Status**: Parameter not exposed
**Implementation**: Add --include-spam flag to list command
**LLM Use Case**: "Search all my mail including spam"

**Code Sketch**:
```python
# In gmail_api.py list_messages():
if include_spam:
    kwargs["includeSpamTrash"] = True
```
```

---

## Tips for Effective Auditing

1. **Start with the API wrapper file** - This shows exactly what's being called
2. **Read response handling carefully** - Look for `.get()` calls that extract only some fields
3. **Check for pagination** - Many APIs support it but tools may only fetch first page
4. **Look for batch operations** - APIs often support batch requests we don't use
5. **Consider metadata** - Timestamps, IDs, and counts are often ignored but valuable

---

## Verification

After generating the report:
1. Verify at least one "quick win" could be implemented with the code sketch provided
2. Confirm the API documentation links are correct
3. Check that the LLM value assessments make sense
4. Verify documentation review section is included with actionable recommendations

---

**Skill Version:** 1.1
**Last Updated:** 2026-02-17
**Based on:** docs/cc-tools_improvements.md
