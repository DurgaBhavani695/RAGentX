import logging
from app.core.logger import logger

def test_logger_instance():
    assert isinstance(logger, logging.Logger)
    assert logger.name == "app"

def test_logger_level():
    assert logger.level == logging.INFO
