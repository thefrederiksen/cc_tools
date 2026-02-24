# cc_tool_audit: cc-gmail

## Summary

- **Tool**: cc-gmail
- **API**: Google Gmail API v1
- **Current Commands**: `auth`, `list`, `read`, `send`, `draft`, `drafts`, `reply`, `search`, `count`, `labels`, `delete`, `untrash`, `archive`, `archive-before`, `profile`, `stats`, `label-stats`, `label-create`, `move`, `accounts` (list/add/default/remove/status)
- **API Coverage**: ~70% of common operations
- **Quick Wins Implemented**: 3

---

## Implementation Status

The cc-gmail tool is well-implemented with comprehensive coverage of common email operations. Key strengths:

| Capability | Status | Notes |
|------------|--------|-------|
| Multi-account support | DONE | Full account management with default account |
| Message listing with pagination | DONE | `list_all_messages()` handles pagination |
| Search with Gmail query syntax | DONE | Full Gmail search syntax supported |
| Batch operations | DONE | `batch_archive_messages()` with chunking |
| Server-side count | DONE | Uses `resultSizeEstimate` for instant counts |
| Mailbox statistics | DONE | Comprehensive `stats` command |
| Label management | DONE | Create, list, get, move to label |
| Draft creation with reply threading | DONE | Properly handles In-Reply-To and References headers |

---

## Current Implementation Map

### gmail_api.py - Methods Used

```
users().getProfile()
  PARAMS USED: userId
  RESPONSE USED: emailAddress, messagesTotal, threadsTotal, historyId

users().labels().list()
  PARAMS USED: userId
  RESPONSE USED: labels[]

users().labels().get()
  PARAMS USED: userId, id
  RESPONSE USED: messagesTotal, messagesUnread, threadsTotal, threadsUnread, type, name, id

users().labels().create()
  PARAMS USED: userId, body (name, labelListVisibility, messageListVisibility)
  RESPONSE USED: id, name

users().messages().list()
  PARAMS USED: userId, maxResults, labelIds, q, pageToken
  PARAMS IGNORED: includeSpamTrash
  RESPONSE USED: messages[], nextPageToken, resultSizeEstimate

users().messages().get()
  PARAMS USED: userId, id, format
  PARAMS IGNORED: metadataHeaders
  RESPONSE USED: id, threadId, snippet, labelIds, payload (headers, body), internalDate
  RESPONSE IGNORED: historyId, sizeEstimate, raw

users().messages().send()
  PARAMS USED: userId, body.raw
  RESPONSE USED: id

users().messages().trash()
  PARAMS USED: userId, id

users().messages().delete()
  PARAMS USED: userId, id

users().messages().modify()
  PARAMS USED: userId, id, body (addLabelIds, removeLabelIds)

users().messages().batchModify()
  PARAMS USED: userId, body (ids, removeLabelIds)

users().drafts().create()
  PARAMS USED: userId, body (message.raw, message.threadId)
  RESPONSE USED: id

users().drafts().list()
  STATUS: IMPLEMENTED but NOT EXPOSED in CLI!
```

---

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Status |
|----------|---------|--------|-----------|--------|
| 1 | `drafts` command | Trivial | High | DONE |
| 2 | `untrash` command | Trivial | Medium | DONE |
| 3 | `--include-spam` flag | Trivial | Low | DONE |
| 4 | `drafts send` command | Small | High | Pending |
| 5 | `thread` command | Medium | High | Pending |

---

## Quick Wins (IMPLEMENTED)

### 1. `drafts` command - List drafts (DONE)

**API Feature**: `users().drafts().list()` - Already implemented as `list_drafts()` in gmail_api.py
**Current Status**: Method exists but NOT exposed in CLI
**Implementation**: Add CLI command that calls existing method
**LLM Use Case**: "Show my draft emails", "Do I have any drafts?"

**Code Sketch** (add to cli.py):
```python
@app.command()
def drafts(
    count: int = typer.Option(10, "-n", "--count", help="Number of drafts to show"),
):
    """List draft emails."""
    client = get_client()

    try:
        draft_list = client.list_drafts(max_results=count)

        if not draft_list:
            console.print("[yellow]No drafts found.[/yellow]")
            return

        acct = resolve_account(state.account)
        console.print(f"\n[cyan]Drafts ({acct})[/cyan]\n")

        for draft in draft_list:
            # Each draft has id and message.id
            draft_id = draft.get("id")
            msg_id = draft.get("message", {}).get("id")
            if msg_id:
                msg = client.get_message_details(msg_id)
                summary = format_message_summary(msg)
                console.print(f"[dim]{draft_id}[/dim]")
                console.print(f"    To: {truncate(summary.get('to', 'N/A'), 50)}")
                console.print(f"    Subject: {truncate(summary['subject'], 60)}")
                console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

---

### 2. `untrash` command - Restore from trash (DONE)

**API Feature**: `users().messages().untrash()`
**Current Status**: Implemented
**Implementation**: Add method to gmail_api.py and CLI command
**LLM Use Case**: "Restore that email I just deleted", "Untrash message X"

**Code Sketch** (add to gmail_api.py):
```python
def untrash_message(self, message_id: str) -> Dict[str, Any]:
    """Restore a message from trash."""
    return (
        self.service.users()
        .messages()
        .untrash(userId=self.user_id, id=message_id)
        .execute()
    )
```

**CLI command**:
```python
@app.command()
def untrash(
    message_id: str = typer.Argument(..., help="Message ID to restore"),
):
    """Restore an email from trash."""
    client = get_client()

    try:
        client.untrash_message(message_id)
        console.print(f"[green]Message restored from trash.[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

---

### 3. `--include-spam` flag on search/list (DONE)

**API Feature**: `includeSpamTrash` parameter on messages.list()
**Current Status**: Implemented on `list` and `search` commands
**Implementation**: Add flag to list and search commands
**LLM Use Case**: "Search all my mail including spam"

**Code Sketch** (modify list_messages in gmail_api.py):
```python
def list_messages(
    self,
    label_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    max_results: int = 10,
    include_spam_trash: bool = False,  # ADD THIS
) -> List[Dict[str, Any]]:
    kwargs = {"userId": self.user_id, "maxResults": max_results}

    if label_ids:
        kwargs["labelIds"] = label_ids
    if query:
        kwargs["q"] = query
    if include_spam_trash:  # ADD THIS
        kwargs["includeSpamTrash"] = True

    results = self.service.users().messages().list(**kwargs).execute()
    return results.get("messages", [])
```

---

## Small-Effort Improvements

### 1. `drafts send` command - Send existing draft

**API Feature**: `users().drafts().send()`
**Current Status**: Not implemented
**Implementation**: Add method and CLI command
**LLM Use Case**: "Send that draft I was working on", "Send draft X"

**Code Sketch** (gmail_api.py):
```python
def send_draft(self, draft_id: str) -> Dict[str, Any]:
    """Send an existing draft."""
    return (
        self.service.users()
        .drafts()
        .send(userId=self.user_id, body={"id": draft_id})
        .execute()
    )
```

**CLI command**:
```python
@app.command("draft-send")
def draft_send(
    draft_id: str = typer.Argument(..., help="Draft ID to send"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation"),
):
    """Send an existing draft email."""
    client = get_client()

    if not yes:
        if not typer.confirm(f"Send draft {draft_id[:16]}?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    try:
        result = client.send_draft(draft_id)
        console.print(f"[green]Draft sent![/green] Message ID: {result.get('id')}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

---

### 2. `draft-delete` command

**API Feature**: `users().drafts().delete()`
**Current Status**: Not implemented
**Implementation**: Add method and CLI command
**LLM Use Case**: "Delete that old draft"

**Code Sketch**:
```python
def delete_draft(self, draft_id: str) -> None:
    """Permanently delete a draft."""
    self.service.users().drafts().delete(
        userId=self.user_id, id=draft_id
    ).execute()
```

---

## Medium-Effort Improvements

### 1. Thread support - View conversation

**API Feature**: `users().threads().list()`, `users().threads().get()`
**Current Status**: Not implemented
**Implementation**: Add thread methods and `thread` command
**LLM Use Case**: "Show me the full conversation with John", "View this email thread"

This requires:
- Add `list_threads()` method
- Add `get_thread()` method to fetch all messages in thread
- Add `thread` CLI command to display conversation
- Consider adding thread-level operations (archive thread, etc.)

**Code Sketch** (gmail_api.py):
```python
def get_thread(self, thread_id: str, format: str = "full") -> Dict[str, Any]:
    """Get all messages in a thread."""
    return (
        self.service.users()
        .threads()
        .get(userId=self.user_id, id=thread_id, format=format)
        .execute()
    )

def list_threads(
    self,
    label_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """List threads matching criteria."""
    kwargs = {"userId": self.user_id, "maxResults": max_results}
    if label_ids:
        kwargs["labelIds"] = label_ids
    if query:
        kwargs["q"] = query
    results = self.service.users().threads().list(**kwargs).execute()
    return results.get("threads", [])
```

**CLI command**:
```python
@app.command()
def thread(
    thread_id: str = typer.Argument(..., help="Thread ID to view"),
):
    """View all messages in an email conversation."""
    client = get_client()

    try:
        thread_data = client.get_thread(thread_id)
        messages = thread_data.get("messages", [])

        console.print(f"\n[cyan]Thread ({len(messages)} messages)[/cyan]\n")

        for msg in messages:
            # Parse and display each message
            headers = {}
            payload = msg.get("payload", {})
            for header in payload.get("headers", []):
                name = header.get("name", "").lower()
                if name in ["from", "date", "subject"]:
                    headers[name] = header.get("value", "")

            console.print(f"[bold]{headers.get('from', 'Unknown')}[/bold]")
            console.print(f"[dim]{headers.get('date', '')}[/dim]")
            console.print(f"{msg.get('snippet', '')[:200]}")
            console.print("-" * 60)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

---

## API Endpoints Not Used

| Endpoint | Purpose | Potential Use Case |
|----------|---------|-------------------|
| `threads.list` | List conversation threads | "Show recent conversations" |
| `threads.get` | Get all messages in thread | "Show full conversation" |
| `threads.modify` | Modify thread labels | "Archive this conversation" |
| `threads.trash/untrash` | Trash/restore thread | "Delete entire conversation" |
| `drafts.get` | Get draft details | "Show draft content" |
| `drafts.update` | Update existing draft | "Edit my draft" |
| `labels.delete` | Delete custom label | "Remove the 'Old' label" |
| `labels.update` | Update label (color, name) | "Rename label X to Y" |
| `history.list` | Get changes since historyId | Sync/incremental updates |
| `settings.*` | Various settings APIs | Filters, forwarding, etc. |

---

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | "Gmail CLI: read, send, search, and manage emails from the command line" |
| What it does NOT do | Missing | Should clarify: no calendar, no contacts, no Google Workspace admin |
| Descriptive name | OK | `cc-gmail` is unambiguous |
| LLM use cases | Missing | Should document common LLM tasks |

### Recommendations

1. Add "What It Does NOT Do" section to README:
   - Does not manage Google Calendar (use `cc-gcal` if it existed)
   - Does not manage Google Contacts
   - Does not access Google Drive attachments directly
   - Does not provide admin/workspace management

2. Add "LLM Use Cases" section:
   - "How many unread emails?" -> `cc-gmail count -l INBOX --unread`
   - "Archive all newsletters" -> `cc-gmail archive-before DATE --category promotions`
   - "What's my inbox status?" -> `cc-gmail stats`
   - "Send email to X about Y" -> `cc-gmail send -t X -s "Y" -b "..."`

---

## Notes

1. **`list_drafts()` is already implemented** - Just needs CLI exposure. This is the easiest win.

2. **Thread support is highly valuable** - Email conversations are fundamental to how people use email. Adding thread view would significantly improve LLM utility.

3. **The tool has excellent multi-account support** - This is a differentiator compared to many email CLI tools.

4. **Error handling is comprehensive** - The `handle_api_error()` function provides user-friendly guidance for common OAuth issues.

5. **Batch operations are well-implemented** - The `batch_archive_messages()` handles chunking correctly for the 1000-message API limit.

---

## Sources

- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [users.messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
- [users.threads Resource](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads)
- [Working with Drafts](https://developers.google.com/workspace/gmail/api/guides/drafts)
- [users.drafts.delete](https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/delete)

---

**Audit Date**: 2026-02-17
**Audited By**: Claude (cc_tool_audit skill)
