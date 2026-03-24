"""Centralized logging configuration for AI Pathfinder."""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3
_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_initialized = False


def get_logger(name: str = "ai_pathfinder") -> logging.Logger:
    """Return a logger. Initializes file handler on first call."""
    global _initialized
    logger = logging.getLogger(name)

    if not _initialized:
        _initialized = True
        logger.setLevel(logging.DEBUG)

        # Console handler (WARNING+)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(logging.Formatter(_FMT))
        logger.addHandler(ch)

        # File handler (DEBUG+, rotating)
        try:
            os.makedirs(_LOG_DIR, exist_ok=True)
            fh = RotatingFileHandler(
                _LOG_FILE, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter(_FMT))
            logger.addHandler(fh)
        except OSError:
            # Can't write logs — fall back to console only
            pass

    return logger
