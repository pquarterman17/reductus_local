@echo off
REM ===========================================================================
REM  Launch Reductus in a native desktop window.
REM  Run install.bat once first to create the .venv.
REM ===========================================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
reductus desktop %*
