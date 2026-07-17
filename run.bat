@echo off
REM ===========================================================================
REM  Launch Reductus in a native desktop window.
REM  Run install.bat once first to create the .venv.
REM
REM  App output is written to run.log next to this script. If the app fails to
REM  start, this window stays open and shows the error.
REM ===========================================================================
setlocal
cd /d "%~dp0"
set "LOG=%~dp0run.log"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
> "%LOG%" echo Reductus run log - started %DATE% %TIME%
echo Starting reductus (output goes to run.log)...
reductus desktop %* >> "%LOG%" 2>&1
if errorlevel 1 (
    echo.
    echo Reductus exited with an error. Details from run.log:
    echo ------------------------------------------------------------
    type "%LOG%"
    echo ------------------------------------------------------------
    pause
    exit /b 1
)
