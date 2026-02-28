"""
Structured logging configuration for Reductus.

Provides standardized logging setup with:
- Structured log format with timestamps
- Different log levels for different components
- File and console handlers
- Contextual logging support
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


# Log format with timestamps and structured fields
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    include_file_handler: bool = False
) -> None:
    """
    Configure structured logging for Reductus.

    Args:
        level: Root logging level (default: INFO)
        log_file: Optional log file path
        include_file_handler: Whether to write logs to file

    Example:
        >>> setup_logging(level=logging.DEBUG)
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if include_file_handler and log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(DETAILED_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Operation started")
    """
    return logging.getLogger(name)


# Convenience loggers for common components
def get_api_logger() -> logging.Logger:
    """Get logger for API operations."""
    return logging.getLogger('reductus.api')


def get_reduce_logger() -> logging.Logger:
    """Get logger for reduction operations."""
    return logging.getLogger('reductus.reduce')


def get_template_logger() -> logging.Logger:
    """Get logger for template operations."""
    return logging.getLogger('reductus.templates')


def get_browser_logger() -> logging.Logger:
    """Get logger for file browser operations."""
    return logging.getLogger('reductus.browser')


def get_desktop_logger() -> logging.Logger:
    """Get logger for desktop app operations."""
    return logging.getLogger('reductus.desktop')
