# cc_outlook MSAL Device Code Flow Implementation

## Date: February 18, 2026

## Overview

This document describes the authentication implementation for cc_outlook using MSAL (Microsoft Authentication Library) with Device Code Flow. This replaces the previous browser-based OAuth flow which had persistent issues.

---

## The Problem

The original O365 library authentication used browser-based OAuth with redirect URIs. This consistently failed with:

1. **"wrongplace" redirect errors** - OAuth state mismatch when browser has cached SSO sessions
2. **State mismatch issues** - Browser automation made it worse
3. **MFA complications** - Multi-factor auth added additional redirect complexity

After 5 days of troubleshooting, we determined the browser redirect approach was fundamentally unreliable for CLI applications.

---

## The Solution: Device Code Flow

Device Code Flow is Microsoft's recommended authentication method for CLI/desktop apps.

### How It Works

1. CLI requests a device code from Microsoft
2. User sees: "Go to https://microsoft.com/devicelogin and enter code XXXXXXXX"
3. User opens browser manually, enters code, signs in
4. CLI polls Microsoft until authentication completes
5. Token is returned to CLI

### Why It Works

- **No redirect URI involved** - eliminates all redirect issues
- **No OAuth state to mismatch** - state is managed by device code
- **Works with MFA** - user completes MFA in browser, CLI just waits
- **Browser independence** - user can even use a different device

---

## Implementation Details

### Files Modified

| File | Purpose |
|------|---------|
| `src/auth.py` | Core authentication logic with MSAL |
| `src/cli.py` | CLI command updates |
| `requirements.txt` | Added `msal>=1.20.0` |
| `cc_outlook.spec` | PyInstaller config for rich unicode data |

### Key Components in auth.py

#### 1. MSALTokenBackend Class (lines 33-107)

Custom token backend that bridges MSAL tokens to O365 library.

```python
class MSALTokenBackend(BaseTokenBackend):
```

**Purpose:** O365 library expects a token backend. This class:
- Loads tokens from MSAL's SerializableTokenCache
- Converts MSAL token format to O365 expected format
- Handles automatic token refresh via `acquire_token_silent()`

**Token Storage:**
- Path: `~/.cc_outlook/tokens/{email}_msal.json`
- Format: MSAL's SerializableTokenCache JSON format (~13KB)

#### 2. authenticate_device_code_with_cache() Function (lines 113-189)

Main authentication function.

```python
def authenticate_device_code_with_cache(client_id, token_path, scopes, force):
```

**Flow:**
1. Load existing token cache (if not forcing)
2. Try silent token refresh first
3. If silent fails, initiate device code flow
4. Display code and URL to user
5. Poll until user completes auth
6. Save token cache to file

#### 3. authenticate() Function (lines 460-526)

Entry point called by CLI.

```python
def authenticate(account_name, force=False):
```

**CRITICAL WORKAROUND (lines 519-526):**

```python
if account.is_authenticated:
    return account
else:
    # Even if O365 says not authenticated, if we have a token, try anyway
    if result and 'access_token' in result:
        print("DEBUG: Forcing return since we have a token from MSAL")
        return account
```

**Why this workaround exists:**
- O365's `Account.is_authenticated` property checks token format
- MSAL tokens have a different format than O365 expects
- `is_authenticated` returns `False` even with valid MSAL tokens
- BUT: `MSALTokenBackend.load_token()` converts to correct format for API calls
- So we ignore `is_authenticated=False` and return the account anyway
- This works because actual API calls go through `load_token()` which converts properly

### Debug Statements

The code includes DEBUG print statements that show:
```
DEBUG: Token acquired: True
DEBUG: Token file exists: True
DEBUG: Token file size: 13400 bytes
DEBUG: Token backend returned: True
DEBUG: Token has access_token: True
DEBUG: account.is_authenticated = False
DEBUG: Forcing return since we have a token from MSAL
```

These are intentionally left in for troubleshooting.

---

## Azure App Configuration

### Required Settings

| Setting | Value |
|---------|-------|
| App Name | `cc_outlook_cli` |
| Account Types | Accounts in any organizational directory and personal Microsoft accounts |
| Redirect URI | `https://login.microsoftonline.com/common/oauth2/nativeclient` (Mobile/desktop) |
| Allow public client flows | **Yes** (CRITICAL) |

### Required API Permissions (Delegated)

- `Mail.ReadWrite`
- `Mail.Send`
- `Calendars.ReadWrite`
- `User.Read`
- `MailboxSettings.Read`

### Known Working Client ID

- example: `YOUR_CLIENT_ID`

---

## Token Flow Diagram

```
User runs: cc_outlook auth
              |
              v
    +-------------------+
    | Check for cached  |
    | token             |
    +-------------------+
              |
     [token exists?]
        /         \
      Yes          No
       |            |
       v            v
+------------+  +------------------+
| Try silent |  | Device Code Flow |
| refresh    |  |                  |
+------------+  +------------------+
       |                |
  [success?]            |
    /    \              |
  Yes     No            |
   |       \           /
   |        \         /
   v         v       v
+------+  +-------------------+
|Return|  | Display code      |
|token |  | User goes to URL  |
+------+  | Enters code       |
          | Signs in + MFA    |
          +-------------------+
                   |
                   v
          +-------------------+
          | Poll for token    |
          | Save to cache     |
          +-------------------+
                   |
                   v
          +-------------------+
          | Create O365 Acct  |
          | with MSAL backend |
          +-------------------+
                   |
                   v
          +-------------------+
          | is_authenticated  |
          | = False (ignore!) |
          +-------------------+
                   |
                   v
          +-------------------+
          | Return account    |
          | (it works anyway) |
          +-------------------+
```

---

## Troubleshooting

### "Failed to create device flow"

**Cause:** Azure app doesn't have public client flow enabled.

**Fix:** Azure Portal -> App registrations -> your app -> Authentication -> "Allow public client flows" = Yes

### Device code expired

**Cause:** Code is valid ~15 minutes. User took too long.

**Fix:** Run `cc_outlook auth` again for fresh code.

### Token expired after ~90 days

**Cause:** Refresh token expired due to inactivity.

**Fix:** `cc_outlook auth --force`

### MFA screen appears

**This is normal.** Complete MFA in browser. CLI will detect completion automatically.

---

## Build and Deploy

```powershell
cd D:\ReposFred\cc_tools\src\cc_outlook
.\build.ps1
copy dist\cc_outlook.exe C:\cc-tools\
```

### PyInstaller Note

The `cc_outlook.spec` file includes:
```python
datas=collect_data_files('rich'),
hiddenimports=[...] + collect_submodules('rich._unicode_data'),
```

This is required because rich library has unicode data files that PyInstaller doesn't find automatically.

---

## Files and Locations

| Item | Path |
|------|------|
| Executable | `C:\cc-tools\cc_outlook.exe` |
| Source | `D:\ReposFred\cc_tools\src\cc_outlook\` |
| Config dir | `%USERPROFILE%\.cc_outlook\` |
| Profiles | `%USERPROFILE%\.cc_outlook\profiles.json` |
| Token cache | `%USERPROFILE%\.cc_outlook\tokens\{email}_msal.json` |
| Auth batch file | `C:\cc-tools\cc_outlook_auth.bat` |

---

## Version History

- **Feb 18, 2026**: Implemented MSAL Device Code Flow, replacing broken browser OAuth
