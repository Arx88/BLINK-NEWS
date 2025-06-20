import logging
import os

def setup_logger():
    """Sets up a rotating file logger for the backend application."""

    # Robust path to project_root/LOG from news-blink-backend/src/logger_config.py
    log_dir_relative_to_file = os.path.join(os.path.dirname(__file__), '..', '..', 'LOG')
    log_directory = os.path.abspath(log_dir_relative_to_file)
    print(f"[LoggerSetup] Resolved log directory: {log_directory}", flush=True)

    print(f"[LoggerSetup] Checking if log directory exists: {log_directory}", flush=True)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        print(f"[LoggerSetup] Created log directory. Exists now: {os.path.exists(log_directory)}", flush=True)

    log_file_path = os.path.join(log_directory, "VoteFixLog.log")
    print(f"[LoggerSetup] Resolved log file path: {log_file_path}", flush=True)

    # Get the logger
    logger = logging.getLogger("blink_backend") # Use a specific name for our app's logger
    logger.setLevel(logging.DEBUG) # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Prevent multiple handlers if setup_logger is called more than once accidentally
    if logger.hasHandlers():
        logger.handlers.clear()

    # Log Formatter - Define formatter before try block for FileHandler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )

    # File Handler
    try:
        print(f"[LoggerSetup] Attempting to create FileHandler for: {log_file_path}", flush=True)
        # Overwrites the log file on each run.
        file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG) # Set level for file handler

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        print(f"[LoggerSetup] SUCCESSFULLY added FileHandler for {log_file_path}. Logger '{logger.name}' handlers: {[type(h).__name__ for h in logger.handlers]}", flush=True)
    except Exception as e:
        print(f"[LoggerSetup] !!! ERROR setting up FileHandler for {log_file_path}: {e} !!!", flush=True)
        # Optionally, re-raise or handle as critical failure

    # Console Handler (optional, good for development/debugging alongside file logs)
    # This setup is outside the try-except for the FileHandler.
    # If it also needs protection, it would require its own try-except.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Or DEBUG, depending on verbosity needed in console
    console_handler.setFormatter(formatter) # Assuming same formatter is okay

    # logger.addHandler(console_handler) # Uncomment if console output is also desired
    # If console_handler is added, the print statement above would need adjustment or another one added.

    print(f"[LoggerSetup] setup_logger function complete. Returning logger '{logger.name}'.", flush=True)
    return logger

# Create a logger instance to be imported by other modules
# This way, setup_logger() is called once when this module is first imported.
app_logger = setup_logger()

if __name__ == '__main__':
    # Example usage if running this file directly for testing
    # Note: log_directory used here will be relative to this file's execution path if run directly
    # For testing the relative path from project root, run this script from the project root.
    # However, the 'app_logger' instance will use the robust path when imported.

    current_file_dir_log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'LOG', 'VoteFixLog.log')
    current_file_dir_log_path = os.path.abspath(current_file_dir_log_path)

    test_logger = setup_logger() # This will re-setup using the same name, clearing handlers
    test_logger.debug("This is a debug message for logger setup test.")
    test_logger.info("This is an info message for logger setup test.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    print(f"Test logs should be in {current_file_dir_log_path}")
    print(f"The app_logger will log to the same file when imported: {log_file_path}")
