# custom_logger.py
import logging
from colorama import Fore, Style, init
import sys

# Initialize colorama (for Windows)
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    # Define color codes for different log levels
    COLOR_MAP = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        # Get the color for the current log level
        color = self.COLOR_MAP.get(record.levelno, Fore.WHITE)
        
        # Create the log format string
        log_fmt = f"{color}%(asctime)s | %(levelname)s | %(message)s{Style.RESET_ALL}"
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        
        # Format the log record
        return formatter.format(record)

def get_custom_logger(name="customLogger"):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers to avoid adding multiple handlers
    if not logger.hasHandlers():
        # Create a console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        
        # Create and set the custom formatter
        color_formatter = ColorFormatter()
        ch.setFormatter(color_formatter)

        # Add the handler to the logger
        logger.addHandler(ch)

    return logger
