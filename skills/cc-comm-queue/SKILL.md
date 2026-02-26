# cc-comm-queue

CLI tool for adding content to the Communication Manager approval queue. All outgoing communications (LinkedIn posts, emails, Reddit posts) must be queued for human review before sending.

## Commands

```bash
# Add LinkedIn post
cc-comm-queue add linkedin post "Post content here" --persona personal --tags "tag1,tag2"

# Add LinkedIn comment
cc-comm-queue add linkedin comment "Great insights!" --context-url "https://linkedin.com/posts/..."

# Add email
cc-comm-queue add email email "Email body" --email-to "to@example.com" --email-subject "Subject"

# Add Reddit post
cc-comm-queue add reddit post "Post content" --reddit-subreddit "r/subreddit" --reddit-title "Title"

# Add from JSON file
cc-comm-queue add-json content.json

# List pending items
cc-comm-queue list --status pending

# Show queue stats
cc-comm-queue status

# Show specific item
cc-comm-queue show <item_id>

# Configuration
cc-comm-queue config show
cc-comm-queue config set queue_path "D:/path/to/content"
```

## Options

| Option | Description |
|--------|-------------|
| `--persona, -p` | Persona: personal, mindzie, center_consulting |
| `--tags, -t` | Comma-separated tags |
| `--context-url, -c` | URL being responded to |
| `--json` | JSON output for agents |
| `--email-to` | Recipient email |
| `--email-subject` | Email subject |
| `--reddit-subreddit` | Target subreddit |
| `--reddit-title` | Reddit post title |

## Platforms

linkedin, twitter, reddit, youtube, email, blog
