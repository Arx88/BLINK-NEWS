import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Sets up a rotating file logger for the backend application."""

    # Robust path to project_root/LOG from news-blink-backend/src/logger_config.py
    log_dir_relative_to_file = os.path.join(os.path.dirname(__file__), '..', '..', 'LOG')
    log_directory = os.path.abspath(log_dir_relative_to_file)

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file_path = os.path.join(log_directory, "backend.log")

    # Get the logger
    logger = logging.getLogger("blink_backend") # Use a specific name for our app's logger
    logger.setLevel(logging.DEBUG) # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Prevent multiple handlers if setup_logger is called more than once accidentally
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler
    # Rotates logs at 5MB, keeping up to 5 backup logs.
    file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Set level for file handler

    # Console Handler (optional, good for development/debugging alongside file logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Or DEBUG, depending on verbosity needed in console

    # Log Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler) # Uncomment if console output is also desired

    return logger

# Create a logger instance to be imported by other modules
# This way, setup_logger() is called once when this module is first imported.
app_logger = setup_logger()

if __name__ == '__main__':
    # Example usage if running this file directly for testing
    # Note: log_directory used here will be relative to this file's execution path if run directly
    # For testing the relative path from project root, run this script from the project root.
    # However, the 'app_logger' instance will use the robust path when imported.

    current_file_dir_log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'LOG', 'backend.log')
    current_file_dir_log_path = os.path.abspath(current_file_dir_log_path)

    test_logger = setup_logger() # This will re-setup using the same name, clearing handlers
    test_logger.debug("This is a debug message for logger setup test.")
    test_logger.info("This is an info message for logger setup test.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    print(f"Test logs should be in {current_file_dir_log_path}")
    print(f"The app_logger will log to the same file when imported: {log_file_path}")
