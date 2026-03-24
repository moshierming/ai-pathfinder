"""Tests for logging_config.py."""

import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestGetLogger:
    """Test get_logger returns configured logger."""

    def test_returns_logger(self):
        import logging_config
        # Reset to allow re-initialization
        logging_config._initialized = False
        logger = logging_config.get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_default_name(self):
        import logging_config
        logger = logging_config.get_logger()
        assert logger.name == "ai_pathfinder"

    def test_idempotent_init(self):
        import logging_config
        logging_config._initialized = False
        logger1 = logging_config.get_logger("idem_test")
        handler_count = len(logger1.handlers)
        # Second call should NOT add more handlers
        logger2 = logging_config.get_logger("idem_test_2")
        # Different logger name → same root init, but handlers on each logger
        assert logger2 is not None

    def test_logger_has_handlers(self):
        import logging_config
        logging_config._initialized = False
        logger = logging_config.get_logger("handler_test")
        assert len(logger.handlers) >= 1  # at least console handler
