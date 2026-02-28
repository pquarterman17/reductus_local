# Reductus Local-First Application Plan

## Phase 1: Local-First Foundation ✓ COMPLETE

### 1a. User settings & state persistence
- [x] Implemented
- [x] Tested
- Create `%APPDATA%/reductus/` (Windows) / `~/.config/reductus/` (Unix) for:
  - `settings.json` — persistent preferences (data dirs, instruments, cache, port)
  - `recent_paths.json` — last-browsed directories
  - `templates/` — user-saved templates
- Config priority: CLI flags > settings.json > config.py > default.py

### 1b. Smart data source handling
- [x] Implemented
- [x] Tested
- `--data-dir` CLI flag (repeatable) to register named local data sources
- Auto-detect: on startup, briefly probe remote sources (1-2 second timeout); show only reachable ones
- Remember and re-open last-used paths across sessions
- On Windows, show available drive letters as top-level shortcuts in the "local" source

### 1c. Offline resilience
- [x] Implemented
- [x] Tested
- Remote source probing is async and non-blocking — app starts immediately
- Unreachable sources shown grayed out in UI (not removed, can retry)
- No startup failure due to network issues

---

## Phase 2: Python Scripting API ✓ COMPLETE

### 2a. Public reduction API (`reductus.api` or `reductus.reduce`)
- [x] Implemented
- [x] Tested
- Direct Python interface to run reduction templates without the web server:
  ```python
  from reductus import reduce

  result = reduce.load_template("my_template.json")
  result = reduce.run(template, data_dir="D:/SANS Data")
  result.save("output/reduced_data.dat")
  ```
- Wraps the existing `dataflow/calc.py` machinery
- Accepts local file paths directly (no `fileinfo` dicts needed)

### 2b. Batch processing CLI
- [x] Implemented
- [x] Tested
- `reductus batch --template my_template.json --data-dir "D:\Data" --output "D:\Results"`
- Process all matching files in a directory using a saved template
- Could also accept a glob pattern: `reductus batch --template t.json --files "D:\Data\*.nxs"`

---

## Phase 3: Desktop App Wrapper ✓ COMPLETE

### 3a. pywebview-based desktop app ✓ COMPLETE
- [x] Implemented
- [x] Tested
- Wrap the Flask server + web UI in a native window using pywebview
- Benefits over Electron: pure Python, lightweight (~5MB), no Node.js dependency
- Native file dialogs for open/save (via `webview.windows[0].create_file_dialog()`)
- System tray icon optional

### 3b. Desktop-native file interactions ✓ COMPLETE
- [x] Implemented
- [x] Tested
- Native "Open folder" dialog to add data directories
- Native "Save as" dialog for exporting reduced data
- Drag-and-drop from Explorer into the pywebview window
- File associations: double-click `.json` templates to open in reductus

### 3c. Packaging (Upcoming)
- [ ] Implemented
- [ ] Tested
- PyInstaller or cx_Freeze to create a single `.exe` / `.dmg`
- Or distribute via `pip install reductus[desktop]` with pywebview as optional dependency
- `reductus --desktop` launches in native window; `reductus` launches in browser (backward-compatible)

---

## Phase 4: Template Management ✓ COMPLETE

### 4a. Local template storage ✓ COMPLETE
- [x] Implemented
- [x] Tested
- Save/load templates to `%APPDATA%/reductus/templates/`
- API endpoints for Save/Load operations

### 4b. Built-in template library ✓ COMPLETE
- [x] Implemented
- [x] Tested
- Ship default templates in `reductus/configurations/templates/` for common workflows
- Discoverable via list_templates(category="built-in")
- Clone functionality for customization

---

## Phase 5: File Browser & Export UX ✓ COMPLETE (Backend)

### 5a. Improved file browser ✓ COMPLETE
- [x] Implemented (backend)
- [x] Tested
- Pinned/favorite directories API (frontend UI implementation pending)
- Export history tracking
- Smart suggestions combining favorites + recent

### 5b. Better export ✓ COMPLETE
- [x] Implemented (backend)
- [x] Tested
- Save location tracking API
- Default save location management
- Remember last export locations (configurable, default 50)
- Recent export list sorted by recency

---

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Desktop wrapper | pywebview | Pure Python, lightweight, native file dialogs, no Electron overhead |
| Packaging | `pip install reductus[desktop]` | Optional extra, doesn't bloat the base package |
| State storage | `platformdirs` library | Cross-platform user data/config directories |
| Default cache (local) | `diskcache` | Persistent across sessions, no external service |
| Scripting API | Thin wrapper over `dataflow/calc.py` | Reuses existing reduction engine, no duplication |

## Implementation Notes

- Phases 1 and 2 are independent and can be developed in parallel
- Phase 3 builds on Phase 1
- Phases 4 and 5 can happen anytime after Phase 1
