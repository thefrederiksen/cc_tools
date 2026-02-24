# cc_tool_audit: cc_reddit

## Summary

- **Tool**: cc_reddit
- **Underlying System**: cc_browser (Playwright-based browser automation) -> Reddit Web UI
- **Current Commands**: 14 (status, whoami, me, goto, feed, post, comment, upvote, downvote, join, leave, snapshot, screenshot)
- **PRD Coverage**: ~40% of P0/P1 requirements implemented
- **Quick Wins Found**: 8

## Current Implementation Analysis

### Implemented Commands

| Command | Status | Notes |
|---------|--------|-------|
| `status` | OK | Checks daemon/browser/Reddit status |
| `whoami` | OK | Detects logged-in username via JS |
| `me` | OK | Shows user's posts and comments |
| `goto` | OK | Navigate to any Reddit URL |
| `feed` | Partial | Shows posts but output is raw snapshot |
| `post` | OK | Views single post with metadata extraction |
| `comment` | OK | Posts comment on a post |
| `upvote` | OK | Clicks upvote button |
| `downvote` | OK | Clicks downvote button |
| `join` | OK | Joins subreddit |
| `leave` | OK | Leaves subreddit |
| `snapshot` | OK | Debug: raw page snapshot |
| `screenshot` | OK | Saves page screenshot |

### Not Implemented (from PRD)

| Feature | PRD Priority | LLM Value |
|---------|--------------|-----------|
| `search` | P0 | HIGH |
| `post create` (new post) | P0 | HIGH |
| `reply` (to comment) | P0 | HIGH |
| `inbox` | P1 | HIGH |
| `saved` | P1 | MEDIUM |
| `user` (view other users) | P0 | MEDIUM |
| `subreddit` (info/rules) | P1 | MEDIUM |
| `subscriptions` (list) | P1 | MEDIUM |
| `message` (DM) | P1 | MEDIUM |
| `edit` | P1 | LOW |
| `delete` | P1 | LOW |
| Moderation commands | P2 | LOW (niche) |

---

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Use Case |
|----------|---------|--------|-----------|----------|
| 1 | `search` command | Small | HIGH | "Find posts about X in r/python" |
| 2 | `create` command (new post) | Small | HIGH | "Post this to r/learnpython" |
| 3 | `reply` command | Trivial | HIGH | "Reply to this comment" |
| 4 | `inbox` command | Small | HIGH | "Do I have any messages?" |
| 5 | `user` command | Small | MEDIUM | "Show me u/spez's recent posts" |
| 6 | `saved` command | Trivial | MEDIUM | "What did I save recently?" |
| 7 | Improve `feed` output | Trivial | HIGH | Structured post list vs raw snapshot |
| 8 | `karma` command | Trivial | MEDIUM | "What's my karma?" |

---

## Quick Wins (Trivial Effort, High LLM Value)

### 1. `reply` Command

**Current Status**: Not implemented (comment only works on posts)
**Implementation**: Reuse `comment` logic but target comment reply button
**LLM Use Case**: "Reply to this comment saying thanks"

**Code Sketch**:
```python
@app.command()
def reply(
    comment_url: str = typer.Argument(..., help="Comment URL to reply to"),
    text: str = typer.Option(..., "--text", "-t", help="Reply text"),
):
    """Reply to a comment."""
    client = get_client()
    client.navigate(comment_url)
    # Click reply button, type text, submit
    # Same pattern as comment command
```

### 2. Improve `feed` Output

**Current Status**: Returns raw snapshot lines
**Implementation**: Use JS extraction like `me` command does
**LLM Use Case**: "Show me top 5 posts from r/python" -> clean table output

**Code Sketch**:
```python
# In feed command, replace snapshot parsing with:
js_posts = """
(() => {
    const posts = document.querySelectorAll("shreddit-post");
    const data = [];
    for (const post of posts) {
        data.push({
            title: post.getAttribute("post-title"),
            subreddit: post.getAttribute("subreddit-prefixed-name"),
            score: post.getAttribute("score"),
            comments: post.getAttribute("comment-count"),
            url: post.getAttribute("permalink")
        });
    }
    return JSON.stringify(data);
})()
"""
# Then render as table like `me` command
```

### 3. `saved` Command

**Current Status**: Not implemented
**Implementation**: Navigate to /user/me/saved, extract posts
**LLM Use Case**: "What posts did I save about Python?"

**Code Sketch**:
```python
@app.command()
def saved(limit: int = typer.Option(10)):
    """View your saved posts and comments."""
    client = get_client()
    client.navigate("https://www.reddit.com/user/me/saved")
    # Use same JS extraction as `me` command
```

### 4. `karma` Command

**Current Status**: Not implemented
**Implementation**: Extract karma from profile page
**LLM Use Case**: "What's my karma?"

**Code Sketch**:
```python
@app.command()
def karma():
    """Show your karma breakdown."""
    client = get_client()
    client.navigate("https://www.reddit.com/user/me")
    # Extract karma via JS from profile
```

---

## Small-Effort Improvements

### 5. `search` Command

**Current Status**: Not implemented
**Implementation**: Navigate to search URL, extract results
**LLM Use Case**: "Find posts about async Python in r/python"

**Code Sketch**:
```python
@app.command()
def search(
    query: str = typer.Argument(...),
    subreddit: str = typer.Option(None, "--subreddit", "-r"),
    sort: str = typer.Option("relevance", help="relevance, hot, top, new"),
    limit: int = typer.Option(10),
):
    """Search Reddit."""
    if subreddit:
        url = f"https://www.reddit.com/r/{subreddit}/search?q={query}&restrict_sr=1"
    else:
        url = f"https://www.reddit.com/search?q={query}"

    client.navigate(url)
    # Extract search results using JS
```

### 6. `create` Command (New Post)

**Current Status**: Not implemented
**Implementation**: Navigate to submit page, fill form, submit
**LLM Use Case**: "Post 'Hello World' to r/test"

**Code Sketch**:
```python
@app.command()
def create(
    subreddit: str = typer.Argument(...),
    title: str = typer.Option(..., "--title", "-t"),
    body: str = typer.Option(None, "--body", "-b"),
    url: str = typer.Option(None, "--url", "-u"),
):
    """Create a new post."""
    client = get_client()
    client.navigate(f"https://www.reddit.com/r/{subreddit}/submit")
    # Fill title, select text/link tab, fill body/url, submit
```

### 7. `inbox` Command

**Current Status**: Not implemented
**Implementation**: Navigate to inbox, extract messages
**LLM Use Case**: "Do I have any unread messages?"

**Code Sketch**:
```python
@app.command()
def inbox(unread: bool = typer.Option(False)):
    """View your inbox."""
    url = "https://www.reddit.com/message/unread" if unread else "https://www.reddit.com/message/inbox"
    client.navigate(url)
    # Extract messages from page
```

### 8. `user` Command

**Current Status**: Not implemented
**Implementation**: Navigate to user profile, extract info
**LLM Use Case**: "Show me u/GallowBoob's top posts"

**Code Sketch**:
```python
@app.command()
def user(
    username: str = typer.Argument(...),
    posts: bool = typer.Option(True, "--posts/--no-posts"),
    comments: bool = typer.Option(False, "--comments/--no-comments"),
):
    """View a user's profile."""
    base = f"https://www.reddit.com/user/{username}"
    if posts:
        client.navigate(f"{base}/submitted")
    # Similar to `me` command but for any user
```

---

## Browser Client Capabilities Not Used

The `browser_client.py` wraps cc_browser but several capabilities are unused:

| Capability | Used | Potential Use |
|------------|------|---------------|
| `text()` | No | Extract all page text |
| `html()` | No | Get raw HTML for parsing |
| `fill()` | No | Fill forms (post creation) |
| `upload()` | No | Image post uploads |
| `tabs_*` | No | Multi-tab workflows |
| `hover()` | No | Trigger dropdowns |
| `select()` | No | Dropdown selections |
| `wait_for_text()` | No | Wait for page load confirmation |

### Recommendation: Use `fill()` for Forms

The `fill()` method can fill multiple fields at once, which would simplify post creation:

```python
client.fill([
    {"ref": "title_ref", "text": "My Post Title"},
    {"ref": "body_ref", "text": "Post body content"}
])
```

---

## Output Format Improvements

### Current Issue

The `--format` option is defined but not fully utilized:
- JSON output works via `console.print_json()`
- Markdown output just wraps JSON in code blocks
- Most commands ignore the format option

### Recommendation

Create consistent output models:

```python
# In models.py
class PostSummary(BaseModel):
    title: str
    subreddit: str
    score: int
    comments: int
    url: str

# In cli.py
def output_posts(posts: list[PostSummary]):
    if config.format == "json":
        console.print_json([p.model_dump() for p in posts])
    elif config.format == "markdown":
        for p in posts:
            console.print(f"- [{p.title}]({p.url}) ({p.score} pts)")
    else:
        # Table output
```

---

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | README explains browser automation approach |
| What it does NOT do | Missing | Should clarify: no API, requires login, no chat |
| Descriptive name | OK | `cc_reddit` is clear |
| LLM use cases | Missing | Should add examples like "Ask Claude to post" |

### Recommendations

1. Add "Limitations" section to README:
   - Requires manual login first
   - No Reddit Chat support
   - Rate limiting is user's responsibility

2. Add "LLM Usage Examples" section:
   ```
   ## Using with Claude Code

   "Check my Reddit inbox"
   -> cc_reddit inbox --unread

   "Post this link to r/programming"
   -> cc_reddit create programming --title "..." --url "..."

   "What are the hot posts in r/python?"
   -> cc_reddit feed python --sort hot --limit 5
   ```

---

## Risk Considerations

### Reddit's Anti-Bot Measures

Reddit may detect automation patterns. Recommendations:
1. Keep `--delay` option (already exists)
2. Add jitter to delays (randomize slightly)
3. Don't expose batch operations that could spam

### Session Persistence

Current implementation relies on browser profile login. Good approach because:
- No API keys to manage
- Uses Reddit's own session handling
- 2FA handled by browser

---

## Next Steps

1. **Immediate** (Quick Wins):
   - Improve `feed` output with JS extraction
   - Add `reply` command
   - Add `saved` command
   - Add `karma` command

2. **Short-term** (Small Effort):
   - Add `search` command
   - Add `create` command for new posts
   - Add `inbox` command
   - Add `user` command

3. **Documentation**:
   - Add limitations section
   - Add LLM usage examples
   - Update PRD checkboxes

---

## Appendix: PRD Checklist Update

Based on this audit, the PRD implementation phases should be updated:

### Phase 1: Foundation (MVP) - MOSTLY COMPLETE
- [x] Directory structure
- [x] CLI scaffolding with Typer
- [x] cc_browser HTTP client wrapper
- [x] Reddit page detection and navigation
- [x] `status` command
- [x] `whoami` command
- [x] `feed` command (needs output improvement)
- [x] `post` command (view post)

### Phase 2: Reading & Navigation - PARTIAL
- [ ] `comments` command (separate from post view)
- [ ] `search` command <- HIGH PRIORITY
- [ ] `user` command <- MEDIUM PRIORITY
- [ ] `subreddit` command
- [ ] JSON/markdown output formats (partial)

### Phase 3: Writing & Engagement - PARTIAL
- [ ] `post create` command <- HIGH PRIORITY
- [x] `comment` command
- [ ] `reply` command <- QUICK WIN
- [x] `upvote` / `downvote` commands
- [x] `join` / `leave` commands

### Phase 4: Advanced Features - NOT STARTED
- [ ] `inbox` command <- HIGH PRIORITY
- [ ] `message` command
- [ ] `saved` command <- QUICK WIN
- [ ] `edit` / `delete` commands

---

**Audit Generated**: 2026-02-17
**Auditor**: Claude (cc_tool_audit skill)
