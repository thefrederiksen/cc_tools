@echo off
REM CC-Tools Test Runner
REM Runs all unit and integration tests

echo ========================================
echo CC-Tools Test Suite
echo ========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0

echo [1/8] Testing cc-markdown...
cd /d "%~dp0..\src\cc-markdown"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [2/8] Testing cc-powerpoint...
cd /d "%~dp0..\src\cc-powerpoint"
venv\Scripts\python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [3/8] Testing cc-transcribe...
cd /d "%~dp0..\src\cc-transcribe"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [4/8] Testing cc-image...
cd /d "%~dp0..\src\cc-image"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [5/8] Testing cc-voice...
cd /d "%~dp0..\src\cc-voice"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [6/8] Testing cc-whisper...
cd /d "%~dp0..\src\cc-whisper"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [7/8] Testing cc-video...
cd /d "%~dp0..\src\cc-video"
python -m pytest tests/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo [8/8] Running integration tests...
cd /d "%~dp0.."
python -m pytest tests/integration/ -q --tb=line
if %ERRORLEVEL% EQU 0 (set /a PASS_COUNT+=1) else (set /a FAIL_COUNT+=1)

echo.
echo ========================================
echo TEST SUMMARY
echo ========================================
echo Passed: %PASS_COUNT%/8 test suites
echo Failed: %FAIL_COUNT%/8 test suites
echo ========================================

if %FAIL_COUNT% GTR 0 (
    echo.
    echo [X] Some tests failed!
    exit /b 1
) else (
    echo.
    echo [OK] All tests passed!
    exit /b 0
)
