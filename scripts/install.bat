@echo off
REM Add C:\cc_tools to user PATH (one-time setup)
REM Usage: scripts\install.bat

setlocal

set "INSTALL_DIR=C:\cc_tools"

echo ============================================
echo cc_tools PATH Installation
echo ============================================
echo.

REM Create install directory if it doesn't exist
if not exist "%INSTALL_DIR%" (
    echo Creating %INSTALL_DIR%...
    mkdir "%INSTALL_DIR%"
)

REM Check if already in PATH
echo %PATH% | findstr /I /C:"%INSTALL_DIR%" >nul
if %errorlevel% equ 0 (
    echo [OK] %INSTALL_DIR% is already in PATH
    goto :done
)

REM Add to user PATH using PowerShell
echo Adding %INSTALL_DIR% to user PATH...

powershell -Command "$p=[Environment]::GetEnvironmentVariable('Path','User'); if($p -notlike '*C:\cc_tools*'){[Environment]::SetEnvironmentVariable('Path',$p+';C:\cc_tools','User'); Write-Host '[OK] Added C:\cc_tools to user PATH'}else{Write-Host '[OK] C:\cc_tools already in PATH'}"

if %errorlevel% neq 0 (
    echo [FAIL] Could not add to PATH
    echo Please add %INSTALL_DIR% to your PATH manually
    exit /b 1
)

:done
echo.
echo ============================================
echo Installation Complete
echo ============================================
echo.
echo IMPORTANT: Open a NEW terminal for PATH changes to take effect.
echo.
echo Available tools:
echo.
echo Python tools (compiled executables):
if exist "%INSTALL_DIR%\cc_gmail.exe" echo   - cc_gmail
if exist "%INSTALL_DIR%\cc_image.exe" echo   - cc_image
if exist "%INSTALL_DIR%\cc_markdown.exe" echo   - cc_markdown
if exist "%INSTALL_DIR%\cc_setup.exe" echo   - cc_setup
if exist "%INSTALL_DIR%\cc_transcribe.exe" echo   - cc_transcribe
if exist "%INSTALL_DIR%\cc_video.exe" echo   - cc_video
if exist "%INSTALL_DIR%\cc_voice.exe" echo   - cc_voice
if exist "%INSTALL_DIR%\cc_whisper.exe" echo   - cc_whisper
echo.
echo Node.js tools:
if exist "%INSTALL_DIR%\cc-browser.cmd" echo   - cc-browser
echo.
echo Run any tool with --help for usage info.
