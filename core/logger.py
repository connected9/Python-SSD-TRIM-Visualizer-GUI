# trimvision/core/logger.py

import logging
import os
from trimvision import config

def setup_logger():
    """Sets up the application logger."""
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] [%(threadName)-10.10s] [%(module)-10.10s L%(lineno)d] %(message)s"
    )
    logger = logging.getLogger(config.APP_NAME)
    logger.setLevel(logging.DEBUG) # Set to INFO for production

    # File Handler
    # Ensure the log file is in the same directory as the executable or script's main directory
    if getattr(sys, 'frozen', False): # PyInstaller bundle
        app_path = os.path.dirname(sys.executable)
    else: # Running as script
        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Up to trimvision/ root

    log_file_path = os.path.join(app_path, config.LOG_FILE)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Console Handler (optional, for debugging)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger

# Initialize logger once
import sys # Import sys here for the getattr check in setup_logger
logger = setup_logger()

if __name__ == '__main__':
    logger.info("Logger test: Info message.")
    logger.debug("Logger test: Debug message.")
    logger.warning("Logger test: Warning message.")
    logger.error("Logger test: Error message.")