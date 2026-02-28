"""
User-specific data directory for reductus local state.

Directory:
  Windows: %APPDATA%/reductus   (via platformdirs, fallback to ~/.reductus)
  Linux:   ~/.local/share/reductus

Contents:
  settings.json       – persisted user preferences (may override default config keys)
  recent_paths.json   – last-browsed pathlist per data source name
  templates/          – saved reduction templates (Phase 4)

Env override: REDUCTUS_DATA_DIR overrides the base directory (useful for tests).
"""

import os
import json
import pathlib


def get_user_data_dir() -> pathlib.Path:
    """Get the user data directory, creating it if needed."""
    env = os.environ.get("REDUCTUS_DATA_DIR")
    if env:
        base = pathlib.Path(env)
    else:
        try:
            from platformdirs import user_data_dir
            base = pathlib.Path(user_data_dir("reductus", "reductus"))
        except ImportError:
            base = pathlib.Path.home() / ".reductus"
    base.mkdir(parents=True, exist_ok=True)
    return base


def load_settings() -> dict:
    """Load user settings from settings.json."""
    path = get_user_data_dir() / "settings.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_settings(settings: dict) -> None:
    """Save user settings to settings.json."""
    _atomic_write(get_user_data_dir() / "settings.json", settings)


def load_recent_paths() -> dict:
    """Return {source_name: pathlist_list, ...}"""
    path = get_user_data_dir() / "recent_paths.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_recent_path(source_name: str, pathlist: list) -> None:
    """Save the most recent path for a data source."""
    recent = load_recent_paths()
    recent[source_name] = list(pathlist)
    _atomic_write(get_user_data_dir() / "recent_paths.json", recent)


def get_templates_dir() -> pathlib.Path:
    """Get the templates directory, creating it if needed."""
    d = get_user_data_dir() / "templates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write(path: pathlib.Path, data: dict) -> None:
    """Atomically write JSON data to a file using a temporary file."""
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
