import logging
import sys
from typing import Any


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with the specified name"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_error(
    logger: logging.Logger, error: Exception, context: dict[str, Any] | None = None
) -> None:
    """Log an error with context information"""
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
    }
    logger.error(f"Error occurred: {error_details}", exc_info=True)


# Create main application logger
logger = setup_logger("jira_agent")
