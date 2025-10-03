"""Application level configurations."""

import datetime as datetime
import os

class Config:
    """Class to hold application configurations."""

    LOG_DIR: str = "opt/logs"  # Define the log directory path
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    LOG_FILE_PATH: str = os.path.join(LOG_DIR, "app.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    LOG_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5

    # Expected keys in the requirements file
    # Any change in this order should be reflected in
    # app/services/vulners_service.py:_validate_and_process_file
    EXPECTED_KEYS: list = ["name", "version", "ecosystem"]

    # Set this flag to True to allow re-creation of projects
    # with the same name. This will overwrite the existing
    REDO_FOR_SAME_PROJECT: bool = False

    #LRU Cache size for API responses
    LRU_CACHE_SIZE: int = 16
    LRU_CACHE_TYPED: bool = False