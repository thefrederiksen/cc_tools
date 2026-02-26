# cc-linkedin Skill

LinkedIn CLI tool for interacting with LinkedIn via browser automation.

## When to Use

Use cc-linkedin when the user wants to:
- Check their LinkedIn feed or view posts
- Like or comment on LinkedIn posts
- View LinkedIn profiles
- Send connection requests
- Send messages to connections
- Search for people, posts, or companies on LinkedIn

## Prerequisites

1. **cc-browser daemon must be running** with a LinkedIn workspace logged in
2. Start with: `cc-browser daemon --workspace linkedin`
3. User must be logged into LinkedIn in that browser session

## Commands

### Status & Authentication
```bash
cc-linkedin status              # Check daemon and login status
cc-linkedin whoami              # Show logged-in user
cc-linkedin me                  # View own profile summary
```

### Feed & Content
```bash
cc-linkedin feed                # View home feed
cc-linkedin feed --limit 5      # Limit results
cc-linkedin post URL            # View specific post
cc-linkedin like URL            # Like a post
cc-linkedin comment URL --text "Great post!"  # Comment on post
cc-linkedin repost URL          # Repost to your feed
cc-linkedin repost URL --thoughts "Great insight!"  # Repost with comment
cc-linkedin save URL            # Save post for later
```

### Profiles & Networking
```bash
cc-linkedin profile USERNAME    # View someone's profile
cc-linkedin connections         # List your connections
cc-linkedin connect USERNAME    # Send connection request
cc-linkedin connect USERNAME --note "Message"  # With note
cc-linkedin company anthropic   # View company page
```

### Invitations
```bash
cc-linkedin invitations         # View pending connection requests
cc-linkedin accept "John"       # Accept invitation from John
cc-linkedin ignore "John"       # Ignore invitation from John
```

### Notifications
```bash
cc-linkedin notifications       # View all notifications
cc-linkedin notifications --unread  # Show only unread
```

### Messaging
```bash
cc-linkedin messages            # View recent messages
cc-linkedin messages --unread   # Show only unread messages
cc-linkedin message USERNAME --text "Hello!"  # Send message
```

### Search & Jobs
```bash
cc-linkedin search "query"                    # Search all
cc-linkedin search "query" --type people      # Search people
cc-linkedin search "query" --type posts       # Search posts
cc-linkedin search "query" --type companies   # Search companies
cc-linkedin jobs "AI engineer"                # Search for jobs
cc-linkedin jobs "Python" --location "Remote" # Jobs with location
```

### Navigation & Debug
```bash
cc-linkedin goto URL            # Navigate to URL
cc-linkedin snapshot            # Get page snapshot
cc-linkedin screenshot          # Take screenshot
```

## Global Options

- `--port INT`: cc-browser daemon port (default 9280)
- `--format TEXT`: Output format (text/json/markdown)
- `--delay FLOAT`: Delay between actions (default 1.0)
- `-v, --verbose`: Verbose output for debugging

## Usage Patterns

### Check Activity
```bash
# Ensure daemon is running
cc-linkedin status

# Check notifications
cc-linkedin notifications --unread

# View feed
cc-linkedin feed --limit 10
```

### Engage with Content
```bash
# View a post
cc-linkedin post "https://www.linkedin.com/feed/update/urn:li:activity:1234567890"

# Like it
cc-linkedin like "https://www.linkedin.com/feed/update/urn:li:activity:1234567890"

# Comment
cc-linkedin comment "https://www.linkedin.com/feed/update/urn:li:activity:1234567890" --text "Great insights!"

# Repost with your thoughts
cc-linkedin repost "https://www.linkedin.com/feed/update/urn:li:activity:1234567890" --thoughts "Must read!"

# Save for later
cc-linkedin save "https://www.linkedin.com/feed/update/urn:li:activity:1234567890"
```

### Manage Invitations
```bash
# Check pending invitations
cc-linkedin invitations

# Accept specific person
cc-linkedin accept "John Smith"

# Ignore spam
cc-linkedin ignore "Recruiter"
```

### Networking Workflow
```bash
# Search for relevant people
cc-linkedin search "software engineer at Microsoft" --type people

# View their profile
cc-linkedin profile johndoe

# Research their company
cc-linkedin company microsoft

# Send connection request
cc-linkedin connect johndoe --note "Hi! I noticed we share similar interests in cloud architecture."
```

### Job Search
```bash
# Search for jobs
cc-linkedin jobs "AI engineer" --location "San Francisco"

# Search remote jobs
cc-linkedin jobs "Python developer" --location "Remote"
```

### Messaging
```bash
# Check unread messages
cc-linkedin messages --unread

# Send a message
cc-linkedin message janedoe --text "Thanks for connecting! Would love to chat about your recent project."
```

## Output Formats

```bash
# Default text output
cc-linkedin feed

# JSON output (for parsing)
cc-linkedin feed --format json

# Markdown output
cc-linkedin profile johndoe --format markdown
```

## Troubleshooting

### "Cannot connect to cc-browser daemon"
- Start the daemon: `cc-browser daemon --workspace linkedin`

### "Not logged in"
- Open LinkedIn in the browser and log in
- The browser session persists with the profile

### "Could not find button"
- LinkedIn's UI changes frequently
- Use `cc-linkedin snapshot` to see available elements
- Report issues if selectors need updating

## Notes

- All interactions happen through browser automation (like a real user)
- No API keys required - uses existing browser session
- Rate limiting: Use `--delay` option to avoid triggering LinkedIn's detection
- LinkedIn may require CAPTCHA verification occasionally
