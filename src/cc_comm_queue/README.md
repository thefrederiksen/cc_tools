# cc_comm_queue

CLI tool for adding content to the Communication Manager approval queue.

## Installation

```bash
# From source
cd D:\ReposFred\cc_tools\src\cc_comm_queue
pip install -e .

# Build executable
.\build.ps1
```

## Usage

### Add Content

```bash
# LinkedIn post
cc_comm_queue add linkedin post "Process mining trends for 2024..." \
    --persona mindzie \
    --tags "process mining,trends"

# LinkedIn comment
cc_comm_queue add linkedin comment "Great insights!" \
    --persona personal \
    --context-url "https://linkedin.com/posts/..."

# Email
cc_comm_queue add email email "Hi Sarah, following up..." \
    --persona mindzie \
    --email-to "sarah@techcorp.com" \
    --email-subject "Following up from Summit"

# Reddit post
cc_comm_queue add reddit post "How we reduced processing time..." \
    --persona personal \
    --reddit-subreddit "r/processimprovement" \
    --reddit-title "Case Study: 70% reduction"
```

### JSON Input

```bash
# From file
cc_comm_queue add-json content.json

# From stdin
cat content.json | cc_comm_queue add-json -
```

### Queue Management

```bash
# List pending items
cc_comm_queue list --status pending

# Show queue stats
cc_comm_queue status

# Show specific item
cc_comm_queue show abc123
```

### Configuration

```bash
# Show config
cc_comm_queue config show

# Set queue path
cc_comm_queue config set queue_path "D:/path/to/content"

# Set default persona
cc_comm_queue config set default_persona mindzie
```

## JSON Output (for Agents)

Use `--json` flag for machine-readable output:

```bash
cc_comm_queue add linkedin post "Hello" --json
# {"success": true, "id": "abc123...", "file": "path/to/file.json"}
```

## Supported Platforms

- `linkedin` - LinkedIn posts, comments, messages
- `twitter` - Tweets, replies, threads
- `reddit` - Posts and comments
- `youtube` - Comments
- `email` - Emails via cc_outlook
- `blog` - Long-form articles

## Personas

- `mindzie` - CTO of mindzie
- `center_consulting` - President of Center Consulting
- `personal` - Soren Frederiksen
