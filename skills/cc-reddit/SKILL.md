# cc-reddit

Reddit CLI via browser automation. Read posts, comment, vote, and manage subreddits.

**Requirements:**
- `cc-reddit` must be available (Python)
- cc-browser daemon must be running
- Logged into Reddit in the browser

---

## Quick Reference

```bash
# Check status
cc-reddit status

# Check login
cc-reddit whoami

# View subreddit feed
cc-reddit feed python

# View a post
cc-reddit post URL

# Navigate to subreddit
cc-reddit goto r/programming
```

---

## Setup

```bash
# 1. Start cc-browser daemon
cc-browser daemon

# 2. Start browser and log into Reddit manually
cc-browser start
cc-browser navigate --url "https://reddit.com/login"
# Log in manually in the browser

# 3. Now cc-reddit commands will work
cc-reddit whoami
```

---

## Commands

### Status & Login

```bash
# Check daemon and browser status
cc-reddit status

# Check logged-in username
cc-reddit whoami
```

### Navigation

```bash
# Go to subreddit
cc-reddit goto r/python
cc-reddit goto programming  # r/ prefix optional

# Go to user profile
cc-reddit goto u/username

# Go to any Reddit URL
cc-reddit goto "https://reddit.com/r/python/hot"
```

### Reading

```bash
# View subreddit feed
cc-reddit feed python
cc-reddit feed home          # Front page
cc-reddit feed python --sort new
cc-reddit feed python --sort top
cc-reddit feed python --limit 20

# View a specific post
cc-reddit post URL
cc-reddit post "https://reddit.com/r/python/comments/abc123"
```

### Commenting

```bash
# Comment on a post
cc-reddit comment URL --text "Great post!"
cc-reddit comment URL -t "I agree with this point"
```

### Voting

```bash
# Upvote
cc-reddit upvote URL

# Downvote
cc-reddit downvote URL
```

### Subreddit Management

```bash
# Join a subreddit
cc-reddit join python

# Leave a subreddit
cc-reddit leave python
```

### Utilities

```bash
# Get page snapshot (for debugging)
cc-reddit snapshot

# Take screenshot
cc-reddit screenshot --output reddit.png
```

---

## Options

| Option | Description |
|--------|-------------|
| `--port` | cc-browser daemon port (default: 9280) |
| `--format` | Output format: text, json, markdown |
| `--delay` | Delay between actions (seconds) |
| `-v, --verbose` | Verbose output |

---

## Feed Sorting

| Sort | Description |
|------|-------------|
| `hot` | Hot posts (default) |
| `new` | Newest posts |
| `top` | Top posts |
| `rising` | Rising posts |

---

## Examples

### Browse Reddit

```bash
# Check what subreddits have interesting content
cc-reddit feed programming --sort hot --limit 10
cc-reddit feed python --sort top
```

### Read and Comment

```bash
# 1. Find an interesting post
cc-reddit feed learnpython --limit 5

# 2. Read a post
cc-reddit post "https://reddit.com/r/learnpython/comments/abc123"

# 3. Comment
cc-reddit comment "https://reddit.com/r/learnpython/comments/abc123" \
  --text "Here's a tip: use list comprehensions for this!"
```

### Manage Subscriptions

```bash
# Join interesting subreddits
cc-reddit join machinelearning
cc-reddit join datascience
cc-reddit join python

# Leave one you don't like
cc-reddit leave memes
```

### Upvote Good Content

```bash
cc-reddit upvote "https://reddit.com/r/python/comments/helpful_post"
```

---

## Tips

1. **Login first** - Use cc-browser to log into Reddit before using cc-reddit
2. **Rate limiting** - Reddit may rate-limit rapid actions; use `--delay` if needed
3. **Verbose mode** - Use `-v` to see what elements are being detected
4. **Snapshot** - Use `cc-reddit snapshot` to debug element detection issues

---

## Requires cc-browser

cc-reddit uses cc-browser for browser automation. Ensure:
1. cc-browser daemon is running (`cc-browser daemon`)
2. Browser is started (`cc-browser start`)
3. You're logged into Reddit in the browser

---

## LLM Use Cases

1. **Reddit browsing** - "Check the top posts in r/programming"
2. **Research** - "Find recent posts about Python asyncio"
3. **Engagement** - "Upvote this helpful answer"
4. **Community management** - "Join these subreddits for learning"
5. **Posting** - "Comment on this post with my response"
