# Getting Started with Reductus Phases 2-5

Complete guide to get up and running with the new features.

---

## Installation (2 minutes)

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)
- Disk space: ~100 MB

### Step 1: Install Reductus

```bash
# Install with all features (recommended)
pip install "reductus[all]"

# Or minimal installation
pip install reductus
```

### Step 2: Verify Installation

```bash
# Check version
python -c "from reductus import reduce; print('✓ Installation successful')"
```

### Step 3: Choose Your Workflow

Three ways to use Reductus:
1. **Web Browser** — Traditional web interface (Phase 1)
2. **Python API** — Direct Python scripting (Phase 2)
3. **Desktop App** — Native application (Phase 3)
4. **Command Line** — Batch processing (Phase 2)

---

## Your First Reduction (10 minutes)

### Method 1: Web Browser (Easiest)

**If you already use Reductus:**

```bash
# Start server
reductus

# Open http://localhost:8002 in your browser
# Use the web interface as before
```

**What's new in the browser:**
- Template save/load UI
- File favorites sidebar
- Export history
- Better file browser

---

### Method 2: Python Script (Fastest)

**If you want to automate reductions:**

1. **Create a Python script** (`reduce_my_data.py`):

```python
from reductus import reduce

# Step 1: Load the template
print("Loading template...")
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Step 2: Run reduction on your data file
print("Running reduction...")
result = template.run(files=["D:/my_data/sample.nxs"])

# Step 3: Save results
print("Saving results...")
result.save("D:/my_results/")

print("✓ Done! Results saved to D:/my_results/")
```

2. **Run the script:**

```bash
python reduce_my_data.py
```

3. **Check results:**

```bash
ls D:/my_results/
```

---

### Method 3: Command Line (Best for Many Files)

**If you have 10+ files to process:**

```bash
# Process all files in a directory
reductus batch \
  --template ncnr.refl.unpolarized.json \
  --data-dir "D:/my_data" \
  --output "D:/my_results"
```

---

### Method 4: Desktop App (Most Native)

**If you want a native application:**

```bash
# Launch desktop app
reductus desktop

# Or with debug output
reductus desktop --debug
```

**Features:**
- Native window (not browser)
- Native file dialogs
- Drag-and-drop support
- System integration

---

## Next Steps (Based on Your Needs)

### I want to reduce one file quickly
→ **Method 2 (Python Script)** above

### I have many files to process
→ **Command line** or **Python with loop**

See: USER_GUIDE.md → "Batch Processing"

### I want to customize the reduction
→ **Clone and edit template**

```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()
manager.clone_template(
    source_name="ncnr.refl.unpolarized",
    target_name="my_custom"
)
# Now edit: ~/.config/reductus/templates/my_custom.json
```

See: USER_GUIDE.md → "Custom Data Reduction"

### I want to integrate with Python notebooks
→ **Jupyter integration**

```python
# In a Jupyter cell
from reductus import reduce
import matplotlib.pyplot as plt

template = reduce.load_template("ncnr.refl.unpolarized.json")
result = template.run(files=["sample.nxs"])
data = result.get_data()

plt.semilogy(data[:, 0], data[:, 1])
plt.show()
```

See: USER_GUIDE.md → "Jupyter Notebook Integration"

### I want to automate processing
→ **Scheduled tasks**

See: USER_GUIDE.md → "Automate with Scheduled Tasks"

### I want to integrate with another system
→ **REST API or Python library**

See: API_REFERENCE.md → "REST API Endpoints"

---

## Find Your Answer

### Common Questions

**Q: How do I find available templates?**

```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()
templates = manager.list_templates(category="built-in")

for t in templates['built-in']:
    print(f"{t['name']}: {t['description']}")
```

**Q: How do I change template parameters?**

```python
result = template.run(
    files=["sample.nxs"],
    detector_bin=4,  # Override detector binning
    background_q_range=[0.05, 0.1]  # Custom background range
)
```

**Q: How do I save custom templates?**

See: USER_GUIDE.md → "Custom Data Reduction"

**Q: How do I process files in parallel?**

See: USER_GUIDE.md → "Batch Processing" → Python Script section

**Q: How do I troubleshoot errors?**

See: USER_GUIDE.md → "Troubleshooting"

---

## Documentation Map

```
You need...                    Read this...                      Section
─────────────────────────────────────────────────────────────────────────
Installation help              GETTING_STARTED.md                (This file)
Quick examples                 API_REFERENCE.md                  Examples
How to run reductions          USER_GUIDE.md                     Quick Start
Batch processing               USER_GUIDE.md                     Batch Processing
Custom templates               USER_GUIDE.md                     Custom Reduction
Jupyter notebooks              USER_GUIDE.md                     Notebook Integration
Scheduled processing           USER_GUIDE.md                     Automation
Troubleshooting                USER_GUIDE.md                     Troubleshooting
Python API details             API_REFERENCE.md                  Modules
REST API details               API_REFERENCE.md                  REST API Endpoints
Architecture overview          IMPLEMENTATION.md                 Architecture
All features explained         IMPLEMENTATION.md                 Phases 2-5
Performance tips               USER_GUIDE.md                     Performance Tips
Best practices                 USER_GUIDE.md                     Best Practices
```

---

## Quick Reference

### Start Here

**Just installed? Run this:**

```bash
# Verify it works
python -c "from reductus import reduce; print('✓ Ready')"

# List available templates
python -c "from reductus.template_manager import get_template_manager; \
          m = get_template_manager(); \
          [print(t['name']) for t in m.list_templates()['built-in']]"

# Run your first reduction
python -c "from reductus import reduce; \
          t = reduce.load_template('ncnr.refl.unpolarized.json'); \
          r = t.run(files=['yourfile.nxs']); \
          r.save('output/')"
```

---

### Common Commands

```bash
# Start web GUI
reductus

# Start desktop app
reductus desktop

# Run batch processing
reductus batch --template template.json --data-dir data/ --output results/

# Manage file associations (Windows)
reductus desktop --register-associations

# Check version
pip show reductus
```

---

### Python Quick Start

```python
# Load and run reduction
from reductus import reduce

template = reduce.load_template("template.json")
result = template.run(files=["file.nxs"])
result.save("output/")

# Manage templates
from reductus.template_manager import get_template_manager
m = get_template_manager()
m.clone_template("source", "target")
m.list_templates()

# Manage favorites
from reductus.favorites import get_favorites_manager
fav = get_favorites_manager()
fav.add_favorite("D:/data", name="My Data")
fav.list_favorites()

# Track exports
from reductus.favorites import get_export_history_manager
exp = get_export_history_manager()
exp.add_export_location("D:/results")
exp.get_recent_exports()
```

---

## Troubleshooting Installation

### Problem: "ModuleNotFoundError: No module named 'reductus'"

**Solution:**
```bash
# Verify installation
pip show reductus

# If not installed, install now
pip install "reductus[all]"

# Verify again
python -c "import reductus; print(reductus.__version__)"
```

---

### Problem: "No module named 'pywebview' (for desktop)"

**Solution:**
```bash
# Install optional dependency
pip install "reductus[desktop]"

# Or install pywebview directly
pip install pywebview
```

---

### Problem: Template not found

**Solution:**
```python
from reductus.template_manager import get_template_manager

# List what's available
m = get_template_manager()
for t in m.list_templates()['built-in']:
    print(t['name'])
```

---

### Problem: "File not found" error

**Solution:**
```python
from pathlib import Path

# Check file exists
filepath = Path("D:/data/sample.nxs")
if filepath.exists():
    print(f"✓ File found: {filepath}")
else:
    print(f"✗ File not found: {filepath}")

# Use absolute path
result = template.run(files=[str(filepath.absolute())])
```

---

## What's New in Phases 2-5?

### Phase 2: Python Scripting API
**Run reductions without web browser or server**

```python
from reductus import reduce
template = reduce.load_template("template.json")
result = template.run(files=["data.nxs"])
result.save("output/")
```

### Phase 3a: Desktop App Wrapper
**Run Reductus as native application**

```bash
reductus desktop
```

### Phase 3b: Desktop-Native File Interactions
**File dialogs and associations**

```bash
reductus desktop --register-associations
# Now: Double-click .json files to open in Reductus
```

### Phase 4: Template Management
**Save and manage reduction templates**

```python
from reductus.template_manager import get_template_manager
m = get_template_manager()
m.save_template(template_def, name="my_template")
m.clone_template("source", "target")
m.list_templates()
```

### Phase 5: File Browser & Export UX
**Favorites and export history**

```python
from reductus.favorites import get_favorites_manager, get_export_history_manager

# Pin directories
fav = get_favorites_manager()
fav.add_favorite("D:/data", name="My Data")

# Track exports
exp = get_export_history_manager()
exp.add_export_location("D:/results")
exp.get_recent_exports()
```

---

## Support & Help

### Documentation

📖 **GETTING_STARTED.md** (this file)
- Installation
- First reduction
- Troubleshooting

📖 **USER_GUIDE.md**
- 7 real-world use cases
- Step-by-step guides
- Performance tips
- Best practices

📖 **API_REFERENCE.md**
- Complete API documentation
- All functions and classes
- 7 working examples

📖 **IMPLEMENTATION.md**
- Architecture details
- How features work
- Design decisions

### Getting Help

1. **Read appropriate documentation** (see map above)
2. **Check USER_GUIDE.md Troubleshooting** for common issues
3. **Review examples** in API_REFERENCE.md
4. **Check test files** for working code:
   - `tests/test_reduce.py`
   - `tests/test_desktop.py`
   - `tests/test_template_manager.py`
   - `tests/test_browser_ux.py`

### Reporting Issues

Include:
- Python version: `python --version`
- Reductus version: `pip show reductus`
- Operating system
- Full error traceback
- Minimal reproducing script

---

## Tips for Success

✅ **Read the right documentation**
- Beginners: USER_GUIDE.md
- Developers: API_REFERENCE.md
- Architects: IMPLEMENTATION.md

✅ **Use absolute paths**
```python
# Good
result = template.run(files=["D:/data/sample.nxs"])

# Avoid relative paths
result = template.run(files=["data/sample.nxs"])
```

✅ **Reuse template objects**
```python
# Good: Load once
template = reduce.load_template("template.json")
for file in files:
    result = template.run(files=[file])

# Avoid: Reload each time
for file in files:
    template = reduce.load_template("template.json")
    result = template.run(files=[file])
```

✅ **Use glob patterns**
```python
# Good: Let Reductus handle globbing
result = template.run(files=["D:/data/*.nxs"])

# Works but less efficient
import glob
files = glob.glob("D:/data/*.nxs")
result = template.run(files=files)
```

✅ **Add error handling**
```python
try:
    result = template.run(files=[filepath])
    result.save(output_dir)
    print(f"✓ Success")
except FileNotFoundError:
    print(f"✗ File not found")
except Exception as e:
    print(f"✗ Error: {e}")
```

✅ **Test with a small dataset first**
```python
# Test with one file before processing many
result = template.run(files=["first_file.nxs"])
data = result.get_data()
print(f"Output has {len(data)} points")
```

---

## Next Steps After Installation

### Immediate (< 5 minutes)
1. ✓ Install Reductus
2. ✓ Run first reduction
3. ✓ Check results

### Short-term (Today)
1. Choose workflow (Web, Python, CLI, Desktop)
2. Read appropriate USER_GUIDE.md section
3. Try with your actual data
4. Customize template if needed

### Medium-term (This Week)
1. Automate your reduction workflow
2. Set up scheduled processing
3. Integrate with your analysis pipeline
4. Create custom templates

### Long-term (This Month)
1. Optimize for performance
2. Integrate with larger systems
3. Share workflows with colleagues
4. Document your custom templates

---

## Key Resources

| Resource | Purpose | Time |
|----------|---------|------|
| GETTING_STARTED.md | This guide | 10 min |
| USER_GUIDE.md | How-to guide | 30 min |
| API_REFERENCE.md | API documentation | 1 hour |
| IMPLEMENTATION.md | Architecture | 1 hour |
| test_*.py files | Working examples | Reference |

---

## What's Next?

**You're ready to:**
- ✅ Process your data with Reductus
- ✅ Create custom reduction workflows
- ✅ Automate batch processing
- ✅ Integrate with Python notebooks
- ✅ Run as desktop application

**Learn more in:**
- USER_GUIDE.md for practical examples
- API_REFERENCE.md for API details
- IMPLEMENTATION.md for architecture

**Questions?**
→ Check the appropriate documentation section above

---

**Happy reducing! 🎉**

