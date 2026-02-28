"""
Example: Using Reductus with Structured Logging

This example demonstrates how to configure and use Reductus logging
for debugging and monitoring reduction workflows.
"""

import logging
from reductus.logging_config import setup_logging, get_reduce_logger
from reductus import reduce
from pathlib import Path

# Setup 1: Simple console logging at DEBUG level
print("Example 1: Basic logging setup")
setup_logging(level=logging.DEBUG)

logger = get_reduce_logger()
logger.info("Reductus logging configured")

# Setup 2: Also log to file
print("\nExample 2: Console + file logging")
log_file = Path("reductus_reduction.log")
setup_logging(
    level=logging.DEBUG,
    log_file=str(log_file),
    include_file_handler=True
)

# Now run a reduction - all operations will be logged
print("\nRunning reduction with logging enabled...")
try:
    template = reduce.load_template("ncnr.refl.unpolarized.json")
    logger.info("Loaded template successfully")

    # This would log all operations
    # result = template.run(files=["D:/data/*.nxs"])
    # result.save("output/")

except FileNotFoundError:
    logger.warning("Template file not found (expected in example)")

# Setup 3: Customize logging by component
print("\nExample 3: Component-specific logging")
setup_logging(level=logging.INFO)

# Get component-specific loggers
reduce_logger = get_reduce_logger()
reduce_logger.setLevel(logging.DEBUG)  # Extra verbose for reduce

# This demonstrates different log levels:
# DEBUG: _path_to_fileinfo converting path
# INFO: Loading template, running reduction, saving results
# WARNING: Missing files, unusual conditions
# ERROR: Failures and exceptions

print("\n=== Logging Setup Examples ===")
print(f"1. Simple console logging")
print(f"2. Console + file logging (logs to: {log_file})")
print(f"3. Component-specific configuration")
print(f"\nFor production, use setup_logging() at app startup")
