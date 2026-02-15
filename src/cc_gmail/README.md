# cc_gmail

Gmail CLI: read, send, search, and manage emails from the command line.

Supports **multiple Gmail accounts** with easy switching between them.

## Quick Start

```bash
# 1. Add your first account
cc_gmail accounts add personal

# 2. Complete Google Cloud setup (see detailed steps below)
# 3. Place credentials.json in the account folder
# 4. Authenticate
cc_gmail auth

# 5. Start using Gmail from the command line
cc_gmail list
```

---

## Google Cloud Setup (Required - One Time)

Before using cc_gmail, you need OAuth credentials from Google Cloud Console.
This is a one-time setup. You can use the same credentials for multiple Gmail accounts.

### Step 1: Go to Google Cloud Console

1. Open https://console.cloud.google.com/
2. Sign in with your Google account

### Step 2: Create or Select a Project

1. Click the project dropdown at the top (next to "Google Cloud")
2. Either:
   - Select an existing project, OR
   - Click "New Project", enter a name (e.g., "cc_gmail"), click "Create"

### Step 3: Set Up OAuth Consent Screen

This tells Google what your app is and who can use it.

1. In the left sidebar, go to **APIs & Services** -> **OAuth consent screen**
   - Or go directly to: https://console.cloud.google.com/apis/credentials/consent
2. If you see "Google Auth Platform not configured yet", click **"Get started"**
3. Fill in the required fields:
   - **App name:** `cc_gmail`
   - **User support email:** Select your email
   - **Audience:** Select **"External"** (unless you have Google Workspace)
   - **Contact email:** Enter your email
4. Click **"Create"** or **"Save and Continue"**
5. On the Scopes page, click **"Save and Continue"** (we'll use default scopes)
6. On the Test users page:
   - Click **"Add Users"**
   - Enter your Gmail address(es) that you want to use with cc_gmail
   - Click **"Save and Continue"**

### Step 4: Enable the Gmail API

1. Go to **APIs & Services** -> **Library**
   - Or go directly to: https://console.cloud.google.com/apis/library
2. Search for **"Gmail API"**
3. Click on **"Gmail API"** in the results
4. Click the **"Enable"** button
5. Wait a few seconds for it to enable

**IMPORTANT:** If you skip this step, you'll get this error when authenticating:
```
Gmail API has not been used in project XXXXX before or it is disabled.
```

### Step 5: Create OAuth Credentials

1. Go to **APIs & Services** -> **Credentials**
   - Or go directly to: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. For **Application type**, select **"Desktop app"**
5. For **Name**, enter `cc_gmail` (or any name you want)
6. Click **"Create"**

### Step 6: Download the Credentials File

1. After creating, a popup shows your Client ID and Secret
2. Click **"DOWNLOAD JSON"** (the download icon)
3. Save the file - it will have a long name like:
   `client_secret_XXXXX.apps.googleusercontent.com.json`

### Step 7: Set Up cc_gmail Account

```bash
# Create an account in cc_gmail
cc_gmail accounts add personal
```

This will show you where to place the credentials file:
```
~/.cc_gmail/accounts/personal/credentials.json
```

Copy/rename your downloaded JSON file to that location:
```bash
# Windows example:
copy "C:\Users\YOU\Downloads\client_secret_XXX.json" "C:\Users\YOU\.cc_gmail\accounts\personal\credentials.json"

# Or manually copy and rename the file
```

### Step 8: Authenticate

```bash
cc_gmail auth
```

This will:
1. Open a browser window
2. Ask you to sign in to your Google account
3. Ask you to grant permissions to cc_gmail
4. Show "Authenticated as: your@email.com" when successful

---

## Common Setup Errors

### "Gmail API has not been used in project XXXXX before or it is disabled"

**Problem:** The Gmail API is not enabled for your project.

**Solution:**
1. Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com
2. Make sure your project is selected at the top
3. Click **"Enable"**
4. Wait a minute, then run `cc_gmail auth` again

### "Access blocked: This app's request is invalid" or "Error 400: redirect_uri_mismatch"

**Problem:** The OAuth client type is wrong.

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Delete the existing OAuth client
3. Create a new one with type **"Desktop app"** (not "Web application")

### "Access blocked: cc_gmail has not completed the Google verification process"

**Problem:** Your app is in testing mode and you're not listed as a test user.

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Under "Test users", click **"Add Users"**
3. Add your Gmail address
4. Try again

### "OAuth credentials not found"

**Problem:** The credentials.json file is missing or in the wrong location.

**Solution:**
1. Run `cc_gmail accounts add <name>` to see the expected path
2. Copy your downloaded JSON file to that exact path
3. Make sure it's named `credentials.json`

### "No accounts configured"

**Problem:** You haven't created any accounts yet.

**Solution:**
```bash
cc_gmail accounts add personal
```

---

## Managing Multiple Accounts

cc_gmail supports multiple Gmail accounts. Each account has its own token
but can share the same OAuth credentials from Google Cloud.

### Add Multiple Accounts

```bash
# Add personal account (set as default)
cc_gmail accounts add personal --default

# Add work account
cc_gmail accounts add work

# Each account needs credentials.json in its folder
# You can copy the SAME credentials.json to each account folder
```

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
