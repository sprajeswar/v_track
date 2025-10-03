"""Application level logger configuration."""

import logging

from logging.handlers import RotatingFileHandler
from app.config import Config

def setup_logger(name: str) -> logging.Logger:
    """Set up the application logger.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL.upper())

    formatter = logging.Formatter(Config.LOG_FORMAT)

    # Console level handlers
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(formatter)
    c_handler.setLevel(logging.INFO)

    #File level handler
    f_handler = RotatingFileHandler(Config.LOG_FILE_PATH, maxBytes=Config.LOG_MAX_FILE_SIZE,
                                    backupCount=Config.LOG_BACKUP_COUNT)
    f_handler.setFormatter(formatter)
    f_handler.setLevel(logging.DEBUG)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger