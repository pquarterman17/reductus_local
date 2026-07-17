#!/usr/bin/env python3
"""
Assemble the Windows release artifacts for reductus.

Produces two zips in release/:

  reductus-<ver>-windows-desktop.zip
      The standalone PyInstaller bundle. Download, unzip, double-click
      reductus.exe. No Python needed on the target machine.

  reductus-<ver>-windows-offline.zip
      Full source + vendored wheels (Python 3.10-3.13, 64-bit Windows) +
      install.bat/run.bat. Unzip, run install.bat once, then run.bat.
      Fully offline (no internet / no PyPI access required).

Prerequisites (run these first, from the repo root, in the build venv):
  1. Build the web client:   npm --prefix reductus/web_gui/webreduce run build
  2. Build the exe:          pyinstaller packaging/reductus.spec --noconfirm \
                                 --distpath dist_exe --workpath build_exe
  3. Download wheels:        pip download -d release/vendor --platform win_amd64 \
                                 --python-version 3.1X --only-binary=:all: <pkgs>

Then:  python packaging/make_release.py
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ROOT / "release"
STAGE = RELEASE / "stage"
EXE_DIR = ROOT / "dist_exe" / "reductus"
WIN_VENDOR = RELEASE / "vendor"

OFFLINE_README = """\
Reductus - offline install for Windows (Python 3.10 - 3.13)
===========================================================

This bundle installs and runs reductus with NO internet access required.
You need Python 3.10, 3.11, 3.12, or 3.13 installed (64-bit) and on PATH.

  1. Unzip this folder anywhere (e.g. your Desktop).
  2. Double-click  install.bat   (creates a local .venv from the bundled
     wheels in vendor\\ - this takes a few minutes).
  3. Double-click  run.bat       (opens reductus in a native window).

To check your Python version, open Command Prompt and run:  python --version

Troubleshooting
---------------
* install.bat logs everything it does to install.log in this folder, and
  run.bat logs to run.log. If anything fails, read those files first.
* If a window flashes open and closes and install.log was NOT created,
  Windows blocked the script before it could run (antivirus or group
  policy). Open Command Prompt yourself so the output stays visible:
      cd /d "<this folder>"
      install.bat
* If install.bat reports "no wheels matching your Python version", your
  Python is outside the 3.10-3.13 range this bundle supports.
* Fully manual install (same steps as install.bat), from Command Prompt
  in this folder:
      py -3 -m venv --clear .venv
      .venv\\Scripts\\python -m pip install --no-index --find-links vendor --force-reinstall setuptools wheel
      .venv\\Scripts\\python -m pip install --no-index --find-links vendor --no-build-isolation ".[all]"
      .venv\\Scripts\\reductus desktop
"""

DESKTOP_README = """\
Reductus - standalone desktop app for Windows
=============================================

No installation and no Python required.

  1. Unzip this folder anywhere.
  2. Double-click  reductus.exe

A native window opens with the reductus interface. The first launch may take a
few seconds while the bundled runtime unpacks. Close the window to exit.
"""


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def get_version():
    out = subprocess.check_output(
        [sys.executable, "-c", "import reductus; print(reductus.__version__)"],
        cwd=ROOT,
    )
    return out.decode().strip()


def zip_tree(folder: Path, zip_path: Path, arc_prefix: str):
    """Zip everything under `folder`, placing it under arc_prefix/ in the zip."""
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, os.path.join(arc_prefix, str(p.relative_to(folder))))
                count += 1
    return count


def build_offline_zip(ver: str) -> Path:
    if not WIN_VENDOR.is_dir() or not any(WIN_VENDOR.glob("*.whl")):
        sys.exit(f"ERROR: no Windows wheels in {WIN_VENDOR}. Run pip download first.")

    name = f"reductus-{ver}-windows-offline"
    stage = STAGE / name
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # Clean, git-tracked source tree (includes built webreduce/dist/, install.bat,
    # run.bat, packaging/). Extract, then replace vendor/ with the Windows wheels.
    src_zip = RELEASE / "_src.zip"
    run(["git", "archive", "--format=zip", "-o", str(src_zip), "HEAD"])
    with zipfile.ZipFile(src_zip) as z:
        z.extractall(stage)
    src_zip.unlink()

    # git archive exports every TRACKED file, so an accidentally committed
    # build environment rides straight into the release (this shipped a full
    # dev .venv once - pip then saw its packages as "already satisfied" on
    # target machines and the app crashed with no visible error).
    junk = sorted(
        p for p in stage.rglob("*")
        if p.name in (".venv", "__pycache__") or p.name.endswith(".egg-info")
    )
    if junk:
        listing = "\n  ".join(str(p.relative_to(stage)) for p in junk[:10])
        sys.exit(
            "ERROR: build-environment files are git-tracked and would ship "
            f"in the release:\n  {listing}\n"
            "Untrack them (git rm -r --cached <path>), commit, and rebuild."
        )

    vendor_dst = stage / "vendor"
    if vendor_dst.exists():
        shutil.rmtree(vendor_dst)
    shutil.copytree(WIN_VENDOR, vendor_dst)

    (stage / "HOW_TO_RUN.txt").write_text(OFFLINE_README, encoding="utf-8")

    out = RELEASE / f"{name}.zip"
    if out.exists():
        out.unlink()
    n = zip_tree(stage, out, name)
    print(f"  -> {out.name}  ({n} files, {out.stat().st_size / 1e6:.1f} MB)")
    return out


def build_desktop_zip(ver: str) -> Path:
    if not EXE_DIR.is_dir():
        sys.exit(f"ERROR: exe bundle not found at {EXE_DIR}. Build it first.")

    name = f"reductus-{ver}-windows-desktop"
    stage = STAGE / name
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # Copy the whole onedir bundle, then drop in a readme.
    shutil.copytree(EXE_DIR, stage, dirs_exist_ok=True)
    (stage / "README.txt").write_text(DESKTOP_README, encoding="utf-8")

    out = RELEASE / f"{name}.zip"
    if out.exists():
        out.unlink()
    n = zip_tree(stage, out, name)
    print(f"  -> {out.name}  ({n} files, {out.stat().st_size / 1e6:.1f} MB)")
    return out


def main():
    ver = get_version()
    print(f"Reductus version: {ver}")
    RELEASE.mkdir(exist_ok=True)
    STAGE.mkdir(exist_ok=True)

    print("Building desktop (.exe) zip...")
    desktop = build_desktop_zip(ver)
    print("Building offline (source + wheels) zip...")
    offline = build_offline_zip(ver)

    print("\nRelease artifacts:")
    for p in (desktop, offline):
        print(f"  {p}   ({p.stat().st_size / 1e6:.1f} MB)")
    print("\nAttach these to a GitHub Release with:")
    print(f"  gh release create v{ver} \"{desktop}\" \"{offline}\" \\")
    print(f"      --title \"reductus v{ver}\" --notes \"Windows desktop + offline builds\"")


if __name__ == "__main__":
    main()
