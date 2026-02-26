# Relocate cc-tools and Vault to User-Writable Locations

## Why

`C:\cc-tools` and `D:\Vault` are root-level directories. On work laptops, users
cannot create directories at `C:\` or `D:\` root without admin privileges. Everything
needs to move to a location any Windows user can write to.

## Decision: %LOCALAPPDATA%

New home: `C:\Users\<username>\AppData\Local\`

Why this location:
- Always writable without admin -- works on every Windows machine including work laptops
- Never synced by OneDrive -- Documents folder gets synced and would corrupt SQLite
  databases and ChromaDB vector stores with file locking conflicts
- Already the pattern -- cc-browser stores workspace data here, cc-setup installer
  already downloads to `%LOCALAPPDATA%\cc-tools`
- Standard Windows convention -- VS Code, Chrome, Discord all use AppData\Local
- Same path structure on every Windows machine regardless of language/locale

The downside (hidden in AppData) is actually a feature for the vault -- users should
not be casually browsing and accidentally deleting or rearranging vault database files.

## Path Referencing Strategy

Since the install path now contains the username (`C:\Users\soren\AppData\Local\...`),
we can no longer hardcode full paths in shared code or documentation. Different users
have different usernames, so hardcoded paths would break for anyone else.

**Rule: Three contexts, three approaches.**

### Source code (Python, JavaScript, C#)

Use runtime resolution. Never hardcode.

```python
# Python -- resolve at runtime
local_app_data = os.environ.get("LOCALAPPDATA")
install_dir = Path(local_app_data) / "cc-tools" / "bin"
vault_dir = Path(local_app_data) / "cc-myvault"
```

```javascript
// JavaScript -- resolve at runtime
const localAppData = process.env.LOCALAPPDATA;
const installDir = path.join(localAppData, 'cc-tools', 'bin');
```

This works for every user automatically.

### Documentation and skills (shared, in the repo)

Two sub-rules:

- **When showing how to RUN a tool**: just use the command name. Tools are on PATH.
  ```
  cc-vault stats
  cc-markdown input.md -o output.pdf
  cc-browser start --workspace mindzie
  ```
  NOT `C:\cc-tools\cc-vault.exe stats` or `%LOCALAPPDATA%\cc-tools\bin\cc-vault.exe stats`.

- **When explaining WHERE things are installed** (setup docs, troubleshooting):
  use the `%LOCALAPPDATA%` environment variable notation.
  ```
  Tools are installed to: %LOCALAPPDATA%\cc-tools\bin\
  Vault data is stored at: %LOCALAPPDATA%\cc-myvault\
  Shared config lives at:  %LOCALAPPDATA%\cc-tools\data\config.json
  ```
  This is generic -- every user can mentally resolve `%LOCALAPPDATA%` to their
  own path, and scripts/tools resolve it automatically.

### Personal files (CLAUDE.md, user memory)

These are only used by one specific user. Could hardcode the full expanded path,
but cleaner to just use command names (on PATH) and `%LOCALAPPDATA%` notation.
This way the instructions survive if the user account changes.

## Current vs Target Layout

### Current (requires admin)

```
C:\cc-tools\                      Executables + shared data
  *.exe                           Python tools (cc-vault, cc-linkedin, etc.)
  *.cmd                           Launchers for Node.js/.NET tools
  cc-browser\                     Node.js tool with node_modules
  cc-click\, cc-trisight\, ...    .NET tools
  data\                           Shared config, OAuth tokens
  CC_TOOLS.md                     Documentation

D:\Vault\                         Personal vault data
  vault.db, vectors\, documents\, media\, health\, ...

%LOCALAPPDATA%\cc-browser\        Browser workspaces (already correct)
~/.cc-tools\config.json           Shared config (fallback)
~/.cc-linkedin\, ~/.cc-reddit\    Per-tool config (already correct)
```

### Target (no admin needed)

```
%LOCALAPPDATA%\
  cc-tools\
    bin\                          Executables, .cmd launchers, CC_TOOLS.md
      *.exe
      *.cmd
      cc-browser\                 Node.js tool
      cc-click\                   .NET tools
      cc-trisight\
      cc-computer\
    data\                         Shared config, OAuth tokens
      config.json
      outlook\tokens\
      gmail\accounts\

  cc-myvault\                     Personal vault data (sibling, NOT nested)
    vault.db
    vectors\
    documents\
      transcripts\
      notes\
      journals\
      research\
    media\
      screenshots\
      images\
      audio\
    health\
      daily\
      sleep\
      workouts\
    imports\
    backups\

  cc-browser\                     Browser workspaces (unchanged)
```

### Why cc-myvault is separate from cc-tools

- `cc-vault` is the tool (the .exe) -- disposable, rebuild from source anytime
- `cc-myvault` is your personal data -- irreplaceable journals, documents, health data
- Separate directories mean you can back up vault independently without dragging
  along 500MB of executables
- Different name eliminates confusion between the tool and the data

### What stays the same

- `%LOCALAPPDATA%\cc-browser\` -- already in the right place
- `~/.cc-linkedin/config.json` -- per-tool configs stay in home directory
- `~/.cc-reddit/config.json` -- same
- Environment variable overrides (`CC_VAULT_PATH`, `CC_TOOLS_DATA`) still work
- PATH just points to a different directory

---

## Migration Procedure

### WARNING: This will break all tools temporarily

Every tool references the old paths. The migration must be done in one session
when you are NOT using the tools. Plan for 1-2 hours of downtime.

### Pre-migration checklist

- [ ] Close all terminals
- [ ] Stop cc-browser daemon (`cc-browser stop` in each workspace)
- [ ] Stop cc-director service if running
- [ ] No scheduled tasks running that use cc-tools
- [ ] Back up `D:\Vault` (the vault database is the most important thing to protect)

### Step 1: Update source code (before building)

These changes go into the cc-tools git repo. They change where tools LOOK for
things, not where things currently ARE.

#### 1a. `src/cc_shared/config.py` -- DO FIRST, everything depends on this

`get_data_dir()` new resolution order:
1. `CC_TOOLS_DATA` environment variable (if set)
2. `%LOCALAPPDATA%\cc-tools\data` (new default)
3. `C:\cc-tools\data` (legacy -- backward compat during transition)
4. `~/.cc-tools` (final fallback)

`VaultConfig` default: `"D:/Vault"` -> `%LOCALAPPDATA%\cc-myvault`

New function `get_install_dir()`: returns `%LOCALAPPDATA%\cc-tools\bin`

#### 1b. `src/cc-vault/src/config.py`

`get_vault_path()` new resolution order:
1. `CC_VAULT_PATH` environment variable
2. Shared cc-tools config (from cc_shared)
3. Legacy `~/.cc-vault/config.json`
4. `%LOCALAPPDATA%\cc-myvault` (new default)
5. `D:/Vault` (legacy, if exists)

### Step 2: Update build scripts

| File | What changes |
|------|-------------|
| `scripts/build.bat` line 13 | `INSTALL_DIR=C:\cc-tools` -> `INSTALL_DIR=%LOCALAPPDATA%\cc-tools\bin` |
| `scripts/install.bat` line 7 | Same + update PATH commands (remove old, add new) |
| `scripts/migrate_config.bat` line 20 | `DATA_DIR=C:\cc-tools\data` -> `DATA_DIR=%LOCALAPPDATA%\cc-tools\data` |
| `src/cc-comm-queue/release.bat` line 13 | Same INSTALL_DIR change |
| `src/cc-comm-queue/build.ps1` lines 39-40 | Target -> `$env:LOCALAPPDATA\cc-tools\bin` |

### Step 3: Run migration script

A new script `scripts/migrate-location.bat` handles the physical move.
No admin required. It COPIES (does not move) so old locations stay intact as backup.

What the script does:
1. Creates `%LOCALAPPDATA%\cc-tools\bin\` and `%LOCALAPPDATA%\cc-tools\data\`
2. Copies all .exe files from `C:\cc-tools\` to `bin\`
3. Copies all .cmd launchers from `C:\cc-tools\` to `bin\`
4. Copies subdirectory tools (cc-browser\, cc-click\, cc-trisight\, cc-computer\)
5. Copies `C:\cc-tools\data\` to `data\` (OAuth tokens, shared config)
6. Copies `D:\Vault\` to `%LOCALAPPDATA%\cc-myvault\` (uses robocopy for large dirs)
7. Updates user PATH: removes `C:\cc-tools`, adds `%LOCALAPPDATA%\cc-tools\bin`
8. Updates `~/.cc-tools/config.json` vault_path from `D:/Vault` to new location
9. Runs verification checks
10. Prints instructions for cleanup

### Step 4: Rebuild all tools

Run `scripts\build.bat` which now targets the new location. This rebuilds every
tool and deploys to `%LOCALAPPDATA%\cc-tools\bin\`.

### Step 5: Update documentation and skills

Apply the path referencing strategy: command names for running tools, `%LOCALAPPDATA%`
notation for explaining where things live.

| File | What changes |
|------|-------------|
| `docs/cc-tools.md` | `C:\cc-tools` -> `%LOCALAPPDATA%\cc-tools\bin` in install section. Command examples use bare command names (already on PATH). |
| `skills/cc-tools/SKILL.md` | Remove hardcoded `C:\cc-tools\cc-vault.exe` etc. Just use `cc-vault`. Add note that tools are on PATH. |
| `skills/cc-vault/SKILL.md` | `C:\cc-tools\cc-vault.exe` -> `cc-vault`. `D:\Vault` -> `%LOCALAPPDATA%\cc-myvault`. |
| `src/cc-vault/README.md` | Default vault path -> `%LOCALAPPDATA%\cc-myvault` |
| `src/cc-outlook/README.md` | `C:\cc-tools\cc-outlook.exe` -> `cc-outlook` (on PATH) |
| `src/cc-hardware/README.md` | Same pattern |
| `src/cc-photos/README.md` | Same pattern |

### Step 6: Update CLAUDE.md

`C:\Users\soren\.claude\CLAUDE.md` -- use command names instead of full paths:
- `"C:/cc-tools/cc-markdown.exe"` -> `cc-markdown` (on PATH)
- `C:\cc-tools\cc-outlook.exe` -> `cc-outlook` (on PATH)
- `C:\cc-tools\cc-outlook_auth.bat` -> `%LOCALAPPDATA%\cc-tools\bin\cc-outlook_auth.bat`
- `C:\cc-tools\CC_TOOLS.md` -> `%LOCALAPPDATA%\cc-tools\bin\CC_TOOLS.md`

### Step 7: Scan for any remaining references

Search the entire codebase for `C:\\cc-tools`, `C:/cc-tools`, and `D:/Vault` to
catch anything missed. Also search skills/ and .claude/ directories.

---

## Post-Migration Verification

Open a NEW terminal (PATH changes require a new terminal):

```bash
# Tools resolve from new PATH
where cc-vault
# Expected: C:\Users\soren\AppData\Local\cc-tools\bin\cc-vault.exe

# Vault finds data at new location
cc-vault stats

# OAuth tokens work
cc-outlook list

# Browser workspaces still work (unchanged location)
cc-browser start --workspace mindzie

# Other tools work
cc-markdown --help
cc-linkedin --help

# Old path is gone from PATH
echo %PATH% | findstr /i "C:\\cc-tools"
# Expected: no output
```

---

## Cleanup (after verification)

Only after confirming everything works:

```bash
# Remove old tools directory (admin may be needed)
rmdir /S /Q C:\cc-tools

# Remove old vault (ONLY after verifying cc-myvault has everything)
# Compare file counts first:
dir /S /B D:\Vault | find /c /v ""
dir /S /B %LOCALAPPDATA%\cc-myvault | find /c /v ""
# Then remove:
rmdir /S /Q D:\Vault
```

---

## Scope

### In scope (cc-tools repo only)

- All source code in `src/` that references `C:\cc-tools` or `D:\Vault`
- All build and install scripts in `scripts/`
- All documentation in `docs/`, `skills/`, and tool READMEs
- User's personal `CLAUDE.md` (path references)
- Migration script to physically copy files to new locations
- PATH update (remove old, add new)
- Post-migration cleanup of old directories

### Out of scope (separate tasks for later)

- **cc-director service**: Runs as SYSTEM user with its own %LOCALAPPDATA%. Needs
  admin privileges to reconfigure. Will need CC_TOOLS_DATA env var set to the
  user's expanded path.
- **cc-consult repo**: Has references to `C:/cc-tools/cc_linkedin.exe` in
  linkedin_safe.py and linkedin_content.py. Separate repo, separate change.
- **cc-vault backup command**: A proper `cc-vault backup` command that creates
  clean snapshots of the vault for safe storage in Documents/OneDrive/external drive.
- **.NET dynamic path resolution**: cc-computer's AgentConfig.cs hardcodes
  cc-click path in appsettings.json. Needs dynamic resolution logic.

---

## Risk Mitigation

- Migration script COPIES data, never moves. Old locations remain as backup.
- Config resolution checks both new and legacy paths, so tools work during transition
  regardless of which location has the data.
- Environment variables (`CC_TOOLS_DATA`, `CC_VAULT_PATH`) override everything,
  providing an escape hatch if something goes wrong.
- The vault is the most critical asset -- back it up before starting.
