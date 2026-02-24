# cc-outlook

Outlook CLI for Claude Code: read, send, search emails and manage calendar from the command line.

**Requirement:** `cc-outlook.exe` must be in PATH (install via `install.bat` in cc-tools repo)

---

## CRITICAL: Authentication Setup

Before using cc-outlook, you MUST set up Azure authentication:

### Azure App Registration (One-Time)

1. Go to https://portal.azure.com
2. Search "App registrations" -> "+ New registration"
3. Settings:
   - Name: `cc-outlook_cli`
   - Account types: **Accounts in any organizational directory and personal Microsoft accounts**
   - Redirect URI: Mobile and desktop -> `http://localhost`
4. Copy the **Application (client) ID**
5. API permissions -> Add (Delegated): `Mail.ReadWrite`, `Mail.Send`, `Calendars.ReadWrite`, `User.Read`, `MailboxSettings.Read`
6. **CRITICAL**: Authentication -> Add URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
7. Enable: **Allow public client flows** = Yes

### Add Account

```bash
cc-outlook accounts add your@email.com --client-id YOUR_CLIENT_ID
cc-outlook auth
```

### Authentication Flow - IMPORTANT

During `cc-outlook auth`:
1. Browser opens -> Sign in -> Accept permissions
2. **You'll see "This is not the right page"** - THIS IS NORMAL
3. **Copy the ENTIRE URL** from the browser address bar
4. **Paste it into the terminal** and press Enter

---

## Quick Reference

```bash
# List inbox
cc-outlook list

# Read email
cc-outlook read <message_id>

# Send email
cc-outlook send -t "to@example.com" -s "Subject" -b "Body text"

# Search
cc-outlook search "project update"

# Show profile
cc-outlook profile

# Calendar events
cc-outlook calendar events
```

---

## Email Commands

### List Emails

```bash
cc-outlook list                    # List inbox (default 10)
cc-outlook list -n 20              # List 20 messages
cc-outlook list -f sent            # List sent mail
cc-outlook list -f drafts          # List drafts
cc-outlook list --unread           # Show unread only
cc-outlook -a work list            # List from 'work' account
```

### Read Email

```bash
cc-outlook read <message_id>       # Read full email
cc-outlook read <message_id> --raw # Show raw data
```

### Send Email

```bash
# Basic send
cc-outlook send -t "to@example.com" -s "Subject" -b "Body text"

# Send with body from file
cc-outlook send -t "to@example.com" -s "Subject" -f body.txt

# Send HTML
cc-outlook send -t "to@example.com" -s "Subject" -f email.html --html

# Send with CC/BCC
cc-outlook send -t "to@example.com" -s "Subject" -b "Body" --cc "cc@example.com" --bcc "bcc@example.com"

# Send with attachments
cc-outlook send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf --attach data.xlsx

# Send with importance
cc-outlook send -t "to@example.com" -s "Urgent" -b "Important" --importance high

# Send from specific account
cc-outlook -a work send -t "colleague@company.com" -s "Update" -b "Here's the update"
```

### Create Draft

```bash
cc-outlook draft -t "to@example.com" -s "Subject" -b "Draft body"
cc-outlook draft -t "to@example.com" -s "Subject" -f draft.txt
```

### Search

```bash
cc-outlook search "quarterly report"
cc-outlook search "from sender" -n 20
cc-outlook search "invoice" -f sent
```

### Delete

```bash
cc-outlook delete <message_id>             # Delete message
cc-outlook delete <message_id> --permanent # Permanently delete
cc-outlook delete <message_id> -y          # Skip confirmation
```

### Folders

```bash
cc-outlook folders                 # List all folders with counts
```

### Profile

```bash
cc-outlook profile                 # Show authenticated user info
```

---

## Calendar Commands

### List Calendars

```bash
cc-outlook calendar list
```

### View Events

```bash
cc-outlook calendar events         # Next 7 days
cc-outlook calendar events -d 14   # Next 14 days
cc-outlook calendar events -c "Work Calendar"
```

### Create Event

```bash
# Basic event (60 min default)
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00

# With duration
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 --duration 90

# With location
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 -l "Room A"

# With attendees
cc-outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 --attendees "a@x.com,b@x.com"

# All-day event
cc-outlook calendar create -s "Holiday" -d 2024-12-25 -t 00:00 --all-day
```

---

## Multiple Accounts

cc-outlook supports multiple Outlook accounts.

```bash
# List accounts
cc-outlook accounts list

# Add account
cc-outlook accounts add work --client-id YOUR_CLIENT_ID

# Set default
cc-outlook accounts default work

# Use specific account with any command
cc-outlook -a personal list
cc-outlook --account work send -t "to@example.com" -s "Subject" -b "Body"
```

---

## Authentication

```bash
# Authenticate (opens browser)
cc-outlook auth

# Force re-authentication
cc-outlook auth --force

# Revoke token
cc-outlook auth --revoke
```

---

## Troubleshooting

### "Reply URL does not match" Error

Add BOTH redirect URIs in Azure Authentication:
- `https://login.microsoftonline.com/common/oauth2/nativeclient`
- `http://localhost`

### "This is not the right page"

THIS IS NORMAL! Copy the URL and paste it in the terminal.

### Token Expired

```bash
cc-outlook auth --force
```

### Account Not Found

```bash
cc-outlook accounts add your@email.com --client-id YOUR_CLIENT_ID
cc-outlook auth
```

---

## Common Tasks

### Check for new messages
```bash
cc-outlook list --unread -n 5
```

### Send a quick reply
```bash
cc-outlook send -t "colleague@example.com" -s "Re: Question" -b "Yes, that works for me."
```

### Send document with attachments
```bash
cc-outlook send -t "client@example.com" -s "Documents" -b "Please find attached." --attach doc1.pdf --attach doc2.pdf
```

### View upcoming meetings
```bash
cc-outlook calendar events -d 3
```

### Schedule a meeting
```bash
cc-outlook calendar create -s "Project Review" -d 2024-12-20 -t 10:00 --duration 60 --attendees "team@company.com"
```

---

## Configuration

| Location | Purpose |
|----------|---------|
| `~/.cc-outlook/profiles.json` | Account configurations |
| `~/.cc-outlook/tokens/` | OAuth tokens |

---

## License

MIT - https://github.com/CenterConsulting/cc-tools
