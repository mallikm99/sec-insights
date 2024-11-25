import os
import logging
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(project_root, "../../logs")

def configure_logger(
    log_file_name=None,
    debug_mode=False,
    console_mode=False,
    overwrite=False,
):
    # Set (str) log_file to store logs to a file instead of console
    # Set (bool) debug_mode to change the visibility of logger.debug()
    # Set (bool) overwrite to overwrite the log file if it already exists

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if log_file_name:
        # Extract directory path and file name from log_file
        log_file = os.path.basename(log_file_name)

        # Create necessary dirs
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Combine directory path and modified log file name
        log_file_path = os.path.join(log_dir, log_file)

        # Create a file handler for logging to the specified log file
        # Use 'w' mode for overwrite, 'a' mode for append
        file_mode = "w" if overwrite else "a"
        file_handler = logging.FileHandler(log_file_path, mode=file_mode)
        file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    if console_mode:
        # Create a console handler for logging to the console (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

    return logger