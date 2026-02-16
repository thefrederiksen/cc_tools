@echo off
REM Build all cc_tools and copy to C:\cc_tools
REM Usage: scripts\build.bat

setlocal enabledelayedexpansion

echo ============================================
echo Building all cc_tools
echo ============================================
echo.

set "REPO_DIR=%~dp0.."
set "INSTALL_DIR=C:\cc_tools"
set "FAILED="
set "SUCCESS_COUNT=0"
set "FAIL_COUNT=0"

REM Create install directory if it doesn't exist
if not exist "%INSTALL_DIR%" (
    echo Creating %INSTALL_DIR%...
    mkdir "%INSTALL_DIR%"
)

REM ============================================
REM Python tools (built with PyInstaller)
REM ============================================
set "PYTHON_TOOLS=cc_gmail cc_image cc_markdown cc_setup cc_transcribe cc_video cc_voice cc_whisper"

for %%T in (%PYTHON_TOOLS%) do (
    echo.
    echo --------------------------------------------
    echo Building %%T...
    echo --------------------------------------------

    set "TOOL_DIR=%REPO_DIR%\src\%%T"

    if exist "!TOOL_DIR!\build.ps1" (
        pushd "!TOOL_DIR!"
        powershell -ExecutionPolicy Bypass -File build.ps1

        if !errorlevel! equ 0 (
            REM Copy exe to install directory
            if exist "dist\%%T.exe" (
                copy /Y "dist\%%T.exe" "%INSTALL_DIR%\" >nul
                echo [OK] %%T.exe copied to %INSTALL_DIR%
                set /a SUCCESS_COUNT+=1
            ) else (
                echo [FAIL] %%T.exe not found after build
                set "FAILED=!FAILED! %%T"
                set /a FAIL_COUNT+=1
            )
        ) else (
            echo [FAIL] Build failed for %%T
            set "FAILED=!FAILED! %%T"
            set /a FAIL_COUNT+=1
        )
        popd
    ) else (
        echo [SKIP] No build.ps1 found for %%T
    )
)

REM ============================================
REM Node.js tools (cc_browser)
REM ============================================
echo.
echo --------------------------------------------
echo Setting up cc_browser (Node.js)...
echo --------------------------------------------

set "BROWSER_SRC=%REPO_DIR%\src\cc_browser"
set "BROWSER_DEST=%INSTALL_DIR%\cc_browser"

if exist "%BROWSER_SRC%\package.json" (
    REM Install npm dependencies
    pushd "%BROWSER_SRC%"
    echo Installing npm dependencies...
    call npm install --silent
    if !errorlevel! neq 0 (
        echo [FAIL] npm install failed for cc_browser
        set "FAILED=!FAILED! cc_browser"
        set /a FAIL_COUNT+=1
        popd
        goto :summary
    )
    popd

    REM Create destination directory
    if not exist "%BROWSER_DEST%" mkdir "%BROWSER_DEST%"
    if not exist "%BROWSER_DEST%\src" mkdir "%BROWSER_DEST%\src"

    REM Copy source files
    copy /Y "%BROWSER_SRC%\package.json" "%BROWSER_DEST%\" >nul
    copy /Y "%BROWSER_SRC%\README.md" "%BROWSER_DEST%\" >nul
    copy /Y "%BROWSER_SRC%\src\*.mjs" "%BROWSER_DEST%\src\" >nul

    REM Copy node_modules
    if exist "%BROWSER_DEST%\node_modules" rmdir /S /Q "%BROWSER_DEST%\node_modules"
    xcopy /E /I /Q /Y "%BROWSER_SRC%\node_modules" "%BROWSER_DEST%\node_modules" >nul

    REM Create launcher script in C:\cc_tools
    echo @node "%%~dp0cc_browser\src\cli.mjs" %%*> "%INSTALL_DIR%\cc-browser.cmd"

    echo [OK] cc_browser installed to %BROWSER_DEST%
    set /a SUCCESS_COUNT+=1
) else (
    echo [SKIP] cc_browser source not found
)

:summary
echo.
echo ============================================
echo Build Summary
echo ============================================
echo Successful: %SUCCESS_COUNT%
echo Failed: %FAIL_COUNT%
if defined FAILED (
    echo Failed tools:%FAILED%
    exit /b 1
) else (
    echo All tools built successfully!
    echo.
    echo Executables installed to: %INSTALL_DIR%
    echo.
    echo Run scripts\install.bat to add %INSTALL_DIR% to your PATH
)
