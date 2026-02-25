#!/bin/bash
# CC Tools Installer for Unix (Linux/macOS)

set -e

REPO="CenterConsulting/cc-tools"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
    linux)  OS_NAME="linux" ;;
    darwin) OS_NAME="macos" ;;
    *)      echo "ERROR: Unsupported OS: $OS"; exit 1 ;;
esac

case "$ARCH" in
    x86_64)  ARCH_NAME="x64" ;;
    amd64)   ARCH_NAME="x64" ;;
    arm64)   ARCH_NAME="arm64" ;;
    aarch64) ARCH_NAME="arm64" ;;
    *)       echo "ERROR: Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "CC Tools Installer"
echo "=================="
echo "OS: $OS_NAME"
echo "Architecture: $ARCH_NAME"
echo "Install directory: $INSTALL_DIR"
echo ""

# Get latest release tag
echo "Fetching latest release..."
LATEST_TAG=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name"' | cut -d'"' -f4)

if [ -z "$LATEST_TAG" ]; then
    echo "ERROR: Could not fetch latest release"
    exit 1
fi

echo "Latest version: $LATEST_TAG"

# Download cc_markdown
ASSET_NAME="cc_markdown-${OS_NAME}-${ARCH_NAME}"
DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/$ASSET_NAME"

echo "Downloading $ASSET_NAME..."
curl -L -o "/tmp/cc_markdown" "$DOWNLOAD_URL"

if [ ! -f "/tmp/cc_markdown" ]; then
    echo "ERROR: Download failed"
    exit 1
fi

# Install
echo "Installing to $INSTALL_DIR..."
chmod +x "/tmp/cc_markdown"

if [ -w "$INSTALL_DIR" ]; then
    mv "/tmp/cc_markdown" "$INSTALL_DIR/cc_markdown"
else
    sudo mv "/tmp/cc_markdown" "$INSTALL_DIR/cc_markdown"
fi

# Install SKILL.md for Claude Code integration
CLAUDE_SKILLS_DIR="$HOME/.claude/skills/cc-markdown"
mkdir -p "$CLAUDE_SKILLS_DIR"

echo "Installing SKILL.md for Claude Code..."
SKILL_URL="https://raw.githubusercontent.com/$REPO/main/skills/cc-markdown/SKILL.md"
if curl -sL "$SKILL_URL" -o "$CLAUDE_SKILLS_DIR/SKILL.md"; then
    echo "SKILL.md installed to: $CLAUDE_SKILLS_DIR"
else
    echo "WARNING: Could not download SKILL.md (Claude Code integration skipped)"
fi

echo ""
echo "Installation complete!"
echo ""
echo "What was installed:"
echo "  - cc_markdown -> $INSTALL_DIR"
echo "  - SKILL.md -> $CLAUDE_SKILLS_DIR"
echo ""
echo "Run 'cc_markdown --help' to get started."
echo ""
echo "In Claude Code, just ask: 'Convert report.md to PDF with boardroom theme'"
