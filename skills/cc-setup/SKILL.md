# cc-setup

Windows installer for the cc-tools CLI suite.

## Commands

```bash
# Run installer (no arguments needed)
cc-tools-setup
```

## What It Does

1. Creates `%LOCALAPPDATA%\cc-tools` directory
2. Downloads latest tool executables from GitHub releases
3. Adds install directory to Windows user PATH
4. Installs Claude Code skill integration

## Notes

- No admin privileges required
- Safe to run multiple times
- Requires internet access for GitHub downloads
- Restart terminal after installation to use tools
