"""
Logging utilities for DreamOS
"""
import os
import logging
import datetime
import glob
from pathlib import Path
from typing import Optional

# Default log levels
DEFAULT_CONSOLE_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG

# Colors for console output
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BOLD': '\033[1m'
}

# Log format with colors
CONSOLE_FORMAT = (
    f"{COLORS['BOLD']}%(asctime)s{COLORS['RESET']} | "
    f"{COLORS['MAGENTA']}%(name)-12s{COLORS['RESET']} | "
    f"%(levelname_colored)s | "
    f"{COLORS['WHITE']}%(message)s{COLORS['RESET']}"
)

# Log format for file without colors
FILE_FORMAT = "%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s"

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to levelname based on the level."""
    
    LEVEL_COLORS = {
        logging.DEBUG: COLORS['BLUE'],
        logging.INFO: COLORS['GREEN'],
        logging.WARNING: COLORS['YELLOW'],
        logging.ERROR: COLORS['RED'],
        logging.CRITICAL: COLORS['RED'] + COLORS['BOLD'],
    }
    
    def format(self, record):
        # Add colored levelname
        levelname = record.levelname
        record.levelname_colored = (
            f"{self.LEVEL_COLORS.get(record.levelno, COLORS['RESET'])}"
            f"{levelname:8}{COLORS['RESET']}"
        )
        return super().format(record)

def setup_logger(
    name: str, 
    log_dir: Optional[str] = None,
    console_level: int = DEFAULT_CONSOLE_LEVEL,
    file_level: int = DEFAULT_FILE_LEVEL,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Name of the logger
        log_dir: Directory to store log files (default: ./logs)
        console_level: Logging level for console output
        file_level: Logging level for file output
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(min(console_level, file_level))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_formatter = ColoredFormatter(CONSOLE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if enable_file:
        # Create log directory if it doesn't exist
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")
        
        # Delete older log files for this logger
        old_log_pattern = os.path.join(log_dir, f"{name}_*.log")
        old_logs = glob.glob(old_log_pattern)
        
        # Sort by creation time (newest last)
        old_logs.sort(key=os.path.getctime)
        
        # Remove all but the newest log file (which will be the one we're creating now)
        for old_log in old_logs:
            try:
                os.remove(old_log)
                logger.debug(f"Deleted old log file: {old_log}")
            except Exception as e:
                # Just log the error but continue
                print(f"Error deleting old log file {old_log}: {str(e)}")
        
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(FILE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Log the file location for reference
        logger.info(f"Logging to file: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If the logger doesn't have handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger 