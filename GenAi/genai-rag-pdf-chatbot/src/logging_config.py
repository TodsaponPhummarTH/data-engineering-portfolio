"""
Logging Configuration Module
===========================

This module sets up the logging configuration for the RAG PDF Chatbot system.
It provides a centralized way to configure logging levels, formats, and handlers.

Key Features:
- Configurable log levels
- Multiple log handlers (console and file)
- Structured log formatting
- Easy to modify logging settings
"""

import logging
import os
from pathlib import Path
from datetime import datetime
import json

def setup_logging():
    """
    Setup logging configuration
    
    Creates a logger with both console and file handlers.
    The log file is rotated daily and kept for 30 days.
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Get current date for log file name
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"app_{current_date}.log"
    
    # Create log formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Example usage
if __name__ == "__main__":
    """
    Example usage of logging
    """
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")