# cc-browser: Profile to Workspace Migration

## What Changed

cc-browser used to call its isolated browser instances "profiles." This conflicted
with Chrome's built-in "profile" concept (Person 1, Work, etc.), so we renamed
cc-browser's concept to **workspace**.

| Before | After |
|--------|-------|
| `--profile` flag | `--workspace` flag |
| `profile.json` config file | `workspace.json` config file |
| `cc-browser start --profile work` | `cc-browser start --workspace work` |
| `ProfileError` exception | `WorkspaceError` exception |
| `resolve_profile()` | `resolve_workspace()` |
| `get_port_for_profile()` | `get_port_for_workspace()` |

## What Did NOT Change

- **Directory names** stay the same (`edge-work/`, `chrome-work/`, `chrome-personal/`).
  Renaming them would lose all cookies and logged-in sessions.
- **Chrome profile commands** are unchanged. `cc-browser profiles` still lists
  Chrome's built-in profiles (Person 1, etc.) and `--profileDir` still works.
- **LinkedIn's `profile` subcommand** is unchanged. `cc-linkedin profile johndoe`
  views a LinkedIn user profile -- that is not related to this rename.
- **Ports** are unchanged: edge-work 9280, chrome-work 9281, chrome-personal 9282.

## Workspace Concept

A **workspace** is a cc-browser-managed isolated browser session with:

- Its own cookies, login sessions, and browser state
- A dedicated daemon port and CDP port
- A `workspace.json` config file with name, browser type, aliases, and favorites
- A data directory under `%LOCALAPPDATA%\cc-browser\<name>\`

A **Chrome profile** is Chrome's built-in user concept (Person 1, Work account, etc.)
with its own bookmarks, extensions, and Google account sync. cc-browser can optionally
use a system Chrome profile via `--profileDir "Profile 1"`, but that is separate from
the workspace concept.

## Configured Workspaces

| Directory | Name | Browser | Port | Aliases |
|-----------|------|---------|------|---------|
| edge-work | Edge Work | edge | 9280 | mindzie, edge-work |
| chrome-work | Chrome Work | chrome | 9281 | center, consulting, chrome-work, linkedin |
| chrome-personal | Chrome Personal | chrome | 9282 | personal |

## How to Update a Tool That Connects to cc-browser

If your tool uses `browser_client.py` to connect to the cc-browser daemon,
apply these changes:

### 1. Rename the exception class

```python
# Before
class ProfileError(Exception): ...

# After
class WorkspaceError(Exception): ...
```

### 2. Rename functions

```python
# Before
def resolve_profile(profile_name): ...
def get_port_for_profile(profile_name): ...

# After
def resolve_workspace(workspace_name): ...
def get_port_for_workspace(workspace_name): ...
```

### 3. Read workspace.json (not profile.json)

```python
# Before
config_path = os.path.join(workspace_dir, "profile.json")

# After
config_path = os.path.join(workspace_dir, "workspace.json")
```

### 4. Use the workspace key in config

```python
# Before
config.get("profile")

# After
config.get("workspace")
```

### 5. Update BrowserClient constructor

```python
# Before
class BrowserClient:
    def __init__(self, profile=None):
        self.profile = profile

# After
class BrowserClient:
    def __init__(self, workspace=None, profile=None):
        # profile kept as deprecated alias for backward compat
        self.workspace = workspace or profile
```

### 6. Update CLI flags

```python
# Before
parser.add_argument("--profile", "-p", help="cc-browser workspace name")

# After
parser.add_argument("--workspace", "-w", help="cc-browser workspace name")
```

### 7. Update HTTP request body

```python
# Before
requests.post(url, json={"profile": name})

# After
requests.post(url, json={"workspace": name})
```

### 8. Update lockfile reading

```python
# Before
lockdata.get("profile")

# After
lockdata.get("workspace")
```

## Tools That Connect to cc-browser

Only two tools connect to the cc-browser daemon:

| Tool | Status |
|------|--------|
| cc-reddit | Migrated |
| cc-linkedin | Migrated |

No other tools in cc-tools connect to cc-browser.

## Files Changed in the Migration

### cc-browser (Node.js)
- `src/chrome.mjs` - parameter rename: profileName -> workspaceName
- `src/daemon.mjs` - functions, state, routes, lockfile, arg parsing
- `src/cli.mjs` - functions, args, help text, new `workspaces` command
- `src/main.mjs` - combined daemon+cli changes
- `README.md` - full rewrite with workspace terminology

### cc-reddit (Python)
- `src/browser_client.py` - exception, functions, config reading
- `src/cli.py` - imports, Config class, CLI flag

### cc-linkedin (Python)
- `src/browser_client.py` - exception, functions, config reading
- `src/cli.py` - imports, Config class, CLI flag, default workspace loading

### Documentation
- `docs/cc-tools.md` - cc-browser section
- `skills/cc-browser/SKILL.md` - examples, options table
- `skills/cc-linkedin/SKILL.md` - prerequisites, troubleshooting
- `~/.claude/CLAUDE.md` - LinkedIn approach instruction

### On-Disk Config Files
- `edge-work/profile.json` -> `edge-work/workspace.json`
- `chrome-work/profile.json` -> `chrome-work/workspace.json` (key also renamed)
- `chrome-personal/profile.json` -> `chrome-personal/workspace.json`
- `daemon.lock` deleted (recreated on next daemon start with workspace field)
