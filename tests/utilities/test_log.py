import logging

import pytest
from flowi.utilities.logger import Logger


@pytest.fixture()
def logger_name():
    return "test_log"


def test_info(logger_name, caplog):
    logger = Logger(logger_name=logger_name)
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    with caplog.at_level(level=logging.DEBUG, logger=logger_name):
        logger.info(message)

    assert message in caplog.text
    assert "INFO" in caplog.text


def test_debug(logger_name, caplog):
    logger = Logger(logger_name=logger_name)
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    with caplog.at_level(level=logging.DEBUG, logger=logger_name):
        logger.debug(message)

    assert message in caplog.text
    assert "DEBUG" in caplog.text


def test_warning(logger_name, caplog):
    logger = Logger(logger_name=logger_name)
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    with caplog.at_level(level=logging.DEBUG, logger=logger_name):
        logger.warning(message)

    assert message in caplog.text
    assert "WARNING" in caplog.text


def test_error(logger_name, caplog):
    logger = Logger(logger_name=logger_name)
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    with caplog.at_level(level=logging.DEBUG, logger=logger_name):
        logger.error(message)

    assert message in caplog.text
    assert "ERROR" in caplog.text
