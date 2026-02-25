# CC Tools Rename Migration: Underscore to Dash Convention

## Overview

This document tracks the migration of all `cc_*` tools to `cc-*` (underscore to dash convention) following CLI industry standards.

**Started:** 2024-02-24
**Status:** Documentation Phase Complete (2026-02-24)

---

## Why We're Doing This

1. **CLI Industry Standard**: Most CLI tools use dashes (e.g., `git-lfs`, `docker-compose`, `aws-cli`)
2. **Consistency**: `cc-browser` already uses dashes; aligning all tools
3. **User Experience**: Dashes are easier to type than underscores (no Shift key)
4. **Professional Appearance**: Matches conventions of major CLI ecosystems

---

## Critical Technical Constraint

**Python cannot import packages with dashes:**
```python
import cc-browser  # SYNTAX ERROR
import cc_browser  # VALID
```

**Solution:** Keep internal Python package directories with underscores. Only rename:
- CLI command names (what users type)
- Executable names (.exe files)
- Repository directory names
- Documentation references
- Installation paths (`C:\cc_tools` -> `C:\cc-tools`)

---

## What's Been Completed

### Phase 1: Preparation
- [x] Documented current state
- [x] Created this migration document

### Phase 2: cc_tools Source Code Updates

#### pyproject.toml Files (18 tools)
- [x] cc_comm_queue -> cc-comm-queue
- [x] cc_crawl4ai -> cc-crawl4ai
- [x] cc_docgen -> cc-docgen
- [x] cc_gmail -> cc-gmail
- [x] cc_hardware -> cc-hardware
- [x] cc_image -> cc-image
- [x] cc_linkedin -> cc-linkedin
- [x] cc_markdown -> cc-markdown
- [x] cc_outlook -> cc-outlook
- [x] cc_photos -> cc-photos
- [x] cc_reddit -> cc-reddit
- [x] cc_shared -> cc-shared (package name only, no CLI)
- [x] cc_transcribe -> cc-transcribe
- [x] cc_vault -> cc-vault
- [x] cc_video -> cc-video
- [x] cc_voice -> cc-voice
- [x] cc_whisper -> cc-whisper
- [x] cc_youtube_info -> cc-youtube-info

#### .NET Projects
- [x] cc_click/CcClick.csproj - Added AssemblyName=cc-click
- [x] cc_trisight/TrisightCli.csproj - Added AssemblyName=cc-trisight

#### PyInstaller .spec Files (14 files)
- [x] All updated to output cc-*.exe names

#### Build Scripts
- [x] scripts/build.bat - Updated install dir to C:\cc-tools, exe names to cc-*
- [x] scripts/install.bat - Updated paths and tool names

#### Documentation
- [x] docs/CC_TOOLS.md - All tool names and paths updated

### Phase 3: cc_director Updates
- [x] dispatcher/email_sender.py - cc-outlook.exe, cc-gmail.exe paths
- [x] dispatcher/linkedin_sender.py - cc-linkedin.exe path

### Phase 4: cc_trisight/cc_computer Config
- [x] cc_tools/src/cc_trisight/skills/_shared/config.py - cc-click.exe, cc-trisight.exe paths
- [x] cc_tools/src/cc_trisight/skills/_shared/cc_click.py - Error messages
- [x] cc_computer/skills/trisight/_shared/config.py - cc-click.exe path
- [x] cc_computer/skills/trisight/_shared/cc_click.py - Error messages

### Phase 5: cc_shared Config
- [x] Verified - data directory (~/.cc_tools/) stays for backward compatibility

### Phase 6: CLAUDE.md Files
- [x] C:\Users\soren\.claude\CLAUDE.md - All cc_* command references updated

### Phase 7: Skills Directories
- [x] Renamed 18 skill directories from cc_* to cc-* (git mv)
- [x] Updated all 17 SKILL.md files with dashed tool names

---

### Phase 8: Individual Tool build.ps1 Files
- [x] All 18 build.ps1 files updated with dashed names:
  - cc_image, cc_transcribe, cc_video, cc_voice, cc_whisper
  - cc_setup, cc_browser, cc_youtube_info, cc_crawl4ai
  - cc_reddit, cc_vault, cc_photos, cc_hardware, cc_comm_queue
  - (cc_markdown, cc_linkedin, cc_gmail, cc_outlook were already done)

### Phase 9: README Files
- [x] All tool README.md files updated:
  - cc_image, cc_transcribe, cc_video, cc_voice, cc_whisper
  - cc_markdown, cc_crawl4ai, cc_youtube_info
  - cc_reddit, cc_linkedin, cc_vault, cc_photos
  - cc_gmail, cc_outlook

### Phase 10: Other Documentation
- [x] .github/workflows/release.yml - artifact names
- [x] docs/cc_markdown_PRD.md
- [x] scripts/install.ps1

### Phase 10b: Documentation File Renames (2026-02-24)
- [x] docs/CC_TOOLS.md -> docs/cc-tools.md
- [x] docs/CC_Tools_Strategy.md -> docs/cc-tools-strategy.md
- [x] docs/cc-vault_migration_plan.md -> docs/cc-vault-migration-plan.md
- [x] docs/cc_tools_improvements.md -> docs/cc-tools-improvements.md
- [x] docs/PLAN_token_consolidation.md -> docs/plan-token-consolidation.md
- [x] docs/site/tools/*.html - Renamed from cc_* to cc-* (gitignored, local only)
- [x] .claude/skills/cc_tools_skill_manager -> .claude/skills/cc-tools-skill-manager (gitignored, local only)
- [x] .claude/skills/cc_tool_audit -> .claude/skills/cc-tool-audit (gitignored, local only)
- [x] .claude-plugin/marketplace.json, plugin.json - Updated cc_tools references to cc-tools
- [x] scripts/install.sh - Updated repo URL and skill paths
- [x] scripts/run-tests.bat, pytest.ini - Updated paths to cc-* directories
- [x] README.md - Updated doc link to cc-tools-strategy.md

---

## What Still Needs To Be Done

### Phase 11: Repository Directory Renames
Local directories to rename:

| Current | New | Status |
|---------|-----|--------|
| D:\ReposFred\cc_tools | D:\ReposFred\cc-tools | DONE |
| D:\ReposFred\cc_director | D:\ReposFred\cc-director | DONE |
| D:\ReposFred\cc_consult | D:\ReposFred\cc-consult | DONE (fresh clone) |
| D:\ReposFred\cc_azprune | D:\ReposFred\cc-azprune | DONE |
| D:\ReposFred\cc_click | D:\ReposFred\cc-click | DONE |
| D:\ReposFred\cc_computer | D:\ReposFred\cc-computer | DONE |
| D:\ReposFred\cc_ideas | D:\ReposFred\cc-ideas | DONE |

### Phase 12: GitHub Repository Renames
After local renames, update GitHub repos:
1. GitHub.com -> Repo -> Settings -> General -> Repository name
2. Update local git remotes: `git remote set-url origin https://github.com/ORG/cc-tools.git`

### Phase 13: Build and Test
- [ ] Run scripts\build.bat
- [ ] Create C:\cc-tools directory
- [ ] Run scripts\install.bat
- [ ] Update PATH (remove C:\cc_tools, add C:\cc-tools)
- [ ] Test all tools with --version
- [ ] Test cross-tool dependencies

---

## Files Modified Summary

### cc-tools Repository
```
src/*/pyproject.toml          - 18 files (CLI entry points)
src/*/*.spec                  - 14 files (exe output names)
src/cc_click/**/*.csproj      - 1 file (AssemblyName)
src/cc_trisight/**/*.csproj   - 1 file (AssemblyName)
scripts/build.bat             - Install dir + exe names
scripts/install.bat           - Paths + tool names
docs/CC_TOOLS.md              - All references
skills/*/                     - 18 directories renamed
skills/*/SKILL.md             - 17 files updated
src/*/build.ps1               - 18 files (exe names, messages)
src/*/README.md               - 14 files (command names)
.github/workflows/release.yml - artifact names
docs/cc_markdown_PRD.md       - tool names
scripts/install.ps1           - paths + tool names
```

### cc_director Repository
```
scheduler/cc_director/dispatcher/email_sender.py
scheduler/cc_director/dispatcher/linkedin_sender.py
```

### cc_computer Repository
```
skills/trisight/_shared/config.py
skills/trisight/_shared/cc_click.py
```

### Global Config
```
C:\Users\soren\.claude\CLAUDE.md
```

---

## Rollback Instructions

If something goes wrong:

```bash
cd D:\ReposFred\cc-tools
git checkout .
git clean -fd
```

For renamed directories:
```cmd
cd D:\ReposFred
ren cc-tools cc_tools
ren cc-director cc_director
# etc.
```

---

## Commands to Continue

### To rename remaining directory (after closing processes):
```cmd
cd D:\ReposFred
ren cc_consult cc-consult
```

### To update remaining build.ps1 files:
Replace `cc_toolname` with `cc-toolname` in:
- exe path references
- display messages

### To build after all changes:
```cmd
cd D:\ReposFred\cc-tools
scripts\build.bat
```

---

## Notes

- The data directory `~/.cc_tools/` stays unchanged for backward compatibility
- Python import statements keep underscores (e.g., `import cc_shared`)
- Only CLI commands and exe files use dashes
- GitHub repo URLs in docs were NOT changed (actual repo names)
