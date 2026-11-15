@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        py -3 "%~dp0start_project.py"
        goto finished
    )
)
where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        python "%~dp0start_project.py"
        goto finished
    )
)
echo Python was not found. Install Python 3.11 or 3.12 from python.org,
echo select "Add Python to PATH" during installation, and try again.
pause
exit /b 1
:finished
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo Project could not start. Read the message above for help.
    pause
)
exit /b %RESULT%
