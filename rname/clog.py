import sys
from enum import Enum


class ReturnCode(Enum):
    """List of Error Exit Codes"""

    USER_ERROR = 3
    CODE_ERROR = 4
    SOFT_ERROR = 5


class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5


# TODO: log.printf("printf %s")
class Log:
    __instance = None

    def __new__(cls):
        if Log.__instance is None:
            Log.__instance = super().__new__(cls)
        return Log.__instance

    def __init__(self):
        self.__log_level = LogLevel.INFO

    def __print(self, level: LogLevel, message: str):
        if self.__log_level.value <= level.value:
            print(message)

    def debug(self, message: str):
        self.__print(LogLevel.DEBUG, f"DEBUG: {message}")

    def info(self, message: str):
        self.__print(LogLevel.INFO, f"INFO: {message}")

    def warning(self, message: str):
        self.__print(LogLevel.WARNING, f"WARNING: {message}")

    def error(self, message: str):
        self.__print(LogLevel.ERROR, f"ERROR: {message}")

    # TODO: raise Exception/use kwargs
    def fatal(self, message: str, return_code: ReturnCode):
        self.__print(LogLevel.FATAL, f"FATAL: {message}")
        sys.exit(return_code.value)

    def setLevel(self, level: LogLevel):
        self.__log_level = level
