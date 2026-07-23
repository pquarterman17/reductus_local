@echo off
REM ===========================================================================
REM  Reductus uninstaller (Windows)
REM
REM  Removes a reductus install created by install.bat (the local .venv) and,
REM  if you choose, the user data reductus keeps OUTSIDE this folder:
REM
REM    %APPDATA%\reductus        settings, recent paths, saved templates
REM    %USERPROFILE%\.reductus   the on-disk reduction cache (can grow large)
REM
REM  It does NOT delete this folder itself - a running .bat cannot remove the
REM  directory it is executing from. Delete the folder by hand once this
REM  finishes (the final message prints its full path).
REM
REM  Works for both bundles: the offline install (has a .venv) and the
REM  standalone desktop .exe (no .venv - only the outside data is cleaned).
REM ===========================================================================
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Reductus uninstaller
echo ============================================================
echo.
echo Close reductus before continuing - an open app locks files
echo inside .venv and blocks their removal.
echo.
pause
echo.

REM --- Remove the local virtual environment (offline install only) -----------
if exist ".venv\" (
    echo Removing .venv ...
    rmdir /s /q ".venv"
    if exist ".venv\" (
        echo   WARNING: .venv could not be fully removed. Is reductus still
        echo   running? Close it and run this script again.
    ) else (
        echo   .venv removed.
    )
) else (
    echo No .venv here - nothing to remove for a desktop-exe bundle.
)

REM --- Remove logs written next to the scripts -------------------------------
if exist "install.log" del /q "install.log"
if exist "run.log"     del /q "run.log"

REM --- Offer to remove user data kept OUTSIDE this folder --------------------
echo.
echo Reductus also stores data outside this folder:
echo   "%APPDATA%\reductus"        settings, recent paths, saved templates
echo   "%USERPROFILE%\.reductus"   reduction cache ^(can grow large^)
echo.
choice /C YN /N /M "Also delete this saved data and cache? [Y/N]: "
if errorlevel 2 goto skip_data

echo Removing user data ...
if exist "%APPDATA%\reductus\"      rmdir /s /q "%APPDATA%\reductus"
if exist "%USERPROFILE%\.reductus\" rmdir /s /q "%USERPROFILE%\.reductus"
echo   User data removed.
goto done

:skip_data
echo Kept your settings, templates, and cache.

:done
echo.
echo ============================================================
echo   Done. To finish, delete this folder:
echo   %~dp0
echo ============================================================
echo.
pause
endlocal
exit /b 0
