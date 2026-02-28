# Reductus User Guide

Practical guide for running data reductions with Reductus.

---

## Quick Start

### Installation

```bash
# Install Reductus with all features
pip install "reductus[all]"

# Verify installation
python -c "from reductus import reduce; print('Ready!')"
```

### First Reduction (Web Mode)

```bash
# Start web server
reductus

# Open http://localhost:8002 in your browser
# Use the web UI as before
```

### First Reduction (Python API)

```python
from reductus import reduce

# Load a template
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Run on your data file
result = template.run(files=["D:/my_data/sample.nxs"])

# Save results
result.save("D:/output/")
```

### First Reduction (Batch CLI)

```bash
# Process all files in a directory
reductus batch \
  --template ncnr.refl.unpolarized.json \
  --data-dir "D:/my_data" \
  --output "D:/output"
```

---

## Use Case: Single File Reduction

**Goal:** Reduce one reflectivity data file

### Method 1: Web Browser

1. Start server: `reductus`
2. Open http://localhost:8002
3. Click "Load file" → browse to `sample.nxs`
4. Click "Save" → choose output directory
5. Download results

### Method 2: Python Script

```python
from reductus import reduce

# Load template (choose appropriate for your data)
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Run reduction
result = template.run(files=["D:/data/sample.nxs"])

# Save to disk
result.save("D:/results/")

print("Done! Check D:/results/")
```

### Method 3: CLI One-Liner

```bash
reductus batch \
  --template ncnr.refl.unpolarized.json \
  --files "D:/data/sample.nxs" \
  --output "D:/results"
```

---

## Use Case: Batch Processing (Many Files)

**Goal:** Reduce 100+ files from a beamtime

### Method 1: Python Script (Recommended)

```python
from reductus import reduce
from pathlib import Path

# Load template once
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Get all data files
data_dir = Path("D:/beamtime_2024-02")
files = list(data_dir.glob("*.nxs"))

print(f"Processing {len(files)} files...")

# Process each file
for i, filepath in enumerate(files, 1):
    print(f"[{i}/{len(files)}] {filepath.name}...", end=" ", flush=True)

    result = template.run(files=[str(filepath)])
    result.save(f"D:/reduced/{filepath.stem}/")

    print("✓")

print("All done!")
```

### Method 2: Batch CLI

```bash
# Process all matching files
reductus batch \
  --template ncnr.refl.unpolarized.json \
  --data-dir "D:/beamtime_2024-02" \
  --output "D:/reduced/"
```

### Method 3: Parallel Processing (Advanced)

```python
from reductus import reduce
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

template = reduce.load_template("ncnr.refl.unpolarized.json")

def process_file(filepath):
    """Process a single file"""
    result = template.run(files=[str(filepath)])
    output_dir = f"D:/reduced/{filepath.stem}/"
    result.save(output_dir)
    return filepath.name

# Process up to 4 files in parallel
data_files = list(Path("D:/beamtime").glob("*.nxs"))
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_file, data_files)
    for filename in results:
        print(f"✓ {filename}")
```

---

## Use Case: Custom Data Reduction

**Goal:** Create a custom reduction workflow

### Step 1: Clone Built-in Template

```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()

# Clone as starting point
manager.clone_template(
    source_name="ncnr.refl.unpolarized",
    target_name="my_custom_workflow"
)

print("Template saved to:")
print("  D:/.../.config/reductus/templates/my_custom_workflow.json")
print("Edit the JSON file to customize")
```

### Step 2: Edit Template (Optional)

The template is a JSON file. You can:
- Modify existing module parameters
- Add/remove modules in the pipeline
- Change wire connections

Example: Change detector binning
```json
{
    "module": "ncnr.refl.super_load",
    "id": "0",
    "config": {
        "detector_bin": 4  // Changed from default
    }
}
```

### Step 3: Use Custom Template

```python
from reductus import reduce

# Use your custom template
template = reduce.load_template("my_custom_workflow")

# Run as usual
result = template.run(files=["D:/data/sample.nxs"])
result.save("D:/output/")
```

---

## Use Case: Jupyter Notebook Integration

**Goal:** Analyze reduction results in Jupyter

### Setup

```bash
# Install Jupyter (if not already)
pip install jupyter notebook

# Start notebook
jupyter notebook
```

### In Jupyter Cell

```python
# Import Reductus
from reductus import reduce
import matplotlib.pyplot as plt
import numpy as np

# Load template
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Run reduction
result = template.run(files=["D:/data/sample.nxs"])

# Get data
data = result.get_data()

# Plot
plt.figure(figsize=(10, 6))
plt.semilogy(data[:, 0], data[:, 1])
plt.xlabel("Q (1/Å)")
plt.ylabel("Reflectivity")
plt.title("Reflectivity Curve")
plt.grid(True)
plt.show()

# Save
result.save("D:/notebook_output/")
```

---

## Use Case: Desktop Application

**Goal:** Run Reductus as native desktop app

### Launch

```bash
# Simple launch
reductus desktop

# With debug output
reductus desktop --debug

# On custom port
reductus desktop --port 9090
```

### Register File Associations (Windows)

```bash
# Enable double-click to open .json templates
reductus desktop --register-associations
```

Now you can:
- Double-click `.json` template files to open in Reductus
- Drag-and-drop files into the window
- Use native file dialogs

---

## Use Case: Automate with Scheduled Tasks

**Goal:** Automatically process data as it arrives

### Windows Task Scheduler

1. Create batch file `process_data.bat`:
```batch
@echo off
cd /d "C:\path\to\project"
call .venv\Scripts\activate.bat
python process_data.py
```

2. Create `process_data.py`:
```python
from reductus import reduce
from pathlib import Path
import shutil
from datetime import datetime

template = reduce.load_template("ncnr.refl.unpolarized.json")

# Watch incoming data directory
incoming = Path("D:/incoming_data")
processed = Path("D:/processed_data")

for filepath in incoming.glob("*.nxs"):
    print(f"[{datetime.now()}] Processing {filepath.name}")

    result = template.run(files=[str(filepath)])
    output = processed / filepath.stem
    output.mkdir(exist_ok=True)
    result.save(str(output))

    # Move original file to archive
    shutil.move(str(filepath), f"D:/archive/{filepath.name}")
```

3. Set up Task Scheduler:
   - Create Basic Task → Name: "Process SANS Data"
   - Trigger: Daily at 2:00 AM
   - Action: Start program → `C:\path\to\process_data.bat`

### Linux Cron

1. Create `process_data.py` (same as above)

2. Make executable:
```bash
chmod +x ~/scripts/process_data.py
```

3. Add to crontab:
```bash
crontab -e

# Add line:
0 2 * * * /home/user/venv/bin/python /home/user/scripts/process_data.py
```

---

## Use Case: Data Quality Check

**Goal:** Verify data before full reduction

```python
from reductus import reduce
from pathlib import Path

template = reduce.load_template("ncnr.refl.unpolarized.json")

# Check a few representative files
test_files = [
    "D:/data/sample_1.nxs",
    "D:/data/sample_50.nxs",
    "D:/data/sample_100.nxs"
]

for filepath in test_files:
    try:
        print(f"Testing {Path(filepath).name}...", end=" ")
        result = template.run(files=[filepath])
        data = result.get_data()

        # Basic sanity checks
        if len(data) < 10:
            print(f"⚠ WARNING: Very few data points ({len(data)})")
        elif any(d < 0 for d in data[:, 1]):  # Check for negative values
            print(f"⚠ WARNING: Negative reflectivity values found")
        else:
            print("✓ OK")

    except Exception as e:
        print(f"✗ FAILED: {e}")
```

---

## Use Case: Pipeline Integration

**Goal:** Integrate Reductus into a larger data pipeline

```python
"""
Example: QA pipeline
1. Receive raw data
2. Run Reductus reduction
3. Generate plots
4. Email summary report
"""

from reductus import reduce
from pathlib import Path
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def reduce_and_report(data_file, email_to):
    """Reduce data and email results"""

    template = reduce.load_template("ncnr.refl.unpolarized.json")

    # Reduce
    print(f"Reducing {data_file}...")
    result = template.run(files=[data_file])

    # Get results
    data = result.get_data()
    output_dir = f"D:/results/{Path(data_file).stem}"
    result.save(output_dir)

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "input_file": data_file,
        "output_directory": output_dir,
        "num_points": len(data),
        "q_range": [float(data[0, 0]), float(data[-1, 0])],
        "status": "SUCCESS"
    }

    # Send email
    send_report_email(report, email_to)

    return report

def send_report_email(report, email_to):
    """Send reduction report via email"""
    # ... email implementation ...
    pass

# Use it
if __name__ == "__main__":
    reduce_and_report(
        "D:/data/sample.nxs",
        "researcher@institution.org"
    )
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'reductus'"

**Solution:** Install and activate virtual environment
```bash
# Install
pip install "reductus[all]"

# Verify
python -c "from reductus import reduce; print('OK')"
```

---

### Problem: "FileNotFoundError: Template not found"

**Solution:** Check template name
```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()

# List available
templates = manager.list_templates()
for t in templates['built-in']:
    print(t['name'])
```

---

### Problem: Files not being found

**Solution:** Use absolute paths and check existence
```python
from pathlib import Path

filepath = Path("D:/data/sample.nxs")

if not filepath.exists():
    print(f"File not found: {filepath}")
else:
    print(f"File size: {filepath.stat().st_size} bytes")

    # Try reduction
    result = template.run(files=[str(filepath)])
```

---

### Problem: "Desktop mode requires pywebview"

**Solution:** Install desktop extra
```bash
pip install "reductus[desktop]"

# Or install pywebview separately
pip install pywebview
```

---

### Problem: Batch processing is slow

**Solutions:**
1. Use parallel processing (see batch example above)
2. Process fewer files at once
3. Use glob instead of pre-expanded list
4. Check available RAM and disk space

```python
import psutil

# Check system resources
mem = psutil.virtual_memory()
print(f"Available RAM: {mem.available / (1024**3):.1f} GB")

disk = psutil.disk_usage("D:/")
print(f"Available disk: {disk.free / (1024**3):.1f} GB")
```

---

### Problem: Files saved in wrong format

**Solution:** Check format parameter
```python
result = template.run(files=["sample.nxs"])

# Specify format when saving
result.save("D:/output/", fmt="column")  # Default

# Other formats depend on data type (check documentation)
```

---

## Performance Tips

### 1. Reuse Template Objects

**Slow (reloads template each time):**
```python
for file in files:
    template = reduce.load_template("template.json")
    result = template.run(files=[file])
```

**Fast (loads once):**
```python
template = reduce.load_template("template.json")
for file in files:
    result = template.run(files=[file])
```

---

### 2. Use Glob Patterns

**Slow (manual file listing):**
```python
import glob
files = glob.glob("D:/data/*.nxs")
result = template.run(files=files)
```

**Fast (let Reductus handle it):**
```python
result = template.run(files=["D:/data/*.nxs"])

# Or directory mode
result = template.run(data_dir="D:/data")
```

---

### 3. Parallel Processing

**Slow (sequential):**
```python
for file in files:
    result = template.run(files=[file])
    result.save(f"output/{file}/")
```

**Fast (parallel with 4 workers):**
```python
from concurrent.futures import ThreadPoolExecutor

def process_one(file):
    result = template.run(files=[file])
    result.save(f"output/{Path(file).stem}/")

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_one, files)
```

---

### 4. Batch CLI (Fastest for Many Files)

```bash
# Let Reductus optimize the process
reductus batch \
  --template template.json \
  --data-dir "D:/data" \
  --output "D:/results"
```

---

## Best Practices

### 1. Use Absolute Paths

```python
# Good: Absolute path
result = template.run(files=["D:/data/sample.nxs"])

# Problematic: Relative path
result = template.run(files=["data/sample.nxs"])
```

---

### 2. Create Output Directories

```python
from pathlib import Path

output = Path("D:/results")
output.mkdir(parents=True, exist_ok=True)
result.save(str(output))
```

---

### 3. Add Error Handling

```python
try:
    result = template.run(files=[filepath])
    result.save(output_dir)
    print(f"✓ {filepath}")
except FileNotFoundError as e:
    print(f"✗ File not found: {e}")
except ValueError as e:
    print(f"✗ Reduction failed: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
```

---

### 4. Log Progress

```python
import logging
from datetime import datetime

logging.basicConfig(
    filename="reduction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info(f"Starting reduction of {filepath}")
result = template.run(files=[filepath])
logger.info(f"Reduction complete, saving to {output_dir}")
result.save(output_dir)
logger.info(f"Done")
```

---

### 5. Verify Results

```python
# Check that output files were created
import os

result.save(output_dir)

output_files = os.listdir(output_dir)
if output_files:
    print(f"✓ Created {len(output_files)} files")
    for f in output_files:
        size = os.path.getsize(os.path.join(output_dir, f))
        print(f"  - {f}: {size} bytes")
else:
    print("✗ No output files created!")
```

---

## Advanced: Custom Module Parameters

If your template contains modules with configurable parameters, you can override them:

```python
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Override any module field
result = template.run(
    files=["sample.nxs"],
    # Common overrides:
    detector_bin=4,           # Detector binning
    background_q_range=[0.05, 0.1],  # Q-range for background
    slit_height=0.2,          # Slit opening (mm)
    normalization="monitor"   # Normalization method
)

result.save("D:/output/")
```

Check your template's module documentation for available parameters.

---

## Getting Help

### Documentation

- **IMPLEMENTATION.md** — Overview of Phases 2-5 features
- **API_REFERENCE.md** — Detailed API documentation
- **USER_GUIDE.md** — This file

### Common Resources

```python
# List available templates
from reductus.template_manager import get_template_manager
manager = get_template_manager()
for t in manager.list_templates()['built-in']:
    print(f"{t['name']}: {t['description']}")

# View template details
template_def = manager.load_template("ncnr.refl.unpolarized")
print(template_def['description'])
print(template_def['modules'])  # See available modules

# Check installed version
import reductus
print(reductus.__version__)
```

### Asking for Help

When reporting issues, include:
1. Python version: `python --version`
2. Reductus version: `pip show reductus`
3. Operating system
4. Full error traceback
5. Minimal reproducing script

