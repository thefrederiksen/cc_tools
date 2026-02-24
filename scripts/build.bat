@echo off
REM Build all cc_tools and copy to C:\cc-tools
REM Usage: scripts\build.bat

setlocal enabledelayedexpansion

echo ============================================
echo Building all cc_tools
echo ============================================
echo.

set "REPO_DIR=%~dp0.."
set "INSTALL_DIR=C:\cc-tools"
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
REM Directory names use underscores, exe names use dashes
REM ============================================
set "PYTHON_TOOLS=cc_comm_queue cc_crawl4ai cc_gmail cc_hardware cc_image cc_linkedin cc_markdown cc_outlook cc_photos cc_reddit cc_setup cc_transcribe cc_vault cc_video cc_voice cc_whisper cc_youtube_info"

for %%T in (%PYTHON_TOOLS%) do (
    echo.
    echo --------------------------------------------
    echo Building %%T...
    echo --------------------------------------------

    set "TOOL_DIR=%REPO_DIR%\src\%%T"

    REM Convert underscore to dash for exe name (cc_outlook -> cc-outlook)
    set "EXE_NAME=%%T"
    set "EXE_NAME=!EXE_NAME:_=-!"

    if exist "!TOOL_DIR!\build.ps1" (
        pushd "!TOOL_DIR!"
        powershell -ExecutionPolicy Bypass -File build.ps1

        if !errorlevel! equ 0 (
            REM Copy exe to install directory
            REM Handle special case: cc_setup builds as cc-tools-setup.exe
            if "%%T"=="cc_setup" (
                if exist "dist\cc-tools-setup.exe" (
                    copy /Y "dist\cc-tools-setup.exe" "%INSTALL_DIR%\" >nul
                    echo [OK] cc-tools-setup.exe copied to %INSTALL_DIR%
                    set /a SUCCESS_COUNT+=1
                ) else (
                    echo [FAIL] cc-tools-setup.exe not found after build
                    set "FAILED=!FAILED! %%T"
                    set /a FAIL_COUNT+=1
                )
            ) else if exist "dist\!EXE_NAME!.exe" (
                copy /Y "dist\!EXE_NAME!.exe" "%INSTALL_DIR%\" >nul
                echo [OK] !EXE_NAME!.exe copied to %INSTALL_DIR%
                set /a SUCCESS_COUNT+=1
            ) else (
                echo [FAIL] !EXE_NAME!.exe not found after build
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
echo Building cc_browser (Node.js)...
echo --------------------------------------------

set "BROWSER_SRC=%REPO_DIR%\src\cc_browser"
set "BROWSER_DEST=%INSTALL_DIR%\cc-browser"

if exist "%BROWSER_SRC%\build.ps1" (
    pushd "%BROWSER_SRC%"
    powershell -ExecutionPolicy Bypass -File build.ps1

    if !errorlevel! equ 0 (
        REM Create destination directory
        if not exist "%BROWSER_DEST%" mkdir "%BROWSER_DEST%"
        if not exist "%BROWSER_DEST%\src" mkdir "%BROWSER_DEST%\src"

        REM Copy built files from dist
        copy /Y "dist\package.json" "%BROWSER_DEST%\" >nul
        copy /Y "dist\README.md" "%BROWSER_DEST%\" >nul
        copy /Y "dist\src\*.mjs" "%BROWSER_DEST%\src\" >nul

        REM Copy node_modules
        if exist "%BROWSER_DEST%\node_modules" rmdir /S /Q "%BROWSER_DEST%\node_modules"
        xcopy /E /I /Q /Y "dist\node_modules" "%BROWSER_DEST%\node_modules" >nul

        REM Create launcher script in C:\cc-tools
        echo @node "%%~dp0cc-browser\src\cli.mjs" %%*> "%INSTALL_DIR%\cc-browser.cmd"

        echo [OK] cc-browser installed to %BROWSER_DEST%
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] Build failed for cc_browser
        set "FAILED=!FAILED! cc_browser"
        set /a FAIL_COUNT+=1
    )
    popd
) else (
    echo [SKIP] No build.ps1 found for cc_browser
)

REM ============================================
REM .NET tools (cc_click, cc_trisight)
REM ============================================
echo.
echo --------------------------------------------
echo Building cc_click (.NET)...
echo --------------------------------------------

set "CCCLICK_SRC=%REPO_DIR%\src\cc_click"
set "CCCLICK_DEST=%INSTALL_DIR%\cc-click"

if exist "%CCCLICK_SRC%\cc_click.slnx" (
    pushd "%CCCLICK_SRC%"
    dotnet publish -c Release -o "%CCCLICK_DEST%"

    if !errorlevel! equ 0 (
        REM Create launcher script (exe name is now cc-click.exe due to AssemblyName)
        echo @"%%~dp0cc-click\cc-click.exe" %%*> "%INSTALL_DIR%\cc-click.cmd"
        echo [OK] cc-click installed to %CCCLICK_DEST%
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] Build failed for cc_click
        set "FAILED=!FAILED! cc_click"
        set /a FAIL_COUNT+=1
    )
    popd
) else (
    echo [SKIP] No cc_click.slnx found
)

echo.
echo --------------------------------------------
echo Building cc_trisight (.NET)...
echo --------------------------------------------

set "TRISIGHT_SRC=%REPO_DIR%\src\cc_trisight"
set "TRISIGHT_DEST=%INSTALL_DIR%\cc-trisight"

if exist "%TRISIGHT_SRC%\cc_trisight.slnx" (
    pushd "%TRISIGHT_SRC%"
    dotnet publish -c Release -o "%TRISIGHT_DEST%"

    if !errorlevel! equ 0 (
        REM Create launcher script (exe name is now cc-trisight.exe due to AssemblyName)
        echo @"%%~dp0cc-trisight\cc-trisight.exe" %%*> "%INSTALL_DIR%\cc-trisight.cmd"
        echo [OK] cc-trisight installed to %TRISIGHT_DEST%
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] Build failed for cc_trisight
        set "FAILED=!FAILED! cc_trisight"
        set /a FAIL_COUNT+=1
    )
    popd
) else (
    echo [SKIP] No cc_trisight.slnx found
)

REM ============================================
REM Copy documentation
REM ============================================
echo.
echo --------------------------------------------
echo Copying documentation...
echo --------------------------------------------

if exist "%REPO_DIR%\docs\CC_TOOLS.md" (
    copy /Y "%REPO_DIR%\docs\CC_TOOLS.md" "%INSTALL_DIR%\" >nul
    echo [OK] CC_TOOLS.md copied to %INSTALL_DIR%
) else (
    echo [SKIP] docs\CC_TOOLS.md not found
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
