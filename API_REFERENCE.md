# Reductus Python API Reference

Complete API documentation for Phases 2-5.

---

## Table of Contents

1. [Module: `reductus.reduce`](#module-reductusreduce) — Python scripting API
2. [Module: `reductus.template_manager`](#module-reductustemplate_manager) — Template management
3. [Module: `reductus.favorites`](#module-reductus-favorites) — File browser UX
4. [Module: `reductus.desktop`](#module-reductusdesktop) — Desktop app wrapper
5. [REST API Endpoints](#rest-api-endpoints) — Web service APIs
6. [Data Structures](#data-structures) — Common types
7. [Examples](#examples) — Usage patterns

---

## Module: `reductus.reduce`

**Direct Python interface for running data reductions.**

### Functions

#### `load_template(name: str) -> Template`

Load a template from file or template library.

**Parameters:**
- `name` (str): Path to JSON file, or template name
  - Full path: `"D:/templates/my_template.json"`
  - Relative to built-in: `"ncnr.refl.unpolarized.json"`
  - By name: `"ncnr.refl.unpolarized"`

**Returns:** `Template` object

**Raises:**
- `FileNotFoundError` — If template file not found

**Example:**
```python
from reductus import reduce

# By full path
t1 = reduce.load_template("D:/my_templates/custom.json")

# By built-in name
t2 = reduce.load_template("ncnr.refl.unpolarized")

# By filename
t3 = reduce.load_template("ncnr.refl.unpolarized.json")
```

---

#### `run(template: Union[Template, str], files: List[str] = None, ...) -> ReductionResult`

Execute a template (shortcut function).

**Parameters:**
- `template` (Template|str): Template object or path to load
- `files` (List[str], optional): File paths or glob patterns
- `data_dir` (str, optional): Directory to glob for all files
- `node` (int, optional): Execute through specific node (default: last)
- `terminal` (str, optional): Terminal name (default: "output")
- `**field_overrides`: Override module field values

**Returns:** `ReductionResult`

**Example:**
```python
result = reduce.run(
    "ncnr.refl.unpolarized.json",
    files=["D:/data/*.nxs"]
)
```

---

### Class: `Template`

**Represents a loaded reduction template.**

#### Constructor

```python
Template(template_def: dict)
```

**Parameters:**
- `template_def` (dict): Template definition from JSON

#### Class Methods

##### `Template.load(path: str) -> Template`

Load template from JSON file.

**Parameters:**
- `path` (str): File path to template JSON

**Returns:** `Template`

**Example:**
```python
template = Template.load("D:/templates/my.json")
```

---

##### `Template.from_dict(d: dict) -> Template`

Create template from dictionary.

**Parameters:**
- `d` (dict): Template definition

**Returns:** `Template`

**Example:**
```python
template_data = {
    "name": "My Template",
    "modules": [...],
    "wires": [...]
}
template = Template.from_dict(template_data)
```

---

#### Instance Methods

##### `run(files=None, data_dir=None, glob_pattern=None, node=None, terminal="output", **field_overrides) -> ReductionResult`

Execute the template on files.

**Parameters:**
- `files` (List[str], optional): List of file paths or glob patterns
  - Examples: `["file1.nxs", "file2.nxs"]`
  - With globs: `["D:/data/*.nxs", "D:/backup/**/*.nxs"]`
- `data_dir` (str, optional): Directory to glob all files from
  - Example: `"D:/SANS Data"`
- `glob_pattern` (str, optional): Custom glob pattern (default: `**/*`)
- `node` (int, optional): Execute through node N (default: last node)
  - Useful for debugging intermediate results
- `terminal` (str, optional): Output terminal name (default: `"output"`)
- `**field_overrides`: Override any module field
  - Example: `detector_bin=4` to override detector binning

**Returns:** `ReductionResult`

**Raises:**
- `ValueError` — Invalid files or configuration
- `RuntimeError` — Reduction failed

**Example:**
```python
# Simple execution
result = template.run(files=["sample.nxs"])

# With directory glob
result = template.run(data_dir="D:/SANS Data")

# With glob pattern
result = template.run(files=["D:/data/*.nxs"])

# Override field
result = template.run(
    files=["sample.nxs"],
    detector_bin=4,  # Override detector binning
    x_range=[0, 10]  # Override x-axis range
)

# Execute through node 3 (for debugging)
result = template.run(
    files=["sample.nxs"],
    node=3
)
```

---

#### Properties

##### `template_def`

The raw template definition dictionary.

**Type:** `dict`

**Example:**
```python
template = Template.load("my.json")
print(template.template_def['name'])  # Template name
print(template.template_def['modules'])  # Module list
```

---

### Class: `ReductionResult`

**Represents the output of a reduction.**

#### Instance Methods

##### `save(output_dir: str, fmt: str = "column") -> None`

Write reduction results to disk.

**Parameters:**
- `output_dir` (str): Directory to save files
  - Created if doesn't exist
- `fmt` (str): Export format
  - `"column"` — Columnar text format (default)
  - Other formats depend on datatype

**Returns:** None

**Raises:**
- `OSError` — If output directory cannot be created or written

**Example:**
```python
result = template.run(files=["sample.nxs"])
result.save("D:/output/")

# Creates files like: D:/output/sample.column
```

---

##### `get_data(node=None, terminal="output") -> List`

Get raw data values from result.

**Parameters:**
- `node` (int, optional): Get data from specific node (default: last)
- `terminal` (str, optional): Terminal name (default: "output")

**Returns:** `List` of values

**Example:**
```python
result = template.run(files=["sample.nxs"])

# Get final output
data = result.get_data()

# Get intermediate node
data = result.get_data(node=3)

# Get specific terminal
data = result.get_data(terminal="uncertainties")
```

---

##### `get_bundle(node=None, terminal="output") -> Bundle`

Get raw Bundle object from reduction.

**Parameters:**
- `node` (int, optional): Get bundle from specific node
- `terminal` (str, optional): Terminal name

**Returns:** `Bundle` object (internal dataflow representation)

**Example:**
```python
bundle = result.get_bundle()

# Access internal structure
print(bundle.datatype.id)  # Data type name
```

---

### Module-Level State

#### `_initialized`

Global flag indicating if environment is initialized.

**Type:** `bool`

---

#### `_ensure_initialized(instruments=None)`

Initialize reduction environment (idempotent).

**Parameters:**
- `instruments` (List[str], optional): Specific instruments to load
  - Default: Load all available

**Returns:** None

**Called automatically** by first `reduce.run()` call.

**Example:**
```python
# Force initialization with specific instruments
reduce._ensure_initialized(instruments=['refl'])
```

---

## Module: `reductus.template_manager`

**Template discovery, loading, and storage.**

### Functions

#### `get_template_manager() -> TemplateManager`

Get global TemplateManager instance (singleton).

**Returns:** `TemplateManager`

**Example:**
```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()
```

---

### Class: `TemplateManager`

**Manages template discovery and persistence.**

#### Constructor

```python
TemplateManager()
```

Automatically sets up directories in user data location.

#### Instance Methods

##### `list_templates(category: str = "all") -> Dict[str, List[Dict]]`

List available templates.

**Parameters:**
- `category` (str): Filter templates
  - `"all"` — Built-in and custom (default)
  - `"built-in"` — Only built-in templates
  - `"custom"` — Only user-saved templates

**Returns:** Dict with structure:
```python
{
    "built-in": [
        {
            "name": "Template Name",
            "description": "Description",
            "instrument": "ncnr.refl",
            "version": "1.0",
            "filename": "ncnr.refl.unpolarized.json",
            "path": "/absolute/path",
            "source": "built-in"
        },
        ...
    ],
    "custom": [...]
}
```

**Example:**
```python
manager = get_template_manager()

# All templates
all_templates = manager.list_templates()

# Just built-in
built_in = manager.list_templates(category="built-in")
for t in built_in['built-in']:
    print(f"{t['name']}: {t['description']}")

# Just custom
custom = manager.list_templates(category="custom")
```

---

##### `load_template(name: str, source: str = "all") -> Optional[Dict]`

Load a template by name or filename.

**Parameters:**
- `name` (str): Template name or filename (with or without `.json`)
- `source` (str): Where to search
  - `"all"` — Search both (default)
  - `"built-in"` — Only built-in
  - `"custom"` — Only custom

**Returns:** Template definition dict, or None if not found

**Example:**
```python
template = manager.load_template("ncnr.refl.unpolarized")
if template:
    print(f"Loaded: {template['name']}")
```

---

##### `save_template(template_def: Dict, name: Optional[str] = None) -> bool`

Save a template to user directory.

**Parameters:**
- `template_def` (dict): Template definition
  - Required fields: `name`, `modules`, `wires`
- `name` (str, optional): Custom filename (without `.json`)
  - Default: Use `template_def['name']`

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
template_def = {
    "name": "My Custom Template",
    "description": "Custom reduction workflow",
    "instrument": "ncnr.refl",
    "modules": [...],
    "wires": [...]
}

success = manager.save_template(template_def, name="my_custom")
if success:
    print("Template saved!")
```

---

##### `delete_template(name: str) -> bool`

Delete a user-saved template.

**Parameters:**
- `name` (str): Template name or filename

**Returns:** `True` if successful, `False` if not found

**Example:**
```python
success = manager.delete_template("my_custom")
if success:
    print("Template deleted")
```

---

##### `clone_template(source_name: str, target_name: str) -> bool`

Clone a built-in template to user directory.

**Parameters:**
- `source_name` (str): Name of template to clone
- `target_name` (str): Name for cloned template

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
# Create customizable copy of built-in
success = manager.clone_template(
    source_name="ncnr.refl.unpolarized",
    target_name="my_modified_refl"
)

if success:
    # Edit D:/.../my_modified_refl.json
    print("Edit your template and reload")
```

---

## Module: `reductus.favorites`

**File browser improvements: favorites and export history.**

### Functions

#### `get_favorites_manager() -> FavoritesManager`

Get global FavoritesManager instance.

**Returns:** `FavoritesManager`

---

#### `get_export_history_manager() -> ExportHistoryManager`

Get global ExportHistoryManager instance.

**Returns:** `ExportHistoryManager`

---

### Class: `FavoritesManager`

**Manage pinned directories.**

#### Instance Methods

##### `add_favorite(path: str, name: Optional[str] = None) -> bool`

Pin a directory.

**Parameters:**
- `path` (str): Directory path
- `name` (str, optional): Display name (default: directory name)

**Returns:** `True` if successful

**Example:**
```python
from reductus.favorites import get_favorites_manager

fav = get_favorites_manager()
fav.add_favorite("D:/SANS Data", name="SANS Data")
fav.add_favorite("D:/Backups/2024")
```

---

##### `remove_favorite(path: str) -> bool`

Unpin a directory.

**Parameters:**
- `path` (str): Directory path

**Returns:** `True` if found and removed, `False` if not found

---

##### `list_favorites() -> List[Dict]`

Get all pinned directories.

**Returns:** List of favorite dicts:
```python
[
    {
        "path": "D:/SANS Data",
        "name": "SANS Data",
        "timestamp": 1708065600
    },
    ...
]
```

---

##### `reorder_favorites(order: List[int]) -> bool`

Reorder pinned directories.

**Parameters:**
- `order` (List[int]): List of indices in new order
  - Example: `[2, 0, 1]` moves third to first

**Returns:** `True` if successful

**Example:**
```python
# Reverse order
favorites = fav.list_favorites()
new_order = list(range(len(favorites)-1, -1, -1))
fav.reorder_favorites(new_order)
```

---

### Class: `ExportHistoryManager`

**Track export/save locations.**

#### Instance Methods

##### `add_export_location(path: str) -> bool`

Record an export location.

**Parameters:**
- `path` (str): Directory path

**Returns:** `True` if successful

---

##### `get_recent_exports(limit: int = 10) -> List[Dict]`

Get recent save locations.

**Parameters:**
- `limit` (int): Maximum number to return (default: 10)

**Returns:** List of export dicts (most recent first):
```python
[
    {
        "path": "D:/results/2024-02-15",
        "timestamp": 1708065600
    },
    ...
]
```

---

##### `set_default_export_location(path: str) -> bool`

Set default save directory.

**Parameters:**
- `path` (str): Directory path

**Returns:** `True` if successful

---

##### `get_default_export_location() -> Optional[str]`

Get default save directory.

**Returns:** Path string, or None if not set

**Example:**
```python
from reductus.favorites import get_export_history_manager

export = get_export_history_manager()

# Track an export
export.add_export_location("D:/results/2024-02-15")

# Set default
export.set_default_export_location("D:/results")

# Get recent
recent = export.get_recent_exports(limit=5)
for loc in recent:
    print(f"Saved to: {loc['path']}")
```

---

## Module: `reductus.desktop`

**Desktop application wrapper.**

### Functions

#### `run_desktop(config=None, port: int = 8002, debug: bool = False) -> None`

Launch desktop application.

**Parameters:**
- `config` (dict, optional): Custom config dictionary
- `port` (int): Server port (default: 8002)
- `debug` (bool): Enable debug output (default: False)

**Returns:** None (blocks until window closed)

**Raises:**
- `ImportError` — If pywebview not installed

**Example:**
```python
from reductus.desktop import run_desktop

run_desktop(port=9090, debug=True)
```

---

#### `run_desktop_cli(args) -> None`

CLI entry point for desktop mode.

**Parameters:**
- `args`: argparse.Namespace with fields:
  - `config_file` (str|None): Path to config file
  - `port` (int): Server port
  - `debug` (bool): Debug mode
  - `register_associations` (bool): Register file associations

**Returns:** None

---

#### `set_webview_window(window) -> None`

Register webview window instance (internal).

Used by `/api/desktop/*` endpoints to access native dialogs.

---

## REST API Endpoints

### Template Management

**Base:** `/api/templates/`

#### GET `/list`

List templates.

**Query Parameters:**
- `category` (str): "all", "built-in", or "custom" (default: "all")

**Response:**
```json
{
  "built-in": [
    {
      "name": "Template Name",
      "description": "Description",
      "instrument": "ncnr.refl",
      "version": "1.0",
      "filename": "ncnr.refl.unpolarized.json",
      "path": "/path/to/template.json",
      "source": "built-in"
    }
  ],
  "custom": [...]
}
```

**Example:**
```bash
curl http://localhost:8002/api/templates/list?category=built-in
```

---

#### GET `/load`

Load a template.

**Query Parameters:**
- `name` (str): Template name or filename

**Response:**
```json
{
  "name": "Template Name",
  "modules": [...],
  "wires": [...],
  "instrument": "ncnr.refl"
}
```

---

#### POST `/save`

Save a template.

**Body:**
```json
{
  "template": {
    "name": "My Template",
    "modules": [...],
    "wires": [...]
  },
  "name": "optional_custom_filename"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Template saved"
}
```

---

#### POST `/delete`

Delete a template.

**Body:**
```json
{"name": "template_name"}
```

**Response:**
```json
{
  "success": true,
  "message": "Template deleted"
}
```

---

#### POST `/clone`

Clone a template.

**Body:**
```json
{
  "source": "source_template_name",
  "target": "new_template_name"
}
```

---

### File Browser & Export UX

**Base:** `/api/browser/` and `/api/export/`

#### GET `/browser/favorites/list`

List pinned directories.

**Response:**
```json
{
  "favorites": [
    {
      "path": "D:/SANS Data",
      "name": "SANS Data",
      "timestamp": 1708065600
    }
  ]
}
```

---

#### POST `/browser/favorites/add`

Pin a directory.

**Body:**
```json
{
  "path": "D:/SANS Data",
  "name": "SANS Data"
}
```

---

#### POST `/export/record`

Record an export location.

**Body:**
```json
{"path": "D:/results/2024-02-15"}
```

---

#### GET `/export/recent`

Get recent export locations.

**Query Parameters:**
- `limit` (int): Maximum entries (default: 10)

**Response:**
```json
{
  "locations": [
    {
      "path": "D:/results/2024-02-15",
      "timestamp": 1708065600
    }
  ]
}
```

---

#### GET `/browser/suggestions`

Get smart browsing suggestions (favorites + recent).

**Response:**
```json
{
  "favorites": [...],
  "recent_exports": [...],
  "default_export": "D:/results"
}
```

---

### Desktop

**Base:** `/api/desktop/`

#### POST `/open_folder`

Show folder picker dialog.

**Body:**
```json
{"title": "Select data directory"}
```

**Response:**
```json
{
  "path": "D:/selected/folder",
  "cancelled": false
}
```

---

#### POST `/save_file`

Show save-as dialog.

**Body:**
```json
{
  "title": "Save results",
  "file_types": [["Column files", "*.column"], ["All files", "*"]],
  "default_name": "output.column"
}
```

**Response:**
```json
{
  "path": "D:/selected/file.column",
  "cancelled": false
}
```

---

## Data Structures

### Fileinfo Dict

Used internally to represent files.

```python
{
    "source": "local",           # Data source name
    "path": "/abs/path/file.nxs", # Absolute filesystem path
    "mtime": 1708065600          # File modification time (Unix timestamp)
}
```

---

### Template Definition

JSON structure for templates.

```json
{
    "name": "Template Name",
    "description": "What this template does",
    "instrument": "ncnr.refl",
    "version": "1.0",
    "modules": [
        {
            "module": "ncnr.refl.load",
            "id": "0",
            "config": {
                "filelist": []
            }
        },
        {
            "module": "ncnr.refl.normalize",
            "id": "1",
            "config": {}
        }
    ],
    "wires": [
        {
            "source": "0",
            "target": "1",
            "source_terminal": "output",
            "target_terminal": "data"
        }
    ]
}
```

---

### Reduction Result Bundle

Internal structure returned by reduction.

```python
Bundle(
    datatype=DataType(...),      # Output data type
    values=[...],                 # Actual output data
    uncertainty=...               # Optional uncertainty
)
```

Access via:
```python
bundle = result.get_bundle()
bundle.datatype.id              # Type name
bundle.values                   # Data values
```

---

## Examples

### Example 1: Simple Batch Processing

```python
from reductus import reduce

# Load template once
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Process multiple files
for data_file in ["file1.nxs", "file2.nxs", "file3.nxs"]:
    result = template.run(files=[data_file])
    result.save(f"output/{data_file.stem}")
```

---

### Example 2: Custom Template Workflow

```python
from reductus.template_manager import get_template_manager
from reductus import reduce

manager = get_template_manager()

# Clone built-in for customization
manager.clone_template("ncnr.refl.unpolarized", "my_custom_refl")

# Edit the template file (it's JSON)
# D:/.../my_custom_refl.json

# Use the custom template
template = reduce.load_template("my_custom_refl")
result = template.run(files=["sample.nxs"])
result.save("output/")
```

---

### Example 3: Template with Field Overrides

```python
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Override template parameters
result = template.run(
    files=["sample.nxs"],
    # These depend on your template's modules
    detector_bin=4,           # Custom detector binning
    background_q_range=[0.05, 0.1],  # Background range
    slit_height=0.2           # Slit height mm
)

result.save("output/")
```

---

### Example 4: Jupyter Notebook Usage

```python
from reductus import reduce
from reductus.template_manager import get_template_manager
import matplotlib.pyplot as plt

# In a Jupyter notebook
template = reduce.load_template("ncnr.refl.unpolarized.json")

# Run reduction
result = template.run(files=["D:/data/sample.nxs"])

# Get data for plotting
data = result.get_data()

# Plot results (pseudo-code)
plt.plot(data.q, data.intensity)
plt.xlabel("Q")
plt.ylabel("Reflectivity")
plt.show()

# Save for later
result.save("D:/results/")
```

---

### Example 5: Managing Templates

```python
from reductus.template_manager import get_template_manager

manager = get_template_manager()

# Browse available templates
templates = manager.list_templates(category="all")

print("Built-in templates:")
for t in templates['built-in']:
    print(f"  - {t['name']}: {t['description']}")

print("Custom templates:")
for t in templates['custom']:
    print(f"  - {t['name']}")

# Clone and customize
manager.clone_template("ncnr.refl.unpolarized", "production_refl")

# Later, delete if no longer needed
manager.delete_template("production_refl")
```

---

### Example 6: File Favorites and History

```python
from reductus.favorites import get_favorites_manager, get_export_history_manager

fav = get_favorites_manager()
export = get_export_history_manager()

# Add frequently-used directories
fav.add_favorite("D:/SANS Data", name="SANS Data")
fav.add_favorite("D:/Backups/2024", name="Backups")

# List favorites
for f in fav.list_favorites():
    print(f"{f['name']}: {f['path']}")

# Track exports
export.add_export_location("D:/results/2024-02-15")
export.set_default_export_location("D:/results")

# Get recent saves
recent = export.get_recent_exports(limit=5)
for loc in recent:
    print(f"Previously saved to: {loc['path']}")

# Get default
default = export.get_default_export_location()
print(f"Default save: {default}")
```

---

### Example 7: CLI Batch Processing

```bash
#!/bin/bash

# Process all SANS files in a directory
reductus batch \
  --template ncnr.refl.unpolarized.json \
  --data-dir "/mnt/data/SANS_2024" \
  --output "/mnt/results/reduced_2024"

# Process specific files
reductus batch \
  --template my_custom.json \
  --files "/data/sample*.nxs" \
  --output "/results/"

# With custom settings
reductus batch \
  --template template.json \
  --files "/data/*.nxs" \
  --output "/results/" \
  --config-file myconfig.py
```

---

## Error Handling

### Common Errors

**ImportError: cannot import name 'reduce'**
```python
# Make sure you have the latest version
pip install --upgrade "reductus[all]"
```

**FileNotFoundError: Template not found**
```python
# Check available templates
from reductus.template_manager import get_template_manager
manager = get_template_manager()
for t in manager.list_templates()['built-in']:
    print(t['name'])
```

**RuntimeError: Reduction failed**
```python
# Check file paths exist
import os
for f in files:
    if not os.path.exists(f):
        print(f"Missing: {f}")
```

---

## Performance Tips

1. **Reuse Template objects** — Don't reload template for each file
   ```python
   template = reduce.load_template("template.json")  # Once
   for f in files:
       result = template.run(files=[f])  # Use same instance
   ```

2. **Use glob patterns** — Let Reductus find files
   ```python
   # Good: Reductus handles globbing
   result = template.run(files=["D:/data/*.nxs"])

   # Okay: But less efficient
   import glob
   files = glob.glob("D:/data/*.nxs")
   result = template.run(files=files)
   ```

3. **Process directories efficiently** — Glob entire directory once
   ```python
   # Good: Single pass
   result = template.run(data_dir="D:/SANS Data")

   # Less efficient: Requires expanded file list
   result = template.run(files=["D:/SANS Data/*.nxs"])
   ```

