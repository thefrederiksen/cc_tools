# CC Tools Installer for Windows

$ErrorActionPreference = "Stop"

$Repo = "CenterConsulting/cc-tools"
$InstallDir = "$env:LOCALAPPDATA\cc-tools"

Write-Host "CC Tools Installer" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "Install directory: $InstallDir"
Write-Host ""

# Create install directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Get latest release
Write-Host "Fetching latest release..."
$Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
$LatestTag = $Release.tag_name

Write-Host "Latest version: $LatestTag"

# Download cc-markdown
$AssetName = "cc-markdown-windows-x64.exe"
$DownloadUrl = "https://github.com/$Repo/releases/download/$LatestTag/$AssetName"
$DestPath = "$InstallDir\cc-markdown.exe"

Write-Host "Downloading $AssetName..."
Invoke-WebRequest -Uri $DownloadUrl -OutFile $DestPath

if (-not (Test-Path $DestPath)) {
    Write-Host "ERROR: Download failed" -ForegroundColor Red
    exit 1
}

# Add to PATH if not already there
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$InstallDir*") {
    Write-Host "Adding to PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
    $env:Path = "$env:Path;$InstallDir"
}

# Install SKILL.md for Claude Code integration
$ClaudeSkillsDir = "$env:USERPROFILE\.claude\skills\cc-markdown"
if (-not (Test-Path $ClaudeSkillsDir)) {
    New-Item -ItemType Directory -Path $ClaudeSkillsDir -Force | Out-Null
}

Write-Host "Installing SKILL.md for Claude Code..."
$SkillUrl = "https://raw.githubusercontent.com/$Repo/main/skills/cc-markdown/SKILL.md"
try {
    Invoke-WebRequest -Uri $SkillUrl -OutFile "$ClaudeSkillsDir\SKILL.md" -ErrorAction Stop
    Write-Host "SKILL.md installed to: $ClaudeSkillsDir" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Could not download SKILL.md (Claude Code integration skipped)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "What was installed:"
Write-Host "  - cc-markdown.exe -> $InstallDir"
Write-Host "  - SKILL.md -> $ClaudeSkillsDir"
Write-Host ""
Write-Host "Restart your terminal, then run 'cc-markdown --help' to get started."
Write-Host ""
Write-Host "In Claude Code, just ask: 'Convert report.md to PDF with boardroom theme'"
