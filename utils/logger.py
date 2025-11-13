# utils/logger.py
"""Logging configuration."""
import logging
import os
from datetime import datetime

from config.settings import LOG_DIR

def setup_logger(name=__name__, level=logging.INFO):
    """Setup and return a logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Create file handler
        log_file = os.path.join(LOG_DIR, f'veo_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(level)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger