# Offline Installation Guide

This directory contains pre-downloaded Python wheel files so you can install
reductus on machines with **no internet access**.

## Supported Platforms

The vendored wheels cover:

| Platform      | Architecture | Python |
|---------------|--------------|--------|
| Windows       | x86_64       | 3.13   |
| Linux (glibc) | x86_64       | 3.13   |

## Quick Install

### 1. Copy the repo to the target machine

Copy the entire `reductus/` directory (including `vendor/`) onto the
offline machine via USB drive, network share, etc.

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install reductus

From the repo root (the directory containing `pyproject.toml`):

```bash
pip install --no-index --find-links vendor/ ".[all]"
```

This installs reductus and every dependency entirely from local wheel files.

For **development** (editable mode — code changes take effect immediately):

```bash
pip install --no-index --find-links vendor/ -e ".[all]"
```

### 4. Verify

```bash
python -c "import reductus; print('OK')"
```

### 5. Run

```bash
# Web server (opens in browser at http://localhost:8002)
reductus

# Desktop native window (no browser needed)
reductus desktop
```

## Install Subsets

If you don't need every optional dependency, you can install a smaller set:

```bash
# Core only (numpy, scipy, uncertainties, docutils, pytz)
pip install --no-index --find-links vendor/ .

# Core + web server
pip install --no-index --find-links vendor/ ".[server]"

# Core + HDF5 support
pip install --no-index --find-links vendor/ ".[nexus_files]"

# Core + desktop GUI
pip install --no-index --find-links vendor/ ".[desktop]"
```

## Adding Another Platform

On an **internet-connected** machine, run `pip download` to fetch wheels for
the target platform. For example:

```bash
# macOS Apple Silicon
pip download -d vendor/ \
    --platform macosx_11_0_arm64 \
    --python-version 3.13 \
    --only-binary=:all: \
    ".[all]" setuptools wheel

# Linux ARM64
pip download -d vendor/ \
    --platform manylinux2014_aarch64 \
    --python-version 3.13 \
    --only-binary=:all: \
    ".[all]" setuptools wheel
```

Pure-Python wheels already present in `vendor/` will be skipped automatically.

## Adding Another Python Version

Replace `--python-version 3.13` with the target version (e.g. `3.10`, `3.11`,
`3.12`). Only platform-specific wheels (numpy, scipy, h5py, etc.) differ
between Python versions; pure-Python wheels are shared.

```bash
pip download -d vendor/ \
    --platform win_amd64 \
    --python-version 3.10 \
    --only-binary=:all: \
    ".[all]" setuptools wheel
```

## Troubleshooting

**"No matching distribution found"** — The vendored wheels don't cover your
platform or Python version. Run `pip download` on a connected machine for
your specific target (see above).

**"Could not build wheels for reductus"** — Make sure `setuptools` and `wheel`
are available. They are included in `vendor/`, but your base pip may be too
old. Upgrade pip first:

```bash
pip install --no-index --find-links vendor/ setuptools wheel
pip install --no-index --find-links vendor/ ".[all]"
```

**Permission errors on Linux** — Use `python3 -m venv` to create an isolated
environment rather than installing system-wide.
