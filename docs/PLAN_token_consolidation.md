# CC Tools Configuration Consolidation Plan

**Status: IMPLEMENTED** (2026-02-23)

## Problem

1. Config and tokens scattered across multiple locations
2. All use `Path.home()` which is user-specific
3. Windows services run as SYSTEM, can't access user profile
4. Result: cc_director_service can't use cc_gmail/cc_outlook

## Current Storage Locations

| Tool | Config/Tokens | Path |
|------|---------------|------|
| cc_shared | config.json | `~/.cc_tools/` |
| cc_outlook | MSAL tokens | `~/.cc_outlook/tokens/` |
| cc_gmail | OAuth tokens | `~/.cc_gmail/accounts/` |
| cc_browser | profiles | `%LOCALAPPDATA%/cc-browser/` |
| cc_vault | database | `D:/Vault/` (configurable) |

## Solution: Consolidate to `C:\cc-tools\data\`

Move all config and tokens to a shared location accessible by all users including SYSTEM:

```
C:\cc-tools\
├── *.exe                    # Executables (already here)
├── data\                    # NEW: All persistent data
│   ├── config.json          # Main shared config
│   ├── outlook\
│   │   └── tokens\          # Outlook MSAL tokens
│   ├── gmail\
│   │   └── accounts\        # Gmail OAuth tokens per account
│   └── browser\
│       └── profiles\        # Browser profile data
└── cc_director_service\     # Service files (already here)
    ├── cc_director_service.exe
    ├── data\                # Service-specific data
    │   └── cc_director.db
    └── logs\
```

## Implementation

### Step 1: Add CC_TOOLS_DATA env var support

Update `cc_shared/config.py` to check for `CC_TOOLS_DATA` environment variable:

```python
def get_data_dir() -> Path:
    """Get the cc-tools data directory."""
    # Priority:
    # 1. CC_TOOLS_DATA env var
    # 2. C:\cc-tools\data (if exists and writable)
    # 3. ~/.cc_tools (fallback for non-service use)

    if env_path := os.environ.get("CC_TOOLS_DATA"):
        return Path(env_path)

    system_path = Path(r"C:\cc-tools\data")
    if system_path.exists():
        return system_path

    return Path.home() / ".cc_tools"
```

### Step 2: Update each tool to use shared data dir

**cc_outlook** (`D:\ReposFred\cc_tools\src\cc_outlook\src\config.py`):
- Change from `Path.home() / ".cc_outlook"`
- To `get_data_dir() / "outlook"`

**cc_gmail** (`D:\ReposFred\cc_tools\src\cc_gmail\src\config.py`):
- Change from `Path.home() / ".cc_gmail"`
- To `get_data_dir() / "gmail"`

**cc_browser** (`D:\ReposFred\cc_tools\src\cc_browser\src\config.ts`):
- Change from `%LOCALAPPDATA%/cc-browser`
- To `C:\cc-tools\data\browser` (or respect env var)

### Step 3: Create migration script

Script to move existing tokens:
```
~/.cc_tools/config.json      -> C:\cc-tools\data\config.json
~/.cc_outlook/tokens/*       -> C:\cc-tools\data\outlook\tokens\
~/.cc_gmail/accounts/*       -> C:\cc-tools\data\gmail\accounts\
```

### Step 4: Set permissions on data folder

```cmd
icacls "C:\cc-tools\data" /grant "SYSTEM:(OI)(CI)F"
icacls "C:\cc-tools\data" /grant "Users:(OI)(CI)F"
```

### Step 5: Update service deployment

Update `deploy.bat` to:
1. Create `C:\cc-tools\data\` if not exists
2. Set CC_TOOLS_DATA env var for the service
3. Set folder permissions

## Files to Modify

1. **cc_shared** - `D:\ReposFred\cc_tools\src\cc_shared\src\cc_shared\config.py`
   - Add `get_data_dir()` function
   - Update `get_config_path()` to use it

2. **cc_outlook** - `D:\ReposFred\cc_tools\src\cc_outlook\src\`
   - `config.py` - use shared data dir
   - `auth.py` - token path changes

3. **cc_gmail** - `D:\ReposFred\cc_tools\src\cc_gmail\src\`
   - `config.py` - use shared data dir
   - `auth.py` - token path changes

4. **cc_browser** - `D:\ReposFred\cc_tools\src\cc_browser\`
   - `src/config.ts` - use shared data dir

5. **Migration script** - NEW `D:\ReposFred\cc_tools\scripts\migrate_config.bat`

6. **cc_director deploy.bat** - `D:\ReposFred\cc_director\scheduler\deploy.bat`
   - Set CC_TOOLS_DATA env var for service

## Verification

1. Run migration script
2. Verify tools work from command line:
   ```
   cc_outlook profile
   cc_gmail -a personal send -t test@test.com -s "Test" -b "Test"
   ```
3. Restart cc_director service
4. Approve an email in Communication Manager
5. Verify email is sent (check logs)

## Rollback

Keep original locations as fallback in code:
- If `C:\cc-tools\data\` doesn't exist, fall back to `~/.cc_*`
- Allows gradual migration

---

## Implementation Complete (2026-02-23)

### Files Modified

1. **cc_shared/config.py** - Added `get_data_dir()` function with priority:
   - CC_TOOLS_DATA env var
   - C:\cc-tools\data (if exists)
   - ~/.cc_tools (fallback)

2. **cc_outlook/src/auth.py** - Updated CONFIG_DIR to use `get_data_dir() / 'outlook'`

3. **cc_gmail/src/auth.py** - Updated CONFIG_DIR to use `get_data_dir() / 'gmail'`

4. **cc_gmail/build.ps1** - Added cc_shared installation step

5. **cc_outlook/build.ps1** - Added cc_shared installation step

6. **cc_gmail/cc_gmail.spec** - Added cc_shared to pathex and hiddenimports

7. **cc_outlook/cc_outlook.spec** - Added cc_shared to pathex and hiddenimports

8. **cc_director/scheduler/deploy.bat** - Added:
   - Creation of C:\cc-tools\data directory structure
   - CC_TOOLS_DATA environment variable for the service
   - SYSTEM permissions on data directory

9. **NEW: cc_tools/scripts/migrate_config.bat** - Migration script to copy existing tokens

### Next Steps

1. Run migration script as Administrator:
   ```cmd
   D:\ReposFred\cc_tools\scripts\migrate_config.bat
   ```

2. Rebuild cc_gmail:
   ```powershell
   cd D:\ReposFred\cc_tools\src\cc_gmail
   .\build.ps1
   copy dist\cc_gmail.exe C:\cc-tools\
   ```

3. Rebuild cc_outlook:
   ```powershell
   cd D:\ReposFred\cc_tools\src\cc_outlook
   .\build.ps1
   copy dist\cc_outlook.exe C:\cc-tools\
   ```

4. Redeploy cc_director service (as Administrator):
   ```cmd
   D:\ReposFred\cc_director\scheduler\deploy.bat
   ```

5. Test:
   ```cmd
   cc_gmail list
   cc_outlook list
   ```

6. Test email dispatch:
   - Approve an email in Communication Manager
   - Check logs: `type C:\cc-tools\cc_director_service\logs\service_stderr.log`
