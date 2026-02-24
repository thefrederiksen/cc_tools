# cc-gmail

Gmail CLI for Claude Code: read, send, search, and manage emails from the command line.

**Requirement:** `cc-gmail.exe` must be in PATH (install via `install.bat` in cc-tools repo)

---

## Quick Reference

```bash
# List inbox
cc-gmail list

# Read email
cc-gmail read <message_id>

# Send email
cc-gmail send -t "to@example.com" -s "Subject" -b "Body text"

# Search
cc-gmail search "from:someone@example.com"

# Show profile
cc-gmail profile
```

---

## Commands

### List Emails

```bash
cc-gmail list                    # List inbox (default 10)
cc-gmail list -n 20              # List 20 messages
cc-gmail list -l SENT            # List sent mail
cc-gmail list -l DRAFT           # List drafts
cc-gmail list --unread           # Show unread only
cc-gmail -a work list            # List from 'work' account
```

### Read Email

```bash
cc-gmail read <message_id>       # Read full email
cc-gmail read <message_id> --raw # Show raw data
```

### Send Email

```bash
# Basic send
cc-gmail send -t "to@example.com" -s "Subject" -b "Body text"

# Send with body from file
cc-gmail send -t "to@example.com" -s "Subject" -f body.txt

# Send HTML
cc-gmail send -t "to@example.com" -s "Subject" -f email.html --html

# Send with CC/BCC
cc-gmail send -t "to@example.com" -s "Subject" -b "Body" --cc "cc@example.com" --bcc "bcc@example.com"

# Send with attachments
cc-gmail send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf --attach data.xlsx

# Send from specific account
cc-gmail -a work send -t "colleague@company.com" -s "Update" -b "Here's the update"
```

### Create Draft

```bash
cc-gmail draft -t "to@example.com" -s "Subject" -b "Draft body"
cc-gmail draft -t "to@example.com" -s "Subject" -f draft.txt
```

### Search

```bash
cc-gmail search "from:boss@company.com"
cc-gmail search "subject:important is:unread"
cc-gmail search "has:attachment after:2024/01/01"
cc-gmail search "in:sent to:client@example.com"
```

### Delete

```bash
cc-gmail delete <message_id>             # Move to trash
cc-gmail delete <message_id> --permanent # Permanently delete
cc-gmail delete <message_id> -y          # Skip confirmation
```

### Labels

```bash
cc-gmail labels                  # List all labels/folders
```

### Profile

```bash
cc-gmail profile                 # Show authenticated user info
```

---

## Multiple Accounts

cc-gmail supports multiple Gmail accounts.

```bash
# List accounts
cc-gmail accounts list

# Add account
cc-gmail accounts add work

# Set default
cc-gmail accounts default work

# Use specific account with any command
cc-gmail -a personal list
cc-gmail --account work send -t "to@example.com" -s "Subject" -b "Body"
```

---

## Gmail Search Syntax

| Query | Description |
|-------|-------------|
| `from:email` | Messages from sender |
| `to:email` | Messages to recipient |
| `subject:word` | Subject contains word |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `has:attachment` | Has attachments |
| `after:YYYY/MM/DD` | After date |
| `before:YYYY/MM/DD` | Before date |
| `label:name` | Has label |
| `in:inbox` | In inbox |
| `in:sent` | In sent |

Combine queries: `from:boss@company.com subject:report after:2024/01/01`

---

## Authentication

```bash
# Authenticate (opens browser)
cc-gmail auth

# Force re-authentication
cc-gmail auth --force

# Revoke token
cc-gmail auth --revoke
```

---

## Setup (First Time)

1. Create OAuth credentials at Google Cloud Console
2. Enable Gmail API for your project
3. Add account: `cc-gmail accounts add personal`
4. Copy credentials.json to `~/.cc-gmail/accounts/personal/`
5. Run: `cc-gmail auth`

See full setup: https://github.com/CenterConsulting/cc-tools/tree/main/src/cc-gmail

---

## Common Tasks

### Check for new messages
```bash
cc-gmail list --unread -n 5
```

### Find recent emails from someone
```bash
cc-gmail search "from:important@example.com after:2024/01/01" -n 10
```

### Send a quick reply
```bash
cc-gmail send -t "colleague@example.com" -s "Re: Question" -b "Yes, that works for me."
```

### Send document with attachments
```bash
cc-gmail send -t "client@example.com" -s "Documents" -b "Please find attached." --attach doc1.pdf --attach doc2.pdf
```

---

## License

MIT - https://github.com/CenterConsulting/cc-tools
