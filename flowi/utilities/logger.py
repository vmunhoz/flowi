import logging

from flowi import settings

logging.basicConfig(level=settings.LOG_LEVEL)
_log_format = "%(name)s - %(levelname)s - %(message)s"
_formatter = logging.Formatter(_log_format)


class Logger(object):
    def __init__(self, logger_name: str):
        self._logger = logging.getLogger(logger_name)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(_formatter)

        self._logger.addHandler(stream_handler)

    def info(self, message: str):
        self._logger.info(message)

    def debug(self, message: str):
        self._logger.debug(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str, exc_info=True):
        self._logger.error(message, exc_info=exc_info)
