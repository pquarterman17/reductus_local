"""
File association utilities for Reductus.

Enables double-clicking .json template files to open them in Reductus.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)


def register_file_associations():
    """
    Register Reductus as the handler for .json template files.

    Supports:
    - Windows: Registry entries (HKCU\Software\Classes)
    - macOS: Not implemented (requires user consent via system settings)
    - Linux: .desktop file in ~/.local/share/applications

    Returns:
        bool: True if registration succeeded or is not needed, False if failed
    """
    if sys.platform == "win32":
        return _register_windows()
    elif sys.platform == "darwin":
        logger.info("macOS file associations require manual setup in System Preferences > Default Apps")
        return True
    else:
        return _register_linux()


def _register_windows():
    """
    Register .json file association on Windows via Registry.

    Returns:
        bool: True if successful
    """
    try:
        import winreg
        from pathlib import Path

        # Get path to reductus executable
        reductus_exe = sys.executable.replace("python.exe", "reductus.exe")
        if not os.path.exists(reductus_exe):
            # Fallback: use python -m reductus.web_gui.run
            reductus_cmd = f'"{sys.executable}" -m reductus.web_gui.run batch --template "%1"'
        else:
            reductus_cmd = f'"{reductus_exe}" desktop --template "%1"'

        # Register file type
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template"
        )
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Reductus Template")
        winreg.CloseKey(key)

        # Register open command
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template\shell\open\command"
        )
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, reductus_cmd)
        winreg.CloseKey(key)

        logger.info("File associations registered for Windows")
        return True

    except Exception as e:
        logger.error(f"Failed to register file associations: {e}")
        return False


def _register_linux():
    """
    Register .json file association on Linux via .desktop file.

    Returns:
        bool: True if successful
    """
    try:
        from pathlib import Path

        # Create ~/.local/share/applications/reductus.desktop
        app_dir = Path.home() / ".local" / "share" / "applications"
        app_dir.mkdir(parents=True, exist_ok=True)

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Reductus
Exec={sys.executable} -m reductus.web_gui.run desktop --template %F
Icon=application-json
Categories=Science;Education;
MimeType=application/json;
Comment=Data reduction for neutron scattering
Terminal=false
"""

        desktop_file = app_dir / "reductus.desktop"
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)

        logger.info(f"File associations registered at {desktop_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to register file associations: {e}")
        return False


def unregister_file_associations():
    """
    Unregister Reductus file associations.

    Returns:
        bool: True if successful
    """
    if sys.platform == "win32":
        return _unregister_windows()
    else:
        return _unregister_linux()


def _unregister_windows():
    """Remove Windows file association registry entries."""
    try:
        import winreg

        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template\shell\open\command"
        )
        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template\shell\open"
        )
        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template\shell"
        )
        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\.json\reductus.template"
        )

        logger.info("File associations removed for Windows")
        return True

    except Exception as e:
        logger.error(f"Failed to unregister file associations: {e}")
        return False


def _unregister_linux():
    """Remove Linux .desktop file."""
    try:
        from pathlib import Path

        desktop_file = Path.home() / ".local" / "share" / "applications" / "reductus.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
            logger.info(f"File associations removed from {desktop_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to unregister file associations: {e}")
        return False
