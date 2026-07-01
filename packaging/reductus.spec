# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the standalone Reductus desktop app (Windows).

Build (from the repo root, inside the build venv):

    pyinstaller packaging/reductus.spec --noconfirm \
        --distpath dist_exe --workpath build_exe

Produces dist_exe/reductus/reductus.exe (onedir bundle). Zip that folder for
the GitHub Release. The bundle carries its own Python 3.13, so the target
machine needs no Python at all.
"""
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

try:
    ROOT = os.path.dirname(SPECPATH)          # repo root (parent of packaging/)
except NameError:
    ROOT = os.path.abspath(os.getcwd())

WEB = os.path.join("reductus", "web_gui", "webreduce")

# --- data files ------------------------------------------------------------
datas = []

# Instrument templates, dataflow schema, CSV/txt lookup tables. Exclude the
# JS build tree here (added explicitly below) and node_modules.
datas += collect_data_files(
    "reductus",
    includes=["**/*.json", "**/*.csv", "**/*.txt"],
    excludes=["**/node_modules/**", "web_gui/webreduce/**", "web_gui/testdata/**"],
)

# Built web client + static assets, mirroring the package layout so that
# importlib.resources.files('reductus.web_gui')/'webreduce' resolves in-bundle.
for sub in ("dist", "img", "css"):
    src = os.path.join(ROOT, WEB, sub)
    if os.path.isdir(src):
        datas.append((src, os.path.join(WEB, sub)))
for fname in ("index.html", "categories_editor.html", "template_editor.html",
              "favicon.ico", "robots.txt"):
    src = os.path.join(ROOT, WEB, fname)
    if os.path.isfile(src):
        datas.append((src, WEB))

# --- hidden imports --------------------------------------------------------
# Instruments and named configs are imported dynamically via importlib, so
# PyInstaller's static analysis can't see them.
hiddenimports = []
hiddenimports += collect_submodules("reductus")
# pywebview's Windows backend (EdgeChromium via pythonnet / WinForms).
hiddenimports += ["clr", "webview.platforms.winforms", "webview.platforms.edgechromium"]

# pywebview ships its own JS bridge data + binaries.
web_datas, web_binaries, web_hidden = collect_all("webview")
datas += web_datas
hiddenimports += web_hidden
binaries = list(web_binaries)

# --- analysis --------------------------------------------------------------
a = Analysis(
    [os.path.join(ROOT, "packaging", "desktop_entry.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "wx", "gi",
        "webview.platforms.gtk", "webview.platforms.cocoa", "webview.platforms.qt",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

_icon = os.path.join(ROOT, WEB, "favicon.ico")
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="reductus",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,   # keep visible for the first smoke test; flip to False for release
    icon=_icon if os.path.isfile(_icon) else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="reductus",
)
