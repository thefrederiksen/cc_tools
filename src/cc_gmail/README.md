# cc_gmail

Gmail CLI: read, send, search, and manage emails from the command line.

Supports **multiple Gmail accounts** with easy switching between them.

## Quick Start

```bash
# 1. Add your first account
cc_gmail accounts add personal

# 2. Follow the setup instructions (see below)
# 3. Place credentials.json in the account folder
# 4. Authenticate
cc_gmail auth

# 5. Start using Gmail from the command line
cc_gmail list
```

---

## Google Cloud Setup (Required)

Before using cc_gmail, you need OAuth credentials from Google Cloud Console.
This is a one-time setup per Google account.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a name (e.g., "cc_gmail")
5. Click "Create"

### Step 2: Enable the Gmail API

1. In your project, go to **APIs & Services** -> **Library**
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click **Enable**

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** -> **OAuth consent screen**
2. Select **External** (or Internal if using Google Workspace)
3. Click "Create"
4. Fill in required fields:
   - App name: `cc_gmail`
   - User support email: Your email
   - Developer contact: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.compose`
   - `https://www.googleapis.com/auth/gmail.modify`
8. Click "Save and Continue"
9. On "Test users" page, click "Add Users"
10. Add your Gmail address(es)
11. Click "Save and Continue"

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** -> **Credentials**
2. Click **Create Credentials** -> **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `cc_gmail`
5. Click "Create"
6. Click **Download JSON** (download icon)
7. Save the file - you'll need it in the next step

### Step 5: Add Account to cc_gmail

```bash
# Add an account (e.g., "personal" or "work")
cc_gmail accounts add personal
```

This will show you where to place the credentials file:

```
~/.cc_gmail/accounts/personal/credentials.json
```

Copy your downloaded JSON file to that location, then authenticate:

```bash
cc_gmail auth
```

A browser window will open. Sign in with your Gmail account and grant permissions.

---

## Managing Multiple Accounts

cc_gmail supports multiple Gmail accounts. Each account has its own credentials
and can be used independently.

### Add Multiple Accounts

```bash
# Add personal account
cc_gmail accounts add personal --default

# Add work account
cc_gmail accounts add work

# Add another account
cc_gmail accounts add side-project
```

Each account needs its own `credentials.json` file in its folder.
You can use the same Google Cloud project credentials for multiple Gmail accounts.

### List Accounts

```bash
cc_gmail accounts list
```

Output:
```
+----------+---------+-------------+---------------+
| Account  | Default | Credentials | Authenticated |
+----------+---------+-------------+---------------+
| personal | *       | OK          | Yes           |
| work     |         | OK          | Yes           |
+----------+---------+-------------+---------------+
```

### Switch Default Account

```bash
cc_gmail accounts default work
```

### Use Specific Account

```bash
# Use --account (or -a) flag with any command
cc_gmail --account work list
cc_gmail -a personal search "from:mom"
```

### Check Account Status

```bash
cc_gmail accounts status personal
```

### Remove Account

```bash
cc_gmail accounts remove old-account
```

---

## Commands

### Authentication

```bash
# Authenticate current/default account
cc_gmail auth

# Force re-authentication
cc_gmail auth --force

# Revoke token (requires re-auth)
cc_gmail auth --revoke
```

### List Emails

```bash
# List inbox (default)
cc_gmail list

# List with options
cc_gmail list -l INBOX -n 20
cc_gmail list --label SENT --count 5
cc_gmail list --unread

# List from specific account
cc_gmail -a work list
```

### Read Email

```bash
# Read a specific email by ID
cc_gmail read <message_id>

# Show raw message data
cc_gmail read <message_id> --raw
```

### Send Email

```bash
# Send with body text
cc_gmail send -t "recipient@example.com" -s "Subject" -b "Body text"

# Send with body from file
cc_gmail send -t "recipient@example.com" -s "Subject" -f body.txt

# Send with CC/BCC
cc_gmail send -t "to@example.com" -s "Subject" -b "Body" --cc "cc@example.com"

# Send HTML email
cc_gmail send -t "to@example.com" -s "Subject" -f email.html --html

# Send with attachments
cc_gmail send -t "to@example.com" -s "Subject" -b "See attached" --attach file1.pdf --attach file2.txt

# Send from specific account
cc_gmail -a work send -t "colleague@company.com" -s "Report" -b "Here's the report"
```

### Create Draft

```bash
cc_gmail draft -t "recipient@example.com" -s "Subject" -b "Draft body"
cc_gmail draft -t "recipient@example.com" -s "Subject" -f draft.txt
```

### Search

```bash
# Basic search
cc_gmail search "from:someone@example.com"

# Search with count
cc_gmail search "subject:important" -n 20

# Gmail query examples
cc_gmail search "is:unread"
cc_gmail search "has:attachment"
cc_gmail search "after:2024/01/01 before:2024/02/01"
cc_gmail search "from:boss@company.com subject:urgent"
```

### Labels

```bash
# List all labels/folders
cc_gmail labels
```

### Delete

```bash
# Move to trash
cc_gmail delete <message_id>

# Permanently delete (skip trash)
cc_gmail delete <message_id> --permanent

# Skip confirmation
cc_gmail delete <message_id> -y
```

### Profile

```bash
# Show authenticated user profile
cc_gmail profile
```

---

## Gmail Search Syntax

cc_gmail supports full Gmail search syntax:

| Query | Description |
|-------|-------------|
| `from:email` | Messages from sender |
| `to:email` | Messages to recipient |
| `subject:word` | Messages with subject containing word |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `has:attachment` | Messages with attachments |
| `after:YYYY/MM/DD` | Messages after date |
| `before:YYYY/MM/DD` | Messages before date |
| `label:name` | Messages with label |
| `in:inbox` | Messages in inbox |
| `in:sent` | Sent messages |

Combine queries: `from:boss@company.com subject:report after:2024/01/01`

---

## Configuration

Configuration files are stored in `~/.cc_gmail/`:

```
~/.cc_gmail/
    config.json              # Default account setting
    accounts/
        personal/
            credentials.json # OAuth client credentials (you provide)
            token.json       # OAuth access token (created automatically)
        work/
            credentials.json
            token.json
```

---

## Troubleshooting

### "OAuth credentials not found"

Run `cc_gmail accounts add <name>` to see where to place your `credentials.json` file.

### "No accounts configured"

1. Run `cc_gmail accounts add <name>` to create an account
2. Download credentials from Google Cloud Console
3. Place `credentials.json` in the account folder
4. Run `cc_gmail auth`

### "Multiple accounts configured but no default set"

Either:
- Set a default: `cc_gmail accounts default <name>`
- Specify account: `cc_gmail --account <name> <command>`

### "Access blocked" or "App not verified"

Your app is in testing mode. Make sure your Gmail address is added as a test user:
1. Go to Google Cloud Console -> APIs & Services -> OAuth consent screen
2. Under "Test users", add your Gmail address

### "Token expired" or authentication issues

```bash
cc_gmail auth --revoke
cc_gmail auth
```

---

## Building Executable

```powershell
.\build.ps1
```

This creates `dist/cc_gmail.exe`.

---

## Installation (Development)

```bash
cd src/cc_gmail
pip install -e .
```

---

## License

MIT
