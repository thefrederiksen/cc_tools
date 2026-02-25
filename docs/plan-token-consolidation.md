# CC Tools Configuration Consolidation Plan

**Status: IMPLEMENTED** (2026-02-23)

## Problem

1. Config and tokens scattered across multiple locations
2. All use `Path.home()` which is user-specific
3. Windows services run as SYSTEM, can't access user profile
4. Result: cc-director_service can't use cc-gmail/cc-outlook

## Current Storage Locations

| Tool | Config/Tokens | Path |
|------|---------------|------|
| cc_shared | config.json | `~/.cc-tools/` |
| cc-outlook | MSAL tokens | `~/.cc-outlook/tokens/` |
| cc-gmail | OAuth tokens | `~/.cc-gmail/accounts/` |
| cc-browser | profiles | `%LOCALAPPDATA%/cc-browser/` |
| cc-vault | database | `D:/Vault/` (configurable) |

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
└── cc-director_service\     # Service files (already here)
    ├── cc-director_service.exe
    ├── data\                # Service-specific data
    │   └── cc-director.db
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
    # 3. ~/.cc-tools (fallback for non-service use)

    if env_path := os.environ.get("CC_TOOLS_DATA"):
        return Path(env_path)

    system_path = Path(r"C:\cc-tools\data")
    if system_path.exists():
        return system_path

    return Path.home() / ".cc-tools"
```

### Step 2: Update each tool to use shared data dir

**cc-outlook** (`D:\ReposFred\cc-tools\src\cc-outlook\src\config.py`):
- Change from `Path.home() / ".cc-outlook"`
- To `get_data_dir() / "outlook"`

**cc-gmail** (`D:\ReposFred\cc-tools\src\cc-gmail\src\config.py`):
- Change from `Path.home() / ".cc-gmail"`
- To `get_data_dir() / "gmail"`

**cc-browser** (`D:\ReposFred\cc-tools\src\cc-browser\src\config.ts`):
- Change from `%LOCALAPPDATA%/cc-browser`
- To `C:\cc-tools\data\browser` (or respect env var)

### Step 3: Create migration script

Script to move existing tokens:
```
~/.cc-tools/config.json      -> C:\cc-tools\data\config.json
~/.cc-outlook/tokens/*       -> C:\cc-tools\data\outlook\tokens\
~/.cc-gmail/accounts/*       -> C:\cc-tools\data\gmail\accounts\
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

1. **cc_shared** - `D:\ReposFred\cc-tools\src\cc_shared\src\cc_shared\config.py`
   - Add `get_data_dir()` function
   - Update `get_config_path()` to use it

2. **cc-outlook** - `D:\ReposFred\cc-tools\src\cc-outlook\src\`
   - `config.py` - use shared data dir
   - `auth.py` - token path changes

3. **cc-gmail** - `D:\ReposFred\cc-tools\src\cc-gmail\src\`
   - `config.py` - use shared data dir
   - `auth.py` - token path changes

4. **cc-browser** - `D:\ReposFred\cc-tools\src\cc-browser\`
   - `src/config.ts` - use shared data dir

5. **Migration script** - NEW `D:\ReposFred\cc-tools\scripts\migrate_config.bat`

6. **cc-director deploy.bat** - `D:\ReposFred\cc-director\scheduler\deploy.bat`
   - Set CC_TOOLS_DATA env var for service

## Verification

1. Run migration script
2. Verify tools work from command line:
   ```
   cc-outlook profile
   cc-gmail -a personal send -t test@test.com -s "Test" -b "Test"
   ```
3. Restart cc-director service
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
   - ~/.cc-tools (fallback)

2. **cc-outlook/src/auth.py** - Updated CONFIG_DIR to use `get_data_dir() / 'outlook'`

3. **cc-gmail/src/auth.py** - Updated CONFIG_DIR to use `get_data_dir() / 'gmail'`

4. **cc-gmail/build.ps1** - Added cc_shared installation step

5. **cc-outlook/build.ps1** - Added cc_shared installation step

6. **cc-gmail/cc-gmail.spec** - Added cc_shared to pathex and hiddenimports

7. **cc-outlook/cc-outlook.spec** - Added cc_shared to pathex and hiddenimports

8. **cc-director/scheduler/deploy.bat** - Added:
   - Creation of C:\cc-tools\data directory structure
   - CC_TOOLS_DATA environment variable for the service
   - SYSTEM permissions on data directory

9. **NEW: cc-tools/scripts/migrate_config.bat** - Migration script to copy existing tokens

### Next Steps

1. Run migration script as Administrator:
   ```cmd
   D:\ReposFred\cc-tools\scripts\migrate_config.bat
   ```

2. Rebuild cc-gmail:
   ```powershell
   cd D:\ReposFred\cc-tools\src\cc-gmail
   .\build.ps1
   copy dist\cc-gmail.exe C:\cc-tools\
   ```

3. Rebuild cc-outlook:
   ```powershell
   cd D:\ReposFred\cc-tools\src\cc-outlook
   .\build.ps1
   copy dist\cc-outlook.exe C:\cc-tools\
   ```

4. Redeploy cc-director service (as Administrator):
   ```cmd
   D:\ReposFred\cc-director\scheduler\deploy.bat
   ```

5. Test:
   ```cmd
   cc-gmail list
   cc-outlook list
   ```

6. Test email dispatch:
   - Approve an email in Communication Manager
   - Check logs: `type C:\cc-tools\cc-director_service\logs\service_stderr.log`
