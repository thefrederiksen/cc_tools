@echo off
REM ============================================================
REM CC Tools Location Migration Script
REM Copies tools and data from legacy locations to %%LOCALAPPDATA%%
REM
REM From:
REM   C:\cc-tools\          -> %LOCALAPPDATA%\cc-tools\bin\
REM   C:\cc-tools\data\     -> %LOCALAPPDATA%\cc-tools\data\
REM   D:\Vault\             -> %LOCALAPPDATA%\cc-myvault\
REM
REM This script COPIES (does not move). Old locations remain
REM as backup until you manually remove them.
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo CC Tools Location Migration
echo ============================================================
echo.

REM Verify LOCALAPPDATA is set
if "%LOCALAPPDATA%"=="" (
    echo ERROR: LOCALAPPDATA environment variable is not set.
    echo This should always be set on Windows. Something is wrong.
    exit /b 1
)

set "OLD_TOOLS=C:\cc-tools"
set "OLD_VAULT=D:\Vault"
set "NEW_BIN=%LOCALAPPDATA%\cc-tools\bin"
set "NEW_DATA=%LOCALAPPDATA%\cc-tools\data"
set "NEW_VAULT=%LOCALAPPDATA%\cc-myvault"

echo Old tools dir:  %OLD_TOOLS%
echo Old vault dir:  %OLD_VAULT%
echo New bin dir:    %NEW_BIN%
echo New data dir:   %NEW_DATA%
echo New vault dir:  %NEW_VAULT%
echo.

REM ============================================================
REM Pre-flight checks
REM ============================================================
echo [1/9] Pre-flight checks...

if not exist "%OLD_TOOLS%" (
    echo WARNING: %OLD_TOOLS% does not exist. Skipping tools migration.
    set "SKIP_TOOLS=1"
) else (
    echo   [OK] Found %OLD_TOOLS%
    set "SKIP_TOOLS=0"
)

if not exist "%OLD_VAULT%" (
    echo WARNING: %OLD_VAULT% does not exist. Skipping vault migration.
    set "SKIP_VAULT=1"
) else (
    echo   [OK] Found %OLD_VAULT%
    set "SKIP_VAULT=0"
)

echo.

REM ============================================================
REM Create directory structure
REM ============================================================
echo [2/9] Creating directory structure...

if not exist "%NEW_BIN%" (
    mkdir "%NEW_BIN%"
    echo   Created %NEW_BIN%
) else (
    echo   [OK] %NEW_BIN% already exists
)

if not exist "%NEW_DATA%" (
    mkdir "%NEW_DATA%"
    echo   Created %NEW_DATA%
) else (
    echo   [OK] %NEW_DATA% already exists
)

if not exist "%NEW_VAULT%" (
    mkdir "%NEW_VAULT%"
    echo   Created %NEW_VAULT%
) else (
    echo   [OK] %NEW_VAULT% already exists
)

echo.

REM ============================================================
REM Copy executables (.exe files)
REM ============================================================
echo [3/9] Copying executables...

if "%SKIP_TOOLS%"=="1" goto :skip_exes

set "EXE_COUNT=0"
for %%F in ("%OLD_TOOLS%\*.exe") do (
    copy /Y "%%F" "%NEW_BIN%\" >nul
    set /a EXE_COUNT+=1
)
echo   Copied %EXE_COUNT% .exe files

:skip_exes
echo.

REM ============================================================
REM Copy launcher scripts (.cmd files)
REM ============================================================
echo [4/9] Copying launcher scripts...

if "%SKIP_TOOLS%"=="1" goto :skip_cmds

set "CMD_COUNT=0"
for %%F in ("%OLD_TOOLS%\*.cmd") do (
    copy /Y "%%F" "%NEW_BIN%\" >nul
    set /a CMD_COUNT+=1
)

REM Also copy .bat files (like cc-outlook_auth.bat)
for %%F in ("%OLD_TOOLS%\*.bat") do (
    copy /Y "%%F" "%NEW_BIN%\" >nul
    set /a CMD_COUNT+=1
)

echo   Copied %CMD_COUNT% launcher scripts

:skip_cmds
echo.

REM ============================================================
REM Copy subdirectory tools (cc-browser, cc-click, etc.)
REM ============================================================
echo [5/9] Copying subdirectory tools...

if "%SKIP_TOOLS%"=="1" goto :skip_subdirs

for %%D in (cc-browser cc-click cc-trisight cc-computer) do (
    if exist "%OLD_TOOLS%\%%D" (
        if exist "%NEW_BIN%\%%D" rmdir /S /Q "%NEW_BIN%\%%D"
        xcopy /E /I /Q /Y "%OLD_TOOLS%\%%D" "%NEW_BIN%\%%D" >nul
        echo   [OK] Copied %%D
    ) else (
        echo   [SKIP] %%D not found in %OLD_TOOLS%
    )
)

REM Copy documentation
if exist "%OLD_TOOLS%\CC_TOOLS.md" (
    copy /Y "%OLD_TOOLS%\CC_TOOLS.md" "%NEW_BIN%\" >nul
    echo   [OK] Copied CC_TOOLS.md
)

:skip_subdirs
echo.

REM ============================================================
REM Copy data directory (OAuth tokens, shared config)
REM ============================================================
echo [6/9] Copying data directory...

if "%SKIP_TOOLS%"=="1" goto :skip_data

if exist "%OLD_TOOLS%\data" (
    xcopy /E /I /Q /Y "%OLD_TOOLS%\data" "%NEW_DATA%" >nul
    echo   [OK] Copied data directory (OAuth tokens, config)
) else (
    echo   [SKIP] No data directory found in %OLD_TOOLS%
)

:skip_data
echo.

REM ============================================================
REM Copy vault (uses robocopy for large directories)
REM ============================================================
echo [7/9] Copying vault data...

if "%SKIP_VAULT%"=="1" goto :skip_vault

echo   This may take a while for large vaults...
robocopy "%OLD_VAULT%" "%NEW_VAULT%" /E /NFL /NDL /NJH /NJS /NC /NS /NP
REM robocopy returns 0-7 for success, 8+ for errors
if %errorlevel% geq 8 (
    echo   ERROR: Vault copy failed with robocopy error %errorlevel%
    echo   Please copy manually: robocopy "%OLD_VAULT%" "%NEW_VAULT%" /E
) else (
    echo   [OK] Vault copied to %NEW_VAULT%
)

:skip_vault
echo.

REM ============================================================
REM Update PATH (remove old, add new)
REM ============================================================
echo [8/9] Updating user PATH...

powershell -Command "$p=[Environment]::GetEnvironmentVariable('Path','User'); $old='C:\cc-tools'; $new=$env:LOCALAPPDATA+'\cc-tools\bin'; $parts=$p -split ';' | Where-Object {$_ -ne $old -and $_ -ne ''}; $removed=($p -split ';') -contains $old; if($parts -notcontains $new){$parts+=$new}; [Environment]::SetEnvironmentVariable('Path',($parts -join ';'),'User'); if($removed){Write-Host '  [OK] Removed C:\cc-tools from PATH'}else{Write-Host '  [OK] C:\cc-tools was not in PATH'}; Write-Host '  [OK] Added' $new 'to PATH'"

echo.

REM ============================================================
REM Verification
REM ============================================================
echo [9/9] Verifying migration...

set "VERIFY_OK=1"

if exist "%NEW_BIN%\cc-vault.exe" (
    echo   [OK] cc-vault.exe found in new location
) else (
    echo   [FAIL] cc-vault.exe NOT found in %NEW_BIN%
    set "VERIFY_OK=0"
)

if exist "%NEW_BIN%\cc-outlook.exe" (
    echo   [OK] cc-outlook.exe found in new location
) else (
    echo   [FAIL] cc-outlook.exe NOT found in %NEW_BIN%
    set "VERIFY_OK=0"
)

if exist "%NEW_BIN%\cc-browser.cmd" (
    echo   [OK] cc-browser.cmd found in new location
) else (
    if exist "%NEW_BIN%\cc-browser" (
        echo   [OK] cc-browser directory found in new location
    ) else (
        echo   [FAIL] cc-browser NOT found in %NEW_BIN%
        set "VERIFY_OK=0"
    )
)

if exist "%NEW_VAULT%\vault.db" (
    echo   [OK] vault.db found in new location
) else (
    if "%SKIP_VAULT%"=="1" (
        echo   [SKIP] Vault was not migrated
    ) else (
        echo   [FAIL] vault.db NOT found in %NEW_VAULT%
        set "VERIFY_OK=0"
    )
)

echo.
echo ============================================================
if "%VERIFY_OK%"=="1" (
    echo Migration complete!
) else (
    echo Migration completed with warnings. Check output above.
)
echo ============================================================
echo.
echo IMPORTANT: Open a NEW terminal for PATH changes to take effect.
echo.
echo Next steps:
echo   1. Open a new terminal
echo   2. Run: where cc-vault
echo      Expected: %NEW_BIN%\cc-vault.exe
echo   3. Run: cc-vault stats
echo   4. Run: cc-outlook list
echo   5. Run: cc-browser start --workspace mindzie
echo.
echo After verifying everything works, you can remove old locations:
echo   rmdir /S /Q C:\cc-tools
echo   rmdir /S /Q D:\Vault
echo.
echo Old locations have NOT been removed - they serve as backup.
echo.
