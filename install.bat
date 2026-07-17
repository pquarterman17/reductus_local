@echo off
REM ===========================================================================
REM  Reductus offline installer (Windows)
REM
REM  Installs reductus and all dependencies from the bundled vendor\ wheels,
REM  with no internet access required. Needs Python 3.10-3.13 already installed
REM  and on PATH. After it finishes, launch the app with run.bat.
REM
REM  Everything is also written to install.log next to this script. If this
REM  window ever closes without a message, read install.log - and if that file
REM  was never created, Windows blocked the script before it could run
REM  (antivirus / group policy): open Command Prompt and run install.bat from
REM  there so the output stays visible.
REM ===========================================================================
setlocal
cd /d "%~dp0"
set "LOG=%~dp0install.log"

> "%LOG%" echo Reductus offline installer log
>> "%LOG%" echo Started: %DATE% %TIME%
>> "%LOG%" echo Folder:  %~dp0

echo ============================================================
echo   Reductus offline installer
echo   (full details are written to install.log)
echo ============================================================
echo.

REM --- [1/4] Locate a Python interpreter (prefer the py launcher) -------------
echo [1/4] Looking for Python...
set "PYCMD="
py -3 --version >nul 2>&1 && set "PYCMD=py -3"
if not defined PYCMD ( python --version >nul 2>&1 && set "PYCMD=python" )
if not defined PYCMD (
    >> "%LOG%" echo ERROR: Python 3.10-3.13 was not found on PATH.
    echo ERROR: Python 3.10-3.13 was not found on PATH.
    echo Install Python from https://www.python.org/downloads/ and re-run.
    goto :fail
)
echo Using interpreter: %PYCMD%
%PYCMD% --version
>> "%LOG%" echo Interpreter: %PYCMD%
%PYCMD% --version >> "%LOG%" 2>&1

REM --- [2/4] Create a CLEAN virtual environment -------------------------------
REM  --clear wipes any pre-existing .venv. A stale or foreign .venv (wrong
REM  Python version, built on another machine) otherwise poisons the install:
REM  pip reports its packages as "already satisfied" and skips the good wheels.
echo [2/4] Creating virtual environment (.venv)...
%PYCMD% -m venv --clear .venv >> "%LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: failed to create the virtual environment.
    goto :fail
)
call ".venv\Scripts\activate.bat"

REM --- [3/4] Install the build backend from vendored wheels -------------------
REM  Force-reinstall so the vendored setuptools/wheel REPLACE any stale copy the
REM  venv seeded from the base interpreter. Some Python builds seed an old
REM  setuptools that crashes under Python 3.12+ (pkgutil.ImpImporter was
REM  removed); without --force-reinstall pip reports "already satisfied" and the
REM  broken copy is used to build reductus in the next step.
echo [3/4] Installing build tools from local wheels...
python -m pip install --no-index --find-links vendor --upgrade --force-reinstall setuptools wheel >> "%LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: could not install setuptools/wheel from vendor\.
    goto :fail
)

REM --- [4/4] Install reductus + dependencies from vendored wheels -------------
echo [4/4] Installing reductus and dependencies from local wheels...
echo       This takes a few minutes; progress is written to install.log.
python -m pip install --no-index --find-links vendor --no-build-isolation ".[all]" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: offline install failed.
    echo   Most likely vendor\ has no wheels matching your Python version:
    python --version
    echo   The bundled wheels cover Python 3.10 - 3.13 on 64-bit Windows.
    goto :fail
)

>> "%LOG%" echo Finished OK: %DATE% %TIME%
echo.
echo ============================================================
echo   Success!  Launch reductus with:   run.bat
echo ============================================================
pause
exit /b 0

:fail
>> "%LOG%" echo FAILED: %DATE% %TIME%
echo.
echo Install FAILED. Full details are in install.log (opening it now).
if exist "%LOG%" start notepad "%LOG%"
pause
exit /b 1
