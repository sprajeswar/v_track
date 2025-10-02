"""Application level configurations."""

import datetime as datetime
import os

class Config:
    """Class to hold application configurations."""

    LOG_DIR = "opt/logs"  # Define the log directory path
    os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the log directory exists

    LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")
    # LOG_LEVEL = os.getenv("LOG_FILE", LOG_FILE_PATH)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    LOG_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5