# CC Tools - Underscore to Dash Migration Tracking

Generated: 2026-02-24 19:51

## Summary

| Category | Occurrences | Files |
|----------|-------------|-------|
| **To Fix** | 483 | 148 |
| Python imports (Keep) | 95 | 42 |
| Historical docs (Keep) | 140 | 2 |

---

## Files to Fix

### docs/ (65 occurrences in 10 files)

#### [ ] `docs/plan-token-consolidation.md` (40 matches)

| Line | Content |
|------|---------|
| 10 | `4. Result: cc_director_service can't use cc_gmail/cc_outlook` |
| 17 | `\| cc_outlook \| MSAL tokens \| '~/.cc_outlook/tokens/' \|` |
| 18 | `\| cc_gmail \| OAuth tokens \| '~/.cc_gmail/accounts/' \|` |
| 19 | `\| cc_browser \| profiles \| '%LOCALAPPDATA%/cc-browser/' \|` |
| 20 | `\| cc_vault \| database \| 'D:/Vault/' (configurable) \|` |
| 37 | `└── cc_director_service\     # Service files (already here)` |
| 38 | `├── cc_director_service.exe` |
| 40 | `│   └── cc_director.db` |
| 56 | `# 3. ~/.cc_tools (fallback for non-service use)` |
| 65 | `return Path.home() / ".cc_tools"` |
| 70 | `**cc_outlook** ('D:\ReposFred\cc_tools\src\cc_outlook\src\config.py'):` |
| 71 | `- Change from 'Path.home() / ".cc_outlook"'` |
| 74 | `**cc_gmail** ('D:\ReposFred\cc_tools\src\cc_gmail\src\config.py'):` |
| 75 | `- Change from 'Path.home() / ".cc_gmail"'` |
| 78 | `**cc_browser** ('D:\ReposFred\cc_tools\src\cc_browser\src\config.ts'):` |
| ... | *25 more matches* |

#### [ ] `docs/IMPLEMENTATION_PLAN.md` (10 matches)

| Line | Content |
|------|---------|
| 30 | `│   ├── cc_transcribe/             # Future` |
| 31 | `│   ├── cc_image/                  # Future` |
| 32 | `│   ├── cc_voice/                  # Future` |
| 33 | `│   ├── cc_whisper/                # Future` |
| 34 | `│   └── cc_video/                  # Future` |
| 383 | `- cc_transcribe` |
| 384 | `- cc_image` |
| 385 | `- cc_voice` |
| 386 | `- cc_whisper` |
| 387 | `- cc_video` |

#### [ ] `docs/CodingStyle.md` (3 matches)

| Line | Content |
|------|---------|
| 158 | `\| Modules \| snake_case \| 'cc_markdown', 'file_utils' \|` |
| 282 | `test_cc_markdown/` |
| 286 | `test_cc_voice/` |

#### [ ] `docs/audits/cc-crawl4ai_audit.md` (2 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-crawl4ai` |
| 516 | `**Audited By**: Claude (cc_tool_audit skill)` |

#### [ ] `docs/audits/cc-gmail_audit.md` (2 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-gmail` |
| 427 | `**Audited By**: Claude (cc_tool_audit skill)` |

#### [ ] `docs/audits/cc-reddit_audit.md` (2 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-reddit` |
| 407 | `**Auditor**: Claude (cc_tool_audit skill)` |

#### [ ] `docs/audits/cc-whisper_audit.md` (2 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-whisper` |
| 353 | `**Audited By**: Claude (cc_tool_audit skill)` |

#### [ ] `docs/audits/cc-youtube-info_audit.md` (2 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-youtube-info` |
| 230 | `**Audited By**: Claude (cc_tool_audit skill)` |

#### [ ] `docs/HANDOVER.md` (1 matches)

| Line | Content |
|------|---------|
| 46 | `\| Tool naming \| 'cc_[function]' \| Consistent, clear, branded \|` |

#### [ ] `docs/audits/cc-linkedin_audit.md` (1 matches)

| Line | Content |
|------|---------|
| 1 | `# cc_tool_audit: cc-linkedin` |

### src/ (348 occurrences in 126 files)

#### [ ] `src/cc-trisight/TEST_PLAN.md` (27 matches)

| Line | Content |
|------|---------|
| 3 | `Test output directory: 'D:\ReposFred\cc_tools\src\trisight\test_output\'` |
| 17 | `mkdir -p D:/ReposFred/cc_tools/src/trisight/test_output` |
| 27 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 37 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 47 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 57 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 67 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 77 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 78 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 90 | `"D:/ReposFred/cc_tools/src/trisight/TrisightCli/bin/Release/net10.0-windows10...` |
| 100 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 102 | `"D:/ReposFred/cc_tools/src/trisight/TrisightCli/bin/Release/net10.0-windows10...` |
| 112 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| 114 | `"D:/ReposFred/cc_tools/src/trisight/TrisightCli/bin/Release/net10.0-windows10...` |
| 124 | `"D:/ReposFred/cc_tools/src/cc_click/src/CcClick/bin/Release/net10.0-windows/C...` |
| ... | *12 more matches* |

#### [ ] `src/cc-photos/src/cli.py` (15 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_photos - photo organization tool."""` |
| 29 | `name="cc_photos",` |
| 124 | `console.print("No sources configured. Add one with: cc_photos source add <pat...` |
| 198 | `console.print("Add one with: cc_photos exclude add <path>")` |
| 368 | `console.print("  cc_photos init <path> --category <private\|work\|other>")` |
| 370 | `console.print("  cc_photos source add <path> -l <label> -c <category> -p <pri...` |
| 407 | `Use 'cc_photos exclude add <path>' to add more exclusions.` |
| 410 | `cc_photos scan                    # Scan all drives` |
| 411 | `cc_photos scan D: E:              # Scan specific drives only` |
| 412 | `cc_photos scan --source "D Drive" # Rescan existing source only` |
| 413 | `cc_photos scan --category private # Mark new photos as private` |
| 471 | `console.print("  Use 'cc_photos exclude list' to view, 'cc_photos exclude add...` |
| 575 | `console.print("  cc_photos stats           # View statistics")` |
| 576 | `console.print("  cc_photos dupes           # Find duplicates")` |
| 577 | `console.print("  cc_photos analyze -n 10   # AI analyze 10 photos")` |

#### [ ] `src/cc-linkedin/src/browser_client.py` (11 matches)

| Line | Content |
|------|---------|
| 1 | `"""HTTP client wrapper for cc_browser daemon."""` |
| 20 | `def get_cc_browser_dir() -> Path:` |
| 45 | `cc_browser_dir = get_cc_browser_dir()` |
| 47 | `if not cc_browser_dir.exists():` |
| 49 | `f"cc-browser directory not found: {cc_browser_dir}\n"` |
| 55 | `for profile_dir in cc_browser_dir.iterdir():` |
| 86 | `for profile_dir in cc_browser_dir.iterdir():` |
| 132 | `"""HTTP client for cc_browser daemon.` |
| 134 | `Communicates with the cc_browser daemon on localhost.` |
| 169 | `f"Cannot connect to cc_browser daemon on port {self.port}.\n"` |
| 187 | `f"Cannot connect to cc_browser daemon on port {self.port}.\n"` |

#### [ ] `src/cc-reddit/src/browser_client.py` (11 matches)

| Line | Content |
|------|---------|
| 1 | `"""HTTP client wrapper for cc_browser daemon."""` |
| 20 | `def get_cc_browser_dir() -> Path:` |
| 45 | `cc_browser_dir = get_cc_browser_dir()` |
| 47 | `if not cc_browser_dir.exists():` |
| 49 | `f"cc-browser directory not found: {cc_browser_dir}\n"` |
| 55 | `for profile_dir in cc_browser_dir.iterdir():` |
| 86 | `for profile_dir in cc_browser_dir.iterdir():` |
| 132 | `"""HTTP client for cc_browser daemon.` |
| 134 | `Communicates with the cc_browser daemon on localhost.` |
| 169 | `f"Cannot connect to cc_browser daemon on port {self.port}.\n"` |
| 187 | `f"Cannot connect to cc_browser daemon on port {self.port}.\n"` |

#### [ ] `src/cc-setup/installer.py` (11 matches)

| Line | Content |
|------|---------|
| 2 | `Core installer logic for cc_tools.` |
| 21 | `"cc_markdown",` |
| 22 | `"cc_transcribe",` |
| 23 | `"cc_image",` |
| 24 | `"cc_voice",` |
| 25 | `"cc_whisper",` |
| 26 | `"cc_video",` |
| 31 | `"""Installer for cc_tools suite."""` |
| 34 | `self.install_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "cc_tools"` |
| 35 | `self.skill_dir = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "skill...` |
| 78 | `if download_raw_file("skills/cc_tools/SKILL.md", str(skill_path)):` |

#### [ ] `src/cc_shared/config.py` (11 matches)

| Line | Content |
|------|---------|
| 1 | `"""Shared configuration for cc_tools.` |
| 3 | `Configuration is stored in the cc_tools data directory:` |
| 6 | `- ~/.cc_tools/ (fallback for user-only use)` |
| 25 | `3. ~/.cc_tools (fallback for user-only use)` |
| 40 | `return Path.home() / ".cc_tools"` |
| 44 | `"""Get the path to the cc_tools config file."""` |
| 125 | `queue_path: str = "D:/ReposFred/cc_consult/tools/communication_manager/content"` |
| 159 | `queue_path=data.get("queue_path", "D:/ReposFred/cc_consult/tools/communicatio...` |
| 168 | `database_path: str = "~/.cc_tools/photos.db"` |
| 185 | `database_path=data.get("database_path", "~/.cc_tools/photos.db"),` |
| 191 | `"""Main configuration class for cc_tools."""` |

#### [ ] `src/cc-reddit/PRD.md` (10 matches)

| Line | Content |
|------|---------|
| 44 | `cc_reddit CLI (Python + Typer)` |
| 47 | `cc_browser Daemon` |
| 158 | `- Easy HTTP client (requests/httpx) for cc_browser communication` |
| 163 | `- 'httpx' - HTTP client for cc_browser communication` |
| 169 | `- No direct Playwright dependency (cc_browser handles it)` |
| 303 | `- [ ] cc_browser HTTP client wrapper` |
| 395 | `src/cc_reddit/` |
| 400 | `│   ├── browser_client.py     # cc_browser HTTP client wrapper` |
| 413 | `├── cc_reddit.spec` |
| 422 | `2. Implement browser_client.py (HTTP wrapper for cc_browser)` |

#### [ ] `src/cc-comm-queue/release.bat` (9 matches)

| Line | Content |
|------|---------|
| 2 | `REM Release script for cc_comm_queue` |
| 8 | `echo Releasing cc_comm_queue` |
| 35 | `pyinstaller "%SCRIPT_DIR%cc_comm_queue.spec" --clean --noconfirm --distpath "...` |
| 43 | `if not exist "%SCRIPT_DIR%dist\cc_comm_queue.exe" (` |
| 56 | `copy /Y "%SCRIPT_DIR%dist\cc_comm_queue.exe" "%INSTALL_DIR%\" >nul` |
| 59 | `if exist "D:\ReposFred\cc_tools\docs\CC_TOOLS.md" (` |
| 60 | `copy /Y "D:\ReposFred\cc_tools\docs\CC_TOOLS.md" "%INSTALL_DIR%\" >nul` |
| 68 | `echo Executable: %INSTALL_DIR%\cc_comm_queue.exe` |
| 70 | `echo Test with: cc_comm_queue --version` |

#### [ ] `src/cc-linkedin/src/cli.py` (8 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_linkedin CLI - LinkedIn interactions via browser automation."""` |
| 24 | `name="cc_linkedin",` |
| 33 | `"""Get cc_linkedin config directory."""` |
| 34 | `return Path.home() / ".cc_linkedin"` |
| 172 | `profile: Optional[str] = typer.Option(None, "--profile", "-p", help="cc_brows...` |
| 179 | `Requires cc_browser daemon to be running.` |
| 198 | `"""Check cc_browser daemon and LinkedIn login status."""` |
| 204 | `console.print("[green]cc_browser daemon:[/green] running")` |

#### [ ] `src/cc-outlook/docs/IMPLEMENTATION_NOTES.md` (8 matches)

| Line | Content |
|------|---------|
| 51 | `\| 'cc_outlook.spec' \| PyInstaller config \|` |
| 68 | `- Path: '~/.cc_outlook/tokens/{email}_msal.json'` |
| 108 | `User runs: cc_outlook auth` |
| 232 | `cd src/cc_outlook` |
| 239 | `The 'cc_outlook.spec' includes:` |
| 258 | `\| Config dir \| '~/.cc_outlook/' \|` |
| 259 | `\| Profiles \| '~/.cc_outlook/profiles.json' \|` |
| 260 | `\| Token cache \| '~/.cc_outlook/tokens/{email}_msal.json' \|` |

#### [ ] `src/cc-outlook/src/cli.py` (8 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_outlook - Outlook from the command line with multi-account supp...` |
| 61 | `name="cc_outlook",` |
| 460 | `cc_list = [addr.strip() for addr in cc.split(',')] if cc else None` |
| 461 | `bcc_list = [addr.strip() for addr in bcc.split(',')] if bcc else None` |
| 469 | `cc=cc_list,` |
| 470 | `bcc=bcc_list,` |
| 515 | `cc_list = [addr.strip() for addr in cc.split(',')] if cc else None` |
| 522 | `cc=cc_list,` |

#### [ ] `src/cc-photos/cc-photos.spec` (8 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_photos."""` |
| 13 | `cc_vault_path = os.path.abspath('../cc-vault/src')` |
| 22 | `(cc_vault_path + '/*.py', 'cc_vault/src'),` |
| 39 | `'cc_vault',` |
| 40 | `'cc_vault.src',` |
| 41 | `'cc_vault.src.db',` |
| 42 | `'cc_vault.src.config',` |
| 43 | `'cc_vault.src.vectors',` |

#### [ ] `src/cc-comm-queue/src/cli.py` (7 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_comm_queue - Communication Manager Queue Tool."""` |
| 35 | `name="cc_comm_queue",` |
| 51 | `return get_cc_config()` |
| 54 | `config_path = Path.home() / ".cc_tools" / "config.json"` |
| 64 | `self.queue_path = cm.get("queue_path", "D:/ReposFred/cc_consult/tools/communi...` |
| 77 | `queue_path = "D:/ReposFred/cc_consult/tools/communication_manager/content"` |
| 441 | `config_path = Path.home() / ".cc_tools" / "config.json"` |

#### [ ] `src/cc-docgen/cli.py` (7 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI interface for cc_docgen using Click.` |
| 4 | `cc_docgen generate [OPTIONS]` |
| 28 | `"""cc_docgen - Generate C4 architecture diagrams from CenCon manifests."""` |
| 76 | `cc_docgen generate` |
| 79 | `cc_docgen generate --manifest ./docs/cencon/architecture_manifest.yaml --outp...` |
| 82 | `cc_docgen generate --format svg` |
| 110 | `test_file = output / ".cc_docgen_test"` |

#### [ ] `src/cc-photos/src/database.py` (7 matches)

| Line | Content |
|------|---------|
| 1 | `"""Database operations for cc_photos - uses vault database.` |
| 4 | `interface for cc_photos while storing all data in the central vault.` |
| 11 | `# Add cc_vault to path` |
| 16 | `cc_vault_path = Path(__file__).parent.parent.parent.parent / "cc_vault"` |
| 17 | `if cc_vault_path.exists():` |
| 18 | `sys.path.insert(0, str(cc_vault_path))` |
| 22 | `raise ImportError("cc_vault module not available. Install cc_vault first.")` |

#### [ ] `src/cc-vault/src/config.py` (7 matches)

| Line | Content |
|------|---------|
| 7 | `2. Shared ~/.cc_tools/config.json (preferred)` |
| 8 | `3. Legacy ~/.cc_vault/config.json (deprecated)` |
| 40 | `"""Get the config directory for cc_vault."""` |
| 41 | `return Path.home() / ".cc_vault"` |
| 53 | `2. Shared ~/.cc_tools/config.json (preferred)` |
| 54 | `3. Legacy ~/.cc_vault/config.json (deprecated)` |
| 62 | `# 2. Check shared cc_tools config (preferred)` |

#### [ ] `src/cc-markdown/build.sh` (6 matches)

| Line | Content |
|------|---------|
| 2 | `# Build script for cc_markdown executable` |
| 7 | `echo "Building cc_markdown executable..."` |
| 31 | `pyinstaller cc_markdown.spec --clean --noconfirm` |
| 34 | `if [ -f "dist/cc_markdown" ]; then` |
| 35 | `size=$(du -h dist/cc_markdown \| cut -f1)` |
| 36 | `echo "SUCCESS: Built dist/cc_markdown ($size)"` |

#### [ ] `src/cc-reddit/src/cli.py` (6 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_reddit CLI - Reddit interactions via browser automation."""` |
| 16 | `name="cc_reddit",` |
| 101 | `Requires cc_browser daemon to be running with the specified profile.` |
| 116 | `"""Check cc_browser daemon and Reddit login status."""` |
| 122 | `console.print("[green]cc_browser daemon:[/green] running")` |
| 930 | `error("Could not find comment input. Try using 'cc_reddit snapshot' to see pa...` |

#### [ ] `src/cc-trisight/skills/desktop/desktop_click.py` (6 matches)

| Line | Content |
|------|---------|
| 29 | `cc_args = {}` |
| 31 | `cc_args["-w"] = args.window` |
| 33 | `cc_args["--name"] = args.name` |
| 35 | `cc_args["--id"] = args.automation_id` |
| 37 | `cc_args["--xy"] = args.xy` |
| 39 | `exit_code, stdout, stderr, elapsed_ms = cc_run("click", cc_args)` |

#### [ ] `src/cc-setup/main.py` (5 matches)

| Line | Content |
|------|---------|
| 2 | `cc_tools-setup - Windows installer for cc_tools suite` |
| 3 | `Downloads and installs all cc_tools executables, adds to PATH, installs SKILL.md` |
| 13 | `print("  cc_tools Setup")` |
| 14 | `print("  https://github.com/CenterConsulting/cc_tools")` |
| 26 | `print("  Restart your terminal to use cc_tools.")` |

#### [ ] `src/cc-trisight/skills/desktop/desktop_type.py` (5 matches)

| Line | Content |
|------|---------|
| 29 | `cc_args = {"--text": args.text}` |
| 31 | `cc_args["-w"] = args.window` |
| 33 | `cc_args["--name"] = args.name` |
| 35 | `cc_args["--id"] = args.automation_id` |
| 37 | `exit_code, stdout, stderr, elapsed_ms = cc_run("type", cc_args)` |

#### [ ] `src/cc-youtube-info/src/cli.py` (5 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_youtube_info - Extract transcripts, metadata, and information f...` |
| 49 | `name="cc_youtube_info",` |
| 182 | `cc_youtube_info info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"` |
| 285 | `cc_youtube_info languages "https://www.youtube.com/watch?v=VIDEO_ID"` |
| 327 | `cc_youtube_info chapters "https://www.youtube.com/watch?v=VIDEO_ID"` |

#### [ ] `src/cc-crawl4ai/src/cli.py` (4 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_crawl4ai - AI-ready web crawler."""` |
| 37 | `name="cc_crawl4ai",` |
| 319 | `console.print("Create one with: cc_crawl4ai session create <name>")` |
| 356 | `console.print(f"Use with: cc_crawl4ai crawl <url> --session {name}")` |

#### [ ] `src/cc-markdown/pyproject.toml` (4 matches)

| Line | Content |
|------|---------|
| 49 | `Homepage = "https://github.com/CenterConsulting/cc_tools"` |
| 50 | `Documentation = "https://github.com/CenterConsulting/cc_tools/tree/main/src/c...` |
| 51 | `Repository = "https://github.com/CenterConsulting/cc_tools"` |
| 52 | `Issues = "https://github.com/CenterConsulting/cc_tools/issues"` |

#### [ ] `src/cc-outlook/docs/AUTHENTICATION.md` (4 matches)

| Line | Content |
|------|---------|
| 36 | `- **Name:** 'cc_outlook_cli' (or your preferred name)` |
| 73 | `### Step 4: Add Account to cc_outlook` |
| 139 | `- **Windows:** '%USERPROFILE%\.cc_outlook\tokens\'` |
| 140 | `- **Linux/Mac:** '~/.cc_outlook/tokens/'` |

#### [ ] `src/cc-photos/main.py` (4 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_photos CLI."""` |
| 20 | `cc_vault_path = base_path.parent / 'cc_vault'` |
| 21 | `if cc_vault_path.exists():` |
| 22 | `sys.path.insert(0, str(cc_vault_path.parent))` |

#### [ ] `src/cc-setup/github_api.py` (4 matches)

| Line | Content |
|------|---------|
| 14 | `REPO_NAME = "cc_tools"` |
| 31 | `"User-Agent": "cc_tools-setup"` |
| 76 | `headers={"User-Agent": "cc_tools-setup"}` |
| 116 | `path: Path within the repository (e.g., "skills/cc_tools/SKILL.md")` |

#### [ ] `src/cc-trisight/skills/desktop/desktop_read.py` (4 matches)

| Line | Content |
|------|---------|
| 25 | `cc_args = {"-w": args.window}` |
| 27 | `cc_args["--name"] = args.name` |
| 29 | `cc_args["--id"] = args.automation_id` |
| 31 | `exit_code, stdout, stderr, elapsed_ms = cc_run("read-text", cc_args)` |

#### [ ] `src/cc-trisight/skills/_shared/cc_click.py` (4 matches)

| Line | Content |
|------|---------|
| 11 | `from config import get_cc_click_path` |
| 26 | `cc_click = get_cc_click_path()` |
| 27 | `cmd = [cc_click, subcommand]` |
| 50 | `return 1, "", f"cc-click.exe not found at: {cc_click}", elapsed` |

#### [ ] `src/cc-crawl4ai/src/sessions.py` (3 matches)

| Line | Content |
|------|---------|
| 1 | `"""Session management for cc_crawl4ai."""` |
| 13 | `sessions_dir = Path.home() / ".cc_crawl4ai" / "sessions"` |
| 20 | `cache_dir = Path.home() / ".cc_crawl4ai" / "cache"` |

#### [ ] `src/cc-docgen/pyproject.toml` (3 matches)

| Line | Content |
|------|---------|
| 38 | `cc-docgen = "cc_docgen.cli:cli"` |
| 45 | `packages = ["cc_docgen"]` |
| 46 | `package-dir = {"cc_docgen" = "."}` |

#### [ ] `src/cc-docgen/README.md` (3 matches)

| Line | Content |
|------|---------|
| 23 | `cd cc-tools/src/cc_docgen` |
| 127 | `python -m cc_docgen generate  # Module name keeps underscore` |
| 145 | `python -m cc_docgen generate --verbose  # Module name keeps underscore` |

#### [ ] `src/cc-trisight/skills/screen/screen_capture.py` (3 matches)

| Line | Content |
|------|---------|
| 27 | `cc_args = {"-o": output_path}` |
| 29 | `cc_args["-w"] = args.window` |
| 31 | `exit_code, stdout, stderr, elapsed_ms = cc_run("screenshot", cc_args)` |

#### [ ] `src/cc-trisight/skills/window/window_elements.py` (3 matches)

| Line | Content |
|------|---------|
| 26 | `cc_args = {"-w": args.window, "-d": str(args.depth)}` |
| 28 | `cc_args["-t"] = args.control_type` |
| 30 | `exit_code, stdout, stderr, elapsed_ms = cc_run("list-elements", cc_args)` |

#### [ ] `src/cc-trisight/skills/_shared/config.py` (3 matches)

| Line | Content |
|------|---------|
| 11 | `r"D:\ReposFred\cc_tools\src\cc_click\src\CcClick\bin\Release\net10.0-windows\...` |
| 15 | `r"D:\ReposFred\cc_tools\src\cc_trisight\TrisightCli\bin\Release\net10.0-windo...` |
| 19 | `def get_cc_click_path() -> str:` |

#### [ ] `src/cc-docgen/__main__.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for running cc_docgen as a module.` |
| 3 | `Usage: python -m cc_docgen generate` |

#### [ ] `src/cc-gmail/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_gmail - Gmail from the command line with multi-account support."""` |
| 61 | `name="cc_gmail",` |

#### [ ] `src/cc-hardware/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI interface for cc_hardware."""` |
| 13 | `name="cc_hardware",` |

#### [ ] `src/cc-image/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_image - unified image toolkit."""` |
| 24 | `name="cc_image",` |

#### [ ] `src/cc-markdown/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI interface for cc_markdown using Typer."""` |
| 29 | `name="cc_markdown",` |

#### [ ] `src/cc-markdown/tests/fixtures/sample.md` (2 matches)

| Line | Content |
|------|---------|
| 3 | `This is a sample Markdown document for testing cc_markdown.` |
| 63 | `This sample document covers the main Markdown features supported by cc_markdown.` |

#### [ ] `src/cc-transcribe/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_transcribe."""` |
| 24 | `name="cc_transcribe",` |

#### [ ] `src/cc-vault/main.py` (2 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_vault CLI."""` |
| 9 | `"""Main entry point for cc_vault CLI."""` |

#### [ ] `src/cc-vault/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_vault - Personal Vault from the command line."""` |
| 42 | `name="cc_vault",` |

#### [ ] `src/cc-vault/tests/test_cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_vault CLI commands."""` |
| 41 | `assert "cc_vault version" in result.output` |

#### [ ] `src/cc-video/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_video."""` |
| 20 | `name="cc_video",` |

#### [ ] `src/cc-voice/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_voice."""` |
| 22 | `name="cc_voice",` |

#### [ ] `src/cc-whisper/src/cli.py` (2 matches)

| Line | Content |
|------|---------|
| 1 | `"""CLI for cc_whisper."""` |
| 14 | `name="cc_whisper",` |

#### [ ] `src/cc-click/src/CcClick/obj/Release/net10.0-windows/CcClick.sourcelink.json` (1 matches)

| Line | Content |
|------|---------|
| 1 | `{"documents":{"D:\\ReposFred\\cc-tools\\*":"https://raw.githubusercontent.com...` |

#### [ ] `src/cc-comm-queue/cc-comm-queue.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec for cc_comm_queue."""` |

#### [ ] `src/cc-comm-queue/README.md` (1 matches)

| Line | Content |
|------|---------|
| 9 | `cd D:\ReposFred\cc-tools\src\cc_comm_queue` |

#### [ ] `src/cc-comm-queue/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_comm_queue - CLI tool for Communication Manager queue."""` |

#### [ ] `src/cc-comm-queue/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for running cc_comm_queue as a module."""` |

#### [ ] `src/cc-comm-queue/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_comm_queue."""` |

#### [ ] `src/cc-crawl4ai/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_crawl4ai CLI."""` |

#### [ ] `src/cc-crawl4ai/src/batch.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Batch processing for cc_crawl4ai."""` |

#### [ ] `src/cc-crawl4ai/src/crawler.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Core crawler module for cc_crawl4ai."""` |

#### [ ] `src/cc-crawl4ai/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_crawl4ai - AI-ready web crawler."""` |

#### [ ] `src/cc-docgen/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_docgen - Architecture diagram generator for CenCon documentation.` |

#### [ ] `src/cc-gmail/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_gmail CLI."""` |

#### [ ] `src/cc-gmail/src/auth.py` (1 matches)

| Line | Content |
|------|---------|
| 39 | `return "https://github.com/CenterConsulting/cc_tools/tree/main/src/cc_gmail"` |

#### [ ] `src/cc-gmail/src/utils.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Utility functions for cc_gmail."""` |

#### [ ] `src/cc-gmail/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_gmail - Gmail CLI: read, send, search, and manage emails from the comma...` |

#### [ ] `src/cc-gmail/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Package entry point for cc_gmail."""` |

#### [ ] `src/cc-gmail/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_gmail."""` |

#### [ ] `src/cc-hardware/main.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for cc_hardware."""` |

#### [ ] `src/cc-hardware/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_hardware - System hardware information CLI."""` |

#### [ ] `src/cc-image/cc-image.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_image."""` |

#### [ ] `src/cc-image/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_image CLI."""` |

#### [ ] `src/cc-image/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_image - Unified image toolkit: generate, analyze, OCR, resize, convert."""` |

#### [ ] `src/cc-image/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_image."""` |

#### [ ] `src/cc-linkedin/main.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for cc_linkedin when run as executable."""` |

#### [ ] `src/cc-linkedin/src/linkedin_selectors.py` (1 matches)

| Line | Content |
|------|---------|
| 7 | `The cc_browser snapshot command with --interactive is the best way to` |

#### [ ] `src/cc-linkedin/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_linkedin - LinkedIn CLI via browser automation."""` |

#### [ ] `src/cc-markdown/cc-markdown.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_markdown."""` |

#### [ ] `src/cc-markdown/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_markdown CLI."""` |

#### [ ] `src/cc-markdown/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_markdown - Convert Markdown to PDF, Word, and HTML with beautiful theme...` |

#### [ ] `src/cc-markdown/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for cc_markdown CLI."""` |

#### [ ] `src/cc-markdown/src/themes/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Theme management for cc_markdown."""` |

#### [ ] `src/cc-markdown/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_markdown."""` |

#### [ ] `src/cc-outlook/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_outlook CLI."""` |

#### [ ] `src/cc-outlook/src/auth.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `Authentication and account management for cc_outlook.` |

#### [ ] `src/cc-outlook/src/utils.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Utility functions for cc_outlook."""` |

#### [ ] `src/cc-outlook/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_outlook - Outlook CLI: read, send, search emails and manage calendar fr...` |

#### [ ] `src/cc-outlook/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Package entry point for cc_outlook."""` |

#### [ ] `src/cc-outlook/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_outlook."""` |

#### [ ] `src/cc-photos/pyproject.toml` (1 matches)

| Line | Content |
|------|---------|
| 20 | `"cc_vault",` |

#### [ ] `src/cc-photos/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_photos - Photo organization tool."""` |

#### [ ] `src/cc-photos/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Allow running as python -m cc_photos."""` |

#### [ ] `src/cc-reddit/src/selectors.py` (1 matches)

| Line | Content |
|------|---------|
| 7 | `The cc_browser snapshot command with --interactive is the best way to` |

#### [ ] `src/cc-reddit/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_reddit - Reddit CLI via browser automation."""` |

#### [ ] `src/cc-reddit/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for cc_reddit."""` |

#### [ ] `src/cc-reddit/tests/test_cli.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_reddit CLI."""` |

#### [ ] `src/cc-reddit/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_reddit."""` |

#### [ ] `src/cc-transcribe/cc-transcribe.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_transcribe."""` |

#### [ ] `src/cc-transcribe/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_transcribe CLI."""` |

#### [ ] `src/cc-transcribe/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_transcribe - Video and audio transcription with timestamps and screensh...` |

#### [ ] `src/cc-transcribe/tests/test_ffmpeg.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for FFmpeg utilities in cc_transcribe."""` |

#### [ ] `src/cc-transcribe/tests/test_screenshots.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for screenshot extraction in cc_transcribe."""` |

#### [ ] `src/cc-transcribe/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_transcribe."""` |

#### [ ] `src/cc-trisight/skills/window/window_list.py` (1 matches)

| Line | Content |
|------|---------|
| 19 | `exit_code, stdout, stderr, elapsed_ms = cc_run("list-windows")` |

#### [ ] `src/cc-trisight/TrisightCli/obj/Release/net10.0-windows10.0.17763.0/TrisightCli.sourcelink.json` (1 matches)

| Line | Content |
|------|---------|
| 1 | `{"documents":{"D:\\ReposFred\\cc-tools\\*":"https://raw.githubusercontent.com...` |

#### [ ] `src/cc-trisight/TrisightCore/obj/Release/net10.0-windows10.0.17763.0/TrisightCore.sourcelink.json` (1 matches)

| Line | Content |
|------|---------|
| 1 | `{"documents":{"D:\\ReposFred\\cc-tools\\*":"https://raw.githubusercontent.com...` |

#### [ ] `src/cc-vault/src/utils.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Utility functions for cc_vault."""` |

#### [ ] `src/cc-vault/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_vault - Personal Data Platform CLI.` |

#### [ ] `src/cc-vault/src/__main__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Entry point for running cc_vault as a module."""` |

#### [ ] `src/cc-vault/tests/test_chunker.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_vault document chunker."""` |

#### [ ] `src/cc-vault/tests/test_db.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_vault database operations."""` |

#### [ ] `src/cc-vault/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_vault."""` |

#### [ ] `src/cc-video/cc-video.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_video."""` |

#### [ ] `src/cc-video/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_video CLI."""` |

#### [ ] `src/cc-video/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_video - Video utilities: info, extract audio, screenshots."""` |

#### [ ] `src/cc-video/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_video."""` |

#### [ ] `src/cc-voice/cc-voice.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_voice."""` |

#### [ ] `src/cc-voice/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_voice CLI."""` |

#### [ ] `src/cc-voice/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_voice - Text-to-speech using OpenAI."""` |

#### [ ] `src/cc-voice/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_voice."""` |

#### [ ] `src/cc-whisper/cc-whisper.spec` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""PyInstaller spec file for cc_whisper."""` |

#### [ ] `src/cc-whisper/main.py` (1 matches)

| Line | Content |
|------|---------|
| 2 | `"""Entry point for cc_whisper CLI."""` |

#### [ ] `src/cc-whisper/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_whisper - Audio transcription using OpenAI Whisper."""` |

#### [ ] `src/cc-whisper/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_whisper."""` |

#### [ ] `src/cc-youtube-info/src/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""cc_youtube_info - Extract transcripts, metadata, and information from YouT...` |

#### [ ] `src/cc-youtube-info/tests/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Tests for cc_youtube."""` |

#### [ ] `src/cc_shared/llm.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""LLM provider abstraction for cc_tools.` |

#### [ ] `src/cc_shared/pyproject.toml` (1 matches)

| Line | Content |
|------|---------|
| 8 | `description = "Shared configuration and LLM abstraction for cc_tools"` |

#### [ ] `src/cc_shared/__init__.py` (1 matches)

| Line | Content |
|------|---------|
| 1 | `"""Shared configuration and LLM abstraction for cc_tools."""` |

### scripts/ (31 occurrences in 3 files)

#### [ ] `scripts/migrate_config.bat` (14 matches)

| Line | Content |
|------|---------|
| 24 | `echo   Gmail:   %USER_HOME%\.cc_gmail` |
| 25 | `echo   Outlook: %USER_HOME%\.cc_outlook` |
| 26 | `echo   Config:  %USER_HOME%\.cc_tools` |
| 42 | `if exist "%USER_HOME%\.cc_gmail\accounts" (` |
| 43 | `xcopy "%USER_HOME%\.cc_gmail\accounts" "%DATA_DIR%\gmail\accounts" /E /Y /Q` |
| 44 | `if exist "%USER_HOME%\.cc_gmail\config.json" (` |
| 45 | `copy /Y "%USER_HOME%\.cc_gmail\config.json" "%DATA_DIR%\gmail\config.json"` |
| 54 | `if exist "%USER_HOME%\.cc_outlook\tokens" (` |
| 55 | `xcopy "%USER_HOME%\.cc_outlook\tokens" "%DATA_DIR%\outlook\tokens" /E /Y /Q` |
| 61 | `if exist "%USER_HOME%\.cc_outlook\profiles.json" (` |
| 62 | `copy /Y "%USER_HOME%\.cc_outlook\profiles.json" "%DATA_DIR%\outlook\profiles....` |
| 68 | `if exist "%USER_HOME%\.cc_tools\config.json" (` |
| 69 | `copy /Y "%USER_HOME%\.cc_tools\config.json" "%DATA_DIR%\config.json"` |
| 87 | `echo   3. Restart cc_director service` |

#### [ ] `scripts/install.sh` (9 matches)

| Line | Content |
|------|---------|
| 45 | `# Download cc_markdown` |
| 46 | `ASSET_NAME="cc_markdown-${OS_NAME}-${ARCH_NAME}"` |
| 50 | `curl -L -o "/tmp/cc_markdown" "$DOWNLOAD_URL"` |
| 52 | `if [ ! -f "/tmp/cc_markdown" ]; then` |
| 59 | `chmod +x "/tmp/cc_markdown"` |
| 62 | `mv "/tmp/cc_markdown" "$INSTALL_DIR/cc_markdown"` |
| 64 | `sudo mv "/tmp/cc_markdown" "$INSTALL_DIR/cc_markdown"` |
| 83 | `echo "  - cc_markdown -> $INSTALL_DIR"` |
| 86 | `echo "Run 'cc_markdown --help' to get started."` |

#### [ ] `scripts/build.bat` (8 matches)

| Line | Content |
|------|---------|
| 2 | `REM Build all cc_tools and copy to C:\cc-tools` |
| 8 | `echo Building all cc_tools` |
| 38 | `REM Convert underscore to dash for exe name (cc_outlook -> cc-outlook)` |
| 48 | `REM Handle special case: cc_setup builds as cc-tools-setup.exe` |
| 49 | `if "%%T"=="cc_setup" (` |
| 120 | `echo [SKIP] No build.ps1 found for cc_browser` |
| 134 | `if exist "%CCCLICK_SRC%\cc_click.slnx" (` |
| 161 | `if exist "%TRISIGHT_SRC%\cc_trisight.slnx" (` |

### tests/ (19 occurrences in 3 files)

#### [ ] `tests/integration/test_cc_markdown.py` (17 matches)

| Line | Content |
|------|---------|
| 1 | `"""Integration tests for cc_markdown CLI.` |
| 19 | `def run_cc_markdown(*args, check=True):` |
| 20 | `"""Run cc_markdown CLI and return result."""` |
| 26 | `cwd=Path(__file__).parent.parent.parent / "src" / "cc_markdown",` |
| 39 | `result = run_cc_markdown("--version")` |
| 41 | `assert "cc_markdown" in result.stdout.lower() or "0." in result.stdout` |
| 45 | `result = run_cc_markdown("--help")` |
| 51 | `result = run_cc_markdown("--themes")` |
| 66 | `result = run_cc_markdown(str(input_file), "-o", str(output_file))` |
| 82 | `result = run_cc_markdown(str(input_file), "-o", str(output_file))` |
| 100 | `result = run_cc_markdown(str(input_file), "-o", str(output_file))` |
| 112 | `result = run_cc_markdown(` |
| 129 | `result = run_cc_markdown(` |
| 146 | `result = run_cc_markdown(str(input_file), "-o", str(output_file))` |
| 157 | `result = run_cc_markdown(str(input_file), "-o", str(output_file))` |
| ... | *2 more matches* |

#### [ ] `tests/integration/fixtures/advanced.md` (1 matches)

| Line | Content |
|------|---------|
| 41 | `Use the 'cc_markdown' command to convert files.` |

#### [ ] `tests/integration/fixtures/basic.md` (1 matches)

| Line | Content |
|------|---------|
| 3 | `This is a basic markdown document for testing cc_markdown.` |

### root/ (20 occurrences in 6 files)

#### [ ] `analyze_csv2.py` (13 matches)

| Line | Content |
|------|---------|
| 7 | `cc_tools_by_file = defaultdict(list)` |
| 8 | `cc_tools_by_pattern = defaultdict(int)` |
| 10 | `with open(r'D:\ReposFred\cc-director\cc_underscore_findings.csv', 'r', encodi...` |
| 23 | `cc_tools_by_file[short_path].append((row['Line'], match))` |
| 29 | `cc_tools_by_pattern['pyproject.toml entries'] += 1` |
| 31 | `cc_tools_by_pattern['PyInstaller spec files'] += 1` |
| 33 | `cc_tools_by_pattern['Python imports'] += 1` |
| 35 | `cc_tools_by_pattern['Documentation (.md)'] += 1` |
| 37 | `cc_tools_by_pattern['Python source code'] += 1` |
| 39 | `cc_tools_by_pattern['Other'] += 1` |
| 42 | `for pattern, count in sorted(cc_tools_by_pattern.items(), key=lambda x: -x[1]):` |
| 47 | `for fpath, matches in sorted(cc_tools_by_file.items(), key=lambda x: -len(x[1...` |
| 54 | `for fpath, matches in cc_tools_by_file.items():` |

#### [ ] `generate_tracking.py` (2 matches)

| Line | Content |
|------|---------|
| 33 | `if 'cc_' in line:` |
| 116 | `lines.append('These use 'cc_' because Python cannot import packages with dash...` |

#### [ ] `.claude/skills/review-code/skill.md` (2 matches)

| Line | Content |
|------|---------|
| 67 | `CRITICAL: Use FULL file paths like D:\ReposFred\cc_tools\src\cc_markdown\main...` |
| 185 | `**Adapted from:** cc_director review-code skill` |

#### [ ] `analyze_csv.py` (1 matches)

| Line | Content |
|------|---------|
| 10 | `with open(r'D:\ReposFred\cc-director\cc_underscore_findings.csv', 'r', encodi...` |

#### [ ] `analyze_remaining.py` (1 matches)

| Line | Content |
|------|---------|
| 33 | `if 'cc_' in line:` |

#### [ ] `.claude/skills/commit/skill.md` (1 matches)

| Line | Content |
|------|---------|
| 127 | `**Adapted from:** cc_director commit skill` |

---

## Python Imports to Keep

These use `cc_` because Python cannot import packages with dashes.

- `analyze_csv2.py`: 2 occurrences
- `analyze_remaining.py`: 3 occurrences
- `docs/plan-token-consolidation.md`: 8 occurrences
- `generate_tracking.py`: 3 occurrences
- `src/cc-comm-queue/src/cli.py`: 3 occurrences
- `src/cc-crawl4ai/src/cli.py`: 1 occurrences
- `src/cc-docgen/__main__.py`: 1 occurrences
- `src/cc-docgen/cli.py`: 4 occurrences
- `src/cc-gmail/build.ps1`: 3 occurrences
- `src/cc-gmail/cc-gmail.spec`: 9 occurrences
- `src/cc-gmail/src/auth.py`: 1 occurrences
- `src/cc-gmail/src/cli.py`: 1 occurrences
- `src/cc-hardware/src/cli.py`: 1 occurrences
- `src/cc-image/src/cli.py`: 1 occurrences
- `src/cc-linkedin/src/browser_client.py`: 1 occurrences
- `src/cc-markdown/src/cli.py`: 1 occurrences
- `src/cc-outlook/build.ps1`: 3 occurrences
- `src/cc-outlook/cc-outlook.spec`: 5 occurrences
- `src/cc-outlook/src/auth.py`: 1 occurrences
- `src/cc-outlook/src/cli.py`: 1 occurrences
- `src/cc-photos/build.ps1`: 3 occurrences
- `src/cc-photos/cc-photos.spec`: 8 occurrences
- `src/cc-photos/main.py`: 4 occurrences
- `src/cc-photos/src/analyzer.py`: 6 occurrences
- `src/cc-photos/src/cli.py`: 1 occurrences
- `src/cc-photos/src/database.py`: 2 occurrences
- `src/cc-reddit/src/browser_client.py`: 1 occurrences
- `src/cc-transcribe/src/cli.py`: 1 occurrences
- `src/cc-trisight/skills/_shared/cc_click.py`: 1 occurrences
- `src/cc-trisight/skills/desktop/desktop_click.py`: 1 occurrences
- `src/cc-trisight/skills/desktop/desktop_read.py`: 1 occurrences
- `src/cc-trisight/skills/desktop/desktop_type.py`: 1 occurrences
- `src/cc-trisight/skills/screen/screen_capture.py`: 1 occurrences
- `src/cc-trisight/skills/window/window_elements.py`: 1 occurrences
- `src/cc-trisight/skills/window/window_list.py`: 1 occurrences
- `src/cc-vault/src/cli.py`: 1 occurrences
- `src/cc-vault/src/config.py`: 2 occurrences
- `src/cc-video/src/cli.py`: 1 occurrences
- `src/cc-voice/src/cli.py`: 1 occurrences
- `src/cc-whisper/src/cli.py`: 1 occurrences
- `src/cc-youtube-info/src/cli.py`: 1 occurrences
- `src/cc_shared/pyproject.toml`: 2 occurrences

---

## Historical Documentation (Keep)

These files document the migration history and should retain original references.

- `RENAME_MIGRATION.md`: 70 occurrences
- `docs/cc-vault-migration-plan.md`: 70 occurrences
