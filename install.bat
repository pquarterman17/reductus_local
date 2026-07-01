@echo off
REM ===========================================================================
REM  Reductus offline installer (Windows)
REM
REM  Installs reductus and all dependencies from the bundled vendor\ wheels,
REM  with no internet access required. Needs Python 3.10-3.13 already installed
REM  and on PATH. After it finishes, launch the app with run.bat.
REM ===========================================================================
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Reductus offline installer
echo ============================================================
echo.

REM --- Locate a Python interpreter (prefer the py launcher) -------------------
set "PYCMD="
py -3 --version >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD ( python --version >nul 2>&1 && set "PYCMD=python" )
if not defined PYCMD (
    echo ERROR: Python 3.10-3.13 was not found on PATH.
    echo Install Python from https://www.python.org/downloads/ and re-run.
    pause
    exit /b 1
)

echo Using interpreter: %PYCMD%
%PYCMD% --version
echo.

REM --- Create an isolated virtual environment --------------------------------
echo Creating virtual environment (.venv)...
%PYCMD% -m venv .venv
if errorlevel 1 (
    echo ERROR: failed to create the virtual environment.
    pause
    exit /b 1
)
call ".venv\Scripts\activate.bat"

REM --- Install offline from vendored wheels ----------------------------------
echo Installing build backend from local wheels...
python -m pip install --no-index --find-links vendor setuptools wheel
if errorlevel 1 (
    echo ERROR: could not install setuptools/wheel from vendor\.
    pause
    exit /b 1
)

echo Installing reductus and dependencies from local wheels...
python -m pip install --no-index --find-links vendor --no-build-isolation ".[all]"
if errorlevel 1 (
    echo.
    echo ERROR: offline install failed.
    echo   Most likely vendor\ has no wheels matching your Python version:
    python --version
    echo   The bundled wheels cover Python 3.10 - 3.13 on 64-bit Windows.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Success!  Launch reductus with:   run.bat
echo ============================================================
pause
