# Reductus Structured Logging Guide

**Complete guide to logging in Reductus Phases 2-5**

---

## Overview

Reductus now includes **structured logging** throughout all Phase 2-5 modules for:

- 📊 **Debugging** — Track operation flow and identify issues
- 📈 **Monitoring** — Track reduction performance and success rates
- 🔍 **Troubleshooting** — Understand what went wrong
- 📝 **Auditing** — Track who did what and when

---

## Quick Start

### Basic Setup

```python
from reductus.logging_config import setup_logging
import logging

# Configure logging at app startup
setup_logging(level=logging.INFO)

# Now all Reductus operations log automatically
from reductus import reduce

template = reduce.load_template("template.json")
result = template.run(files=["data.nxs"])
# Logs appear on console automatically
```

### With File Logging

```python
from reductus.logging_config import setup_logging
import logging

setup_logging(
    level=logging.DEBUG,
    log_file="reductus.log",
    include_file_handler=True
)
```

### Example Output

```
2024-02-28 14:32:15,847 - reductus.reduce - INFO - Running template reduction
2024-02-28 14:32:15,847 - reductus.reduce - INFO - Initializing Reductus reduction API
2024-02-28 14:32:15,862 - reductus.reduce - DEBUG - Loading template from: ncnr.refl.unpolarized.json
2024-02-28 14:32:15,873 - reductus.templates - INFO - Successfully loaded template: ncnr.refl.unpolarized
2024-02-28 14:32:15,875 - reductus.reduce - INFO - Running template reduction
2024-02-28 14:32:15,885 - reductus.reduce - INFO - Loaded 1 files for reduction
2024-02-28 14:32:16,124 - reductus.reduce - INFO - Template execution complete
2024-02-28 14:32:16,142 - reductus.reduce - INFO - Saving reduction results
2024-02-28 14:32:16,155 - reductus.reduce - INFO - Successfully saved 1 files to output/
```

---

## Architecture

### Logging Module

**File:** `reductus/logging_config.py`

```python
from reductus.logging_config import setup_logging, get_logger, get_reduce_logger
```

**Functions:**

| Function | Purpose |
|----------|---------|
| `setup_logging(level, log_file, include_file_handler)` | Configure root logger |
| `get_logger(name)` | Get logger by module name |
| `get_reduce_logger()` | Get reduce module logger |
| `get_template_logger()` | Get template manager logger |
| `get_browser_logger()` | Get browser/favorites logger |

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Internal operations, variable values | "Path normalized to: D:/data/file.nxs" |
| **INFO** | Key operations, completion status | "Template execution complete" |
| **WARNING** | Potential issues, non-fatal errors | "File not found: missing.nxs" |
| **ERROR** | Failures and exceptions | "Failed to save template: permission denied" |

---

## What Gets Logged

### Phase 2: Python Scripting API (`reductus/reduce.py`)

**Initialization:**
```
INFO: Initializing Reductus reduction API
DEBUG: Loaded configuration with instruments: ['refl', 'sans']
INFO: Reductus API initialized successfully
```

**File Handling:**
```
DEBUG: Converting path to fileinfo: D:/data/*.nxs
DEBUG: Glob pattern matched 5 files
DEBUG: Could not stat file: /missing/file.nxs
INFO: Converted 5 files from pattern: D:/data/*.nxs
```

**Template Execution:**
```
INFO: Running template reduction
  template_name: ncnr.refl.unpolarized
  has_files: true
  node: None
  terminal: output
DEBUG: Processing 2 file patterns
INFO: Loaded 10 files for reduction
DEBUG: Found 1 loader nodes
INFO: Executing through node 5 terminal 'output'
INFO: Template execution complete
  datatype: refldata
  output_size: 12345
```

**Saving Results:**
```
INFO: Saving reduction results
  output_dir: D:/output
  format: column
DEBUG: Created output directory: D:/output
INFO: Exporting 3 values
INFO: Successfully saved 3 files to D:/output
```

### Phase 4: Template Management (`reductus/template_manager.py`)

**Listing:**
```
INFO: Listing templates
  category: all
DEBUG: Found 15 built-in templates
DEBUG: Found 3 custom templates
INFO: Listed 18 templates
```

**Saving:**
```
INFO: Saving template
  template_name: My Custom Template
  custom_name: my_template
DEBUG: Using template name as filename: My_Custom_Template
INFO: Template saved successfully
  path: ~/.config/reductus/templates/my_template.json
  size_bytes: 1524
```

**Cloning:**
```
INFO: Cloning template
  source: ncnr.refl.unpolarized
  target: my_custom_refl
DEBUG: Loading source template: ncnr.refl.unpolarized
INFO: Template cloned successfully
  source: ncnr.refl.unpolarized
  target: my_custom_refl
```

### Phase 5: File Browser & Favorites (`reductus/favorites.py`)

**Favorites:**
```
INFO: Adding favorite directory
  path: D:/SANS Data
  name: SANS Data
DEBUG: Normalized path: D:/SANS Data
INFO: Favorite added successfully
  name: SANS Data
  path: D:/SANS Data
  total_favorites: 3
```

**Export History:**
```
INFO: Recording export location
  path: D:/results/2024-02-28
DEBUG: Normalized export path: D:/results/2024-02-28
INFO: Export location recorded successfully
  path: D:/results/2024-02-28
  total_locations: 5
```

### REST API Endpoints

**API Requests:**
```
INFO: API request: list templates
  category: all
DEBUG: Returning 18 templates

INFO: API request: add favorite
  path: D:/data
  name: My Data
DEBUG: Favorite added, returning 4 total favorites

INFO: API request: list favorites
DEBUG: Returning 4 favorites
```

---

## Using Logs for Debugging

### Find Failures

```bash
# Show only errors
grep ERROR reductus.log

# Show errors with context
grep -A 5 ERROR reductus.log
```

### Track Performance

```bash
# Find slow operations
grep "execution complete" reductus.log

# Find file conversion times
grep "Converted.*files" reductus.log
```

### Debug Configuration

```bash
# Check what was loaded
grep "configuration with instruments" reductus.log

# Check data source detection
grep "Initializing Reductus" reductus.log
```

---

## Best Practices

### 1. **Always Enable Logging**

```python
# At application startup
from reductus.logging_config import setup_logging
import logging

setup_logging(level=logging.INFO)  # At least INFO level

# In production, add file logging
setup_logging(
    level=logging.INFO,
    log_file="/var/log/reductus.log",
    include_file_handler=True
)
```

### 2. **Use Appropriate Log Levels**

```python
logger.debug("Internal details")      # Only for diagnostics
logger.info("Key operations")         # Normal flow
logger.warning("Unusual conditions")  # Worth investigating
logger.error("Failures")              # Always bad
```

### 3. **Include Context in Logs**

```python
# Good: Structured context
logger.info("Template executed", extra={
    "template_name": "my_template",
    "num_files": 10,
    "duration_sec": 3.5
})

# Bad: Unstructured
logger.info(f"Template {name} executed with {files} files")
```

### 4. **Use Logger for Components**

```python
# Get component-specific logger
from reductus.logging_config import get_reduce_logger

logger = get_reduce_logger()
logger.info("Operation started")
```

---

## Configuration Examples

### Development Setup

```python
import logging
from reductus.logging_config import setup_logging, get_reduce_logger

# Detailed console logging
setup_logging(level=logging.DEBUG)

# Extra verbose for debugging reduce operations
reduce_logger = get_reduce_logger()
reduce_logger.setLevel(logging.DEBUG)
```

### Production Setup

```python
import logging
from reductus.logging_config import setup_logging

# Log INFO and above to file, ERROR and above to console
setup_logging(
    level=logging.INFO,
    log_file="/var/log/reductus/app.log",
    include_file_handler=True
)
```

### Testing Setup

```python
import logging
from reductus.logging_config import setup_logging

# Minimal logging to avoid test output clutter
setup_logging(level=logging.WARNING)

# But enable logging for specific failures
# Set to INFO to debug test failures
```

---

## Common Scenarios

### Scenario: "Reduction failed silently"

Look for ERROR logs:
```bash
grep ERROR reductus.log

# Output might show:
# ERROR - Failed to save template: permission denied
# ERROR - Template execution failed: invalid module configuration
```

---

### Scenario: "Why is my reduction slow?"

Check for timing information:
```bash
grep "execution complete" reductus.log
# Check timestamps to measure duration

grep "Loaded.*files" reductus.log
# See how many files were processed

grep "conversion" reductus.log
# Check file discovery time
```

---

### Scenario: "Which template was used?"

Search logs for template loading:
```bash
grep "Successfully loaded template" reductus.log

# Output shows:
# Successfully loaded template: ncnr.refl.unpolarized
```

---

### Scenario: "Debugging file browser issues"

Check browser/favorites logs:
```bash
grep "reductus.browser" reductus.log
# Shows all browser operations

grep "favorite" reductus.log
# Shows all favorites operations
```

---

## Advanced: Custom Logging

### Log to Multiple Files

```python
import logging
from logging.handlers import RotatingFileHandler
from reductus.logging_config import get_logger

logger = get_logger("reductus.reduce")

# Add custom file handler
handler = RotatingFileHandler(
    "reduction.log",
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)
```

### Structured JSON Logging

```python
import json
import logging
from reductus.logging_config import get_logger

logger = get_logger(__name__)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": record.created,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

---

## Troubleshooting Logging

### Problem: "No log output"

**Check:**
1. Did you call `setup_logging()`?
2. Is log level too high? (Try `logging.DEBUG`)
3. Check console for errors

**Solution:**
```python
from reductus.logging_config import setup_logging
import logging

setup_logging(level=logging.DEBUG)  # Explicitly set level
```

---

### Problem: "Log file not created"

**Check:**
1. Do you have write permissions?
2. Does the directory exist?
3. Is `include_file_handler=True`?

**Solution:**
```python
from pathlib import Path
from reductus.logging_config import setup_logging
import logging

log_dir = Path.home() / ".reductus" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

setup_logging(
    level=logging.INFO,
    log_file=str(log_dir / "app.log"),
    include_file_handler=True
)
```

---

### Problem: "Log file growing too large"

**Solution:** The built-in RotatingFileHandler limits logs to 10 MB per file with 5 backups:
- `app.log` — Current
- `app.log.1` — Previous
- `app.log.2` — Even older
- etc. (max 5 files)

---

## Summary

✅ **Comprehensive logging** added to all Phase 2-5 modules
✅ **Structured context** in log messages (extra dicts)
✅ **Configurable** for development, testing, and production
✅ **File rotation** support for production logs
✅ **Component-specific** loggers for fine-grained control
✅ **DEBUG, INFO, WARNING, ERROR** levels for filtering

**Start using it:**
```python
from reductus.logging_config import setup_logging
import logging

setup_logging(level=logging.INFO)
# All Reductus operations now logged!
```

