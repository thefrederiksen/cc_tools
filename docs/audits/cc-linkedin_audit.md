# cc_tool_audit: cc_linkedin

## Summary

- **Tool**: cc_linkedin
- **Type**: Browser automation (via cc_browser daemon)
- **Current Commands**: 24 commands
- **LinkedIn Feature Coverage**: ~60% of common user actions
- **Quick Wins Implemented**: 8 of 8 (all trivial-small effort items done)

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Use Case | Status |
|----------|---------|--------|-----------|----------|--------|
| 1 | `notifications` command | Small | High | "Do I have any LinkedIn notifications?" | IMPLEMENTED |
| 2 | `invitations` command | Small | High | "Show me pending connection requests" | IMPLEMENTED |
| 3 | `accept` / `ignore` invitation | Trivial | High | "Accept all invitations from X" | IMPLEMENTED |
| 4 | `repost` command | Trivial | High | "Repost this article" | IMPLEMENTED |
| 5 | `save` post command | Trivial | Medium | "Save this post for later" | IMPLEMENTED |
| 6 | `company` command | Small | High | "Show me info about Anthropic" | IMPLEMENTED |
| 7 | `jobs` command | Small | Medium | "Search for AI engineer jobs" | IMPLEMENTED |
| 8 | `unread` messages filter | Trivial | High | "Show only unread messages" | IMPLEMENTED |
| 9 | Profile sections (experience, education) | Medium | Medium | "What's John's work history?" | Pending |
| 10 | `create-post` command | Medium | High | "Post this to LinkedIn" | Pending |

## Quick Wins (Trivial Effort, High LLM Value)

### 1. Notifications Command

**Current Status**: Not implemented (URL exists in selectors.py)
**Implementation**: Navigate to notifications page, extract notification items
**LLM Use Case**: "Do I have any LinkedIn notifications?" / "What's new on LinkedIn?"

**Code Sketch**:
```python
@app.command()
def notifications(
    limit: int = typer.Option(10, help="Number of notifications to show"),
):
    """View LinkedIn notifications."""
    client = get_client()
    client.navigate(LinkedInURLs.notifications())
    time.sleep(3)

    js_notifications = """
    (() => {
        const items = document.querySelectorAll('.nt-card');
        const data = [];
        for (const item of items) {
            const text = item.querySelector('.nt-card__text')?.textContent?.trim() || '';
            const time = item.querySelector('.nt-card__time')?.textContent?.trim() || '';
            const unread = item.classList.contains('nt-card--unread');
            if (text) data.push({ text, time, unread });
        }
        return JSON.stringify(data);
    })()
    """
    # ... extract and display
```

### 2. Invitations Command (Pending Connection Requests)

**Current Status**: URL exists (`LinkedInURLs.invitations()`) but no command
**Implementation**: Navigate to invitation manager, list pending requests
**LLM Use Case**: "Who wants to connect with me?" / "Show pending invitations"

**Code Sketch**:
```python
@app.command()
def invitations(
    limit: int = typer.Option(10, help="Number of invitations to show"),
):
    """View pending connection invitations."""
    client = get_client()
    client.navigate(LinkedInURLs.invitations())
    time.sleep(3)

    js_invitations = """
    (() => {
        const cards = document.querySelectorAll('li.invitation-card');
        const data = [];
        for (const card of cards) {
            const name = card.querySelector('.invitation-card__name')?.textContent?.trim() || '';
            const headline = card.querySelector('.invitation-card__occupation')?.textContent?.trim() || '';
            const time = card.querySelector('.time-badge')?.textContent?.trim() || '';
            data.push({ name, headline, time });
        }
        return JSON.stringify(data);
    })()
    """
    # ... extract and display
```

### 3. Accept/Ignore Invitation

**Current Status**: Selectors exist (`ACCEPT_BUTTON`, `IGNORE_BUTTON`) but no commands
**Implementation**: Navigate to invitations, find specific invite, click accept/ignore
**LLM Use Case**: "Accept invitation from John" / "Ignore all invitations"

**Code Sketch**:
```python
@app.command()
def accept(
    name: str = typer.Argument(..., help="Name or partial name to accept"),
):
    """Accept a connection invitation."""
    client = get_client()
    client.navigate(LinkedInURLs.invitations())
    time.sleep(3)

    # Find invitation matching name, click accept button
    snapshot = client.snapshot()
    # ... find accept button near matching name
```

### 4. Repost Command

**Current Status**: Selector exists (`REPOST_BUTTON`) but no command
**Implementation**: Navigate to post, click repost button
**LLM Use Case**: "Repost this article to my network"

**Code Sketch**:
```python
@app.command()
def repost(
    url: str = typer.Argument(..., help="Post URL to repost"),
    comment: str = typer.Option("", help="Optional comment to add"),
):
    """Repost content to your feed."""
    # Similar pattern to like command
```

### 5. Save Post Command

**Current Status**: Not implemented
**Implementation**: Click save/bookmark on a post (LinkedIn added Saves feature)
**LLM Use Case**: "Save this post for later"

### 6. Unread Messages Filter

**Current Status**: Unread detection exists but no filter option
**Implementation**: Add `--unread` flag to messages command
**LLM Use Case**: "Show only unread messages"

**Code Sketch**:
```python
@app.command()
def messages(
    limit: int = typer.Option(10, help="Number of conversations to show"),
    unread_only: bool = typer.Option(False, "--unread", help="Show only unread"),
):
    # ... filter by m.get("unread") when unread_only is True
```

## Medium-Effort Improvements

### 7. Company Page Command

**Current Status**: URL pattern exists but no command
**Implementation**: Navigate to company page, extract info (size, industry, about)
**LLM Use Case**: "Tell me about Anthropic" / "What does OpenAI do?"

**Code Sketch**:
```python
@app.command()
def company(
    company_id: str = typer.Argument(..., help="Company name or LinkedIn company ID"),
):
    """View company page information."""
    client = get_client()
    client.navigate(LinkedInURLs.company(company_id))
    time.sleep(3)

    js_company = """
    (() => {
        const name = document.querySelector('h1.org-top-card-summary__title')?.textContent?.trim() || '';
        const industry = document.querySelector('.org-top-card-summary-info-list__info-item')?.textContent?.trim() || '';
        const about = document.querySelector('.org-page-details-module__card-spacing p')?.textContent?.trim() || '';
        const followers = document.querySelector('[data-test-id="about-us__followers"]')?.textContent?.trim() || '';
        return JSON.stringify({ name, industry, about, followers });
    })()
    """
```

### 8. Jobs Search Command

**Current Status**: URL exists but no command
**Implementation**: Navigate to jobs search, extract listings
**LLM Use Case**: "Find AI engineer jobs in SF" / "Search for remote Python jobs"

### 9. Create Post Command

**Current Status**: Not implemented
**Implementation**: Navigate to feed, click create post, enter text, submit
**LLM Use Case**: "Post this update to LinkedIn"

This is higher effort because:
- Need to handle text editor (contenteditable)
- May need to handle media attachments
- Post visibility options

### 10. Profile Sections (Experience, Education)

**Current Status**: Profile command only extracts name, headline, location, connections
**Implementation**: Extract experience, education, skills sections
**LLM Use Case**: "What's John's work history?" / "Where did Jane go to school?"

## Features NOT Exposed (with URLs/Selectors Ready)

| Feature | URL/Selector | Potential Use Case |
|---------|--------------|-------------------|
| Notifications | `LinkedInURLs.notifications()` | "Any new activity?" |
| Invitations | `LinkedInURLs.invitations()` | "Pending requests?" |
| Jobs | `LinkedInURLs.jobs()` | "Find jobs for me" |
| My Network | `LinkedInURLs.network()` | "Who should I connect with?" |
| Company pages | `LinkedInURLs.company()` | "Tell me about X company" |
| Groups search | `search(..., "groups")` | "Find LinkedIn groups" |

## Data Extraction Gaps

Current feed/post extraction ignores:
- **Media type** (image, video, document, poll)
- **Hashtags** in posts
- **Mentions** (@username) in posts
- **Link previews** / shared articles
- **Reaction types** (like, celebrate, support, funny, love, insightful)
- **Who reacted** (list of reactors)
- **Full comment threads** (currently only count)

Profile extraction ignores:
- **Experience** section (companies, roles, dates)
- **Education** section
- **Skills** section
- **Recommendations**
- **Activity** (recent posts)
- **Mutual connections**
- **Profile picture URL**

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | "LinkedIn interactions via browser automation" |
| What it does NOT do | Missing | Should clarify: no job applications, no data export, no analytics |
| Descriptive name | OK | cc_linkedin is clear |
| LLM use cases | OK | Examples provided in README |

### Documentation Recommendations

1. **Add "Limitations" section** to README:
   - Cannot apply to jobs (would require form filling)
   - Cannot export data (no bulk operations)
   - Cannot access LinkedIn Premium features
   - Rate limited by normal UI interaction speed

2. **Add "What This Tool Does NOT Do"**:
   - Does not scrape or export large amounts of data
   - Does not automate job applications
   - Does not manage LinkedIn ads or company pages

## Rate Limiting Considerations

LinkedIn actively detects automation. Recommendations:
- Add configurable delays between actions (already have `--delay` option)
- Add random jitter to delays
- Implement session persistence to avoid repeated logins
- Consider adding a "human-like" mode with longer random delays

## Notes

1. **LinkedIn UI changes frequently** - Selectors will need periodic updates
2. **Browser profile persistence** is critical - User must log in once, session persists
3. **No official API** - This is browser automation, not API access
4. **Premium features** - Some features may only be available to Premium users

## Sources

- [LinkedIn Updates 2026 - SocialBee](https://socialbee.com/blog/linkedin-updates/)
- [LinkedIn New Features - LinkedFusion](https://www.linkedfusion.io/blogs/linkedin-new-features-and-updates/)
- [LinkedIn Notifications Help](https://www.linkedin.com/help/linkedin/answer/a1341821)

---

**Audit Date:** 2026-02-17
**Tool Version:** 0.1.0
