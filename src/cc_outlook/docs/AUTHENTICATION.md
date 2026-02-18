# cc_outlook Authentication Guide

## Overview

cc_outlook uses Microsoft Graph API with OAuth 2.0 Device Code Flow authentication.
This is the most reliable authentication method for CLI applications - no browser redirects needed.

**Technical Implementation Details:** See [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) for full technical documentation of how this works internally.

## Quick Reference

Already set up? Here are the common commands:

```bash
cc_outlook list                     # List inbox emails
cc_outlook list --unread            # List unread emails only
cc_outlook calendar events          # View calendar for next 7 days
cc_outlook folders                  # List mail folders
cc_outlook send -t email@example.com -s "Hi" -b "Hello"
cc_outlook auth                     # Re-authenticate if needed
```

---

## Part 1: Azure App Registration (One-Time Setup)

You only need to do this ONCE. The same app registration works for multiple email accounts.

### Step 1: Open Azure Portal

1. Go to **https://portal.azure.com**
2. Sign in with your Microsoft account

### Step 2: Navigate to App Registrations

1. In the **search bar at the top**, type: `App registrations`
2. Click on **App registrations** in the results
3. Click **+ New registration**

### Step 3: Fill in the Registration Form

| Field | Value |
|-------|-------|
| **Name** | `cc_outlook_cli` |
| **Supported account types** | Select: **Accounts in any organizational directory and personal Microsoft accounts** |

**Redirect URI:**

| Field | Value |
|-------|-------|
| **Platform** | Select: **Mobile and desktop applications** |
| **URI** | Enter: `https://login.microsoftonline.com/common/oauth2/nativeclient` |

Click **Register**

### Step 4: Copy the Application (Client) ID

After registration, you'll see the app overview page.

1. Find **Application (client) ID** in the Essentials section
2. **Copy this value** - you'll need it later
3. It looks like: `YOUR_CLIENT_ID`

### Step 5: Add API Permissions

1. In the left menu, click **API permissions**
2. Click **+ Add a permission**
3. Click **Microsoft Graph**
4. Click **Delegated permissions**
5. Search and **check** each of these (one at a time):
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `Calendars.ReadWrite`
   - `User.Read`
   - `MailboxSettings.Read`
6. Click **Add permissions**

Your permissions list should show:

```
Microsoft Graph (5)
  Calendars.ReadWrite      Delegated    No
  Mail.ReadWrite           Delegated    No
  Mail.Send                Delegated    No
  MailboxSettings.Read     Delegated    No
  User.Read                Delegated    No
```

### Step 6: Enable Public Client Flow

1. In the left menu, click **Authentication**
2. Scroll down to **Advanced settings**
3. Find **Allow public client flows**
4. Set it to **Yes** (toggle should be enabled)
5. Click **Save**

---

## Part 2: Connect Your Account

### Add an Account

```bash
cc_outlook accounts add YOUR_EMAIL --client-id YOUR_CLIENT_ID
```

Example:
```bash
cc_outlook accounts add user@example.com --client-id YOUR_CLIENT_ID
```

### Authenticate

```bash
cc_outlook auth
```

### The Device Code Flow

Device Code Flow is simple and reliable:

1. Run `cc_outlook auth`
2. A code and URL are displayed:
   ```
   ============================================================
   DEVICE CODE AUTHENTICATION
   ============================================================

   To sign in, use a web browser to open the page https://microsoft.com/devicelogin
   and enter the code XXXXXXXXX to authenticate.

   ============================================================
   ```
3. Open **https://microsoft.com/devicelogin** in any browser
4. Enter the code shown
5. Sign in with your Microsoft account
6. Accept the permissions when prompted
7. The CLI automatically completes authentication

You should see:
```
[green]Authenticated as:[/green] your.email@domain.com
```

**Why Device Code Flow?**
- No browser redirect issues
- No "wrongplace" errors
- Works even if the browser is on a different device
- No URL copying/pasting required

---

## Part 3: Using cc_outlook

### Email Commands

```bash
# List emails
cc_outlook list                    # List inbox (default 10)
cc_outlook list -n 20              # List 20 messages
cc_outlook list -f sent            # List sent mail
cc_outlook list --unread           # Show unread only

# Read email
cc_outlook read <message_id>       # Read full email

# Send email
cc_outlook send -t "to@example.com" -s "Subject" -b "Body text"
cc_outlook send -t "to@example.com" -s "Subject" -f body.txt
cc_outlook send -t "to@example.com" -s "Report" -b "See attached" --attach report.pdf

# Create draft
cc_outlook draft -t "to@example.com" -s "Subject" -b "Draft body"

# Search
cc_outlook search "quarterly report"
cc_outlook search "from:sender" -n 20

# Delete
cc_outlook delete <message_id>             # Delete message
cc_outlook delete <message_id> -y          # Skip confirmation
```

### Calendar Commands

```bash
# List calendars
cc_outlook calendar list

# View events
cc_outlook calendar events         # Next 7 days
cc_outlook calendar events -d 14   # Next 14 days
cc_outlook calendar events -c "Work Calendar"

# Create event
cc_outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00
cc_outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 --duration 90
cc_outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 -l "Room A"
cc_outlook calendar create -s "Meeting" -d 2024-12-25 -t 14:00 --attendees "a@x.com,b@x.com"
```

### Multiple Accounts

```bash
# List accounts
cc_outlook accounts list

# Add another account (same client ID works)
cc_outlook accounts add another@email.com --client-id YOUR_CLIENT_ID

# Set default
cc_outlook accounts default another@email.com

# Use specific account
cc_outlook -a personal list
cc_outlook --account work send -t "to@example.com" -s "Subject" -b "Body"
```

---

## Part 4: Troubleshooting

### Error: "Failed to create device flow"

**Cause:** The Azure app may not have public client flow enabled.

**Solution:**
1. Go to Azure Portal -> App registrations -> your app -> Authentication
2. Under "Advanced settings", set "Allow public client flows" to **Yes**
3. Click Save

### Error: AADSTS65001 - User has not consented

**Cause:** Permissions not accepted.

**Solution:**
1. Re-run `cc_outlook auth --force`
2. Make sure to click "Accept" on the consent screen at microsoft.com/devicelogin

### Device code expired

The device code is valid for about 15 minutes. If you see an expiration error:

**Solution:**
1. Run `cc_outlook auth` again to get a fresh code
2. Complete the authentication faster

### Token expired / Authentication required again

Tokens expire after ~90 days of inactivity.

**Solution:**
```bash
# Revoke and re-authenticate
cc_outlook auth --revoke
cc_outlook auth
```

Or force re-authentication:
```bash
cc_outlook auth --force
```

### Error: Account not found

**Solution:**
```bash
# List accounts to see what's configured
cc_outlook accounts list

# Add the account if missing
cc_outlook accounts add your@email.com --client-id YOUR_CLIENT_ID
```

---

## Part 5: File Locations

| Item | Location |
|------|----------|
| Profiles | `%USERPROFILE%\.cc_outlook\profiles.json` |
| Token Cache | `%USERPROFILE%\.cc_outlook\tokens\` |

---

## Part 6: Azure App Settings Summary

For reference, here are all the Azure app settings needed:

### App Registration

| Setting | Value |
|---------|-------|
| Name | `cc_outlook_cli` |
| Supported account types | Accounts in any organizational directory and personal Microsoft accounts |

### Redirect URI (Mobile and desktop applications)

```
https://login.microsoftonline.com/common/oauth2/nativeclient
```

### API Permissions (Microsoft Graph - Delegated)

| Permission | Description |
|------------|-------------|
| Mail.ReadWrite | Read and write mail |
| Mail.Send | Send mail |
| Calendars.ReadWrite | Read and write calendars |
| User.Read | Read user profile |
| MailboxSettings.Read | Read mailbox settings |

### Authentication Settings

| Setting | Value |
|---------|-------|
| Allow public client flows | **Yes** (Enabled) |

---

## Appendix: Known Working Client IDs

| Account Type | Client ID |
|--------------|-----------|
| example (multi-tenant) | `YOUR_CLIENT_ID` |

The same Client ID can be used for multiple accounts if the app is registered as multi-tenant.
