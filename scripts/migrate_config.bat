@echo off
REM CC Tools Configuration Migration Script
REM Migrates tokens and config from user profile to C:\cc-tools\data
REM This allows Windows services (running as SYSTEM) to access the tokens

echo.
echo CC Tools Configuration Migration
echo =================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

set DATA_DIR=C:\cc-tools\data
set USER_HOME=%USERPROFILE%

echo Source locations:
echo   Gmail:   %USER_HOME%\.cc-gmail
echo   Outlook: %USER_HOME%\.cc-outlook
echo   Config:  %USER_HOME%\.cc-tools
echo.
echo Target location: %DATA_DIR%
echo.

REM Create directory structure
echo [1/5] Creating directory structure...
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\gmail" mkdir "%DATA_DIR%\gmail"
if not exist "%DATA_DIR%\gmail\accounts" mkdir "%DATA_DIR%\gmail\accounts"
if not exist "%DATA_DIR%\outlook" mkdir "%DATA_DIR%\outlook"
if not exist "%DATA_DIR%\outlook\tokens" mkdir "%DATA_DIR%\outlook\tokens"
echo       Done.

REM Copy Gmail accounts
echo [2/5] Migrating Gmail accounts...
if exist "%USER_HOME%\.cc-gmail\accounts" (
    xcopy "%USER_HOME%\.cc-gmail\accounts" "%DATA_DIR%\gmail\accounts" /E /Y /Q
    if exist "%USER_HOME%\.cc-gmail\config.json" (
        copy /Y "%USER_HOME%\.cc-gmail\config.json" "%DATA_DIR%\gmail\config.json"
    )
    echo       Migrated Gmail accounts.
) else (
    echo       No Gmail accounts found to migrate.
)

REM Copy Outlook tokens
echo [3/5] Migrating Outlook tokens...
if exist "%USER_HOME%\.cc-outlook\tokens" (
    xcopy "%USER_HOME%\.cc-outlook\tokens" "%DATA_DIR%\outlook\tokens" /E /Y /Q
    echo       Migrated Outlook tokens.
) else (
    echo       No Outlook tokens found to migrate.
)

if exist "%USER_HOME%\.cc-outlook\profiles.json" (
    copy /Y "%USER_HOME%\.cc-outlook\profiles.json" "%DATA_DIR%\outlook\profiles.json"
    echo       Migrated Outlook profiles.
)

REM Copy shared config
echo [4/5] Migrating shared config...
if exist "%USER_HOME%\.cc-tools\config.json" (
    copy /Y "%USER_HOME%\.cc-tools\config.json" "%DATA_DIR%\config.json"
    echo       Migrated shared config.
) else (
    echo       No shared config found to migrate.
)

REM Set permissions
echo [5/5] Setting permissions for SYSTEM and Users...
icacls "%DATA_DIR%" /grant "SYSTEM:(OI)(CI)F" /Q
icacls "%DATA_DIR%" /grant "Users:(OI)(CI)F" /Q
echo       Permissions set.

echo.
echo Migration complete!
echo.
echo Next steps:
echo   1. Rebuild cc-gmail and cc-outlook (run build scripts)
echo   2. Copy new executables to C:\cc-tools\
echo   3. Restart cc-director service
echo   4. Test: cc-gmail list
echo   5. Test: cc-outlook list
echo.
pause
