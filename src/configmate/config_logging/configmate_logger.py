import enum
import logging

LOG_FORMAT_STRING = "%(asctime)s - %(levelname)s - %(message)s"


class LoggingLevels(int, enum.Enum):
    TRACE = 5  ## -vvv
    DEBUG = logging.DEBUG  # -vv
    INFO = logging.INFO  # -v
    SUCCESS = 35
    WARNING = logging.WARNING  # default
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ConfigMateLogger(logging.Logger):
    def __init__(self, name: str = "ConfigMate", level: int = logging.NOTSET):
        super().__init__(name, level)

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(LoggingLevels.TRACE):
            self._log(LoggingLevels.TRACE, msg, args, **kwargs)

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(LoggingLevels.SUCCESS):
            self._log(LoggingLevels.SUCCESS, msg, args, **kwargs)


## Add logging levels
logging.addLevelName(LoggingLevels.TRACE, LoggingLevels.TRACE.name)
logging.addLevelName(LoggingLevels.SUCCESS, LoggingLevels.SUCCESS.name)


## Set logger
logger = ConfigMateLogger(__name__)
formatter = logging.Formatter(LOG_FORMAT_STRING)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
