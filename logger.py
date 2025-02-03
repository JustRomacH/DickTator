import inspect
import platform
from utils import *
from config import *
from termcolor import cprint
from functools import lru_cache


class Logger:
    _instance = None

    def __new__(cls, output: bool = True):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, output: bool = True):
        if self._initialized:
            return
        self._initialized = True

        self.terminal_out = output
        self.FILE = open(
            file=LoggerConfig.FILENAME,
            mode=LoggerConfig.FILEMODE,
            encoding="utf-8",
            errors="ignore",
        )
        self.OS = platform.system()

    def __del__(self):
        if hasattr(self, "FILE") and not self.FILE.closed:
            self.FILE.close()

    @lru_cache(maxsize=128)
    def get_caller(self):
        try:
            caller_frame = inspect.stack()[2]
            caller_function = caller_frame.function
            caller_class = None
            f_locals = caller_frame.frame.f_locals

            if 'self' in f_locals:
                caller_class = f_locals['self'].__class__.__name__
            elif 'cls' in f_locals:
                caller_class = f_locals['cls'].__name__

            return f"{caller_class}.{caller_function}" if caller_class else caller_function

        except Exception as ex:
            self.error(ex)
            return "Unknown"

    def output(self, log, color: str = "grey") -> None:
        if self.OS == "Windows":
            cprint(log, color)
        self.FILE.write(log + "\n")

    def log_message(self, level, color, message):
        time = get_current_time_formatted()
        caller = self.get_caller()
        log = f"[{level}] [{time}] {caller} >>> {message}"
        self.output(log, color)

    def debug(self, message) -> None:
        self.log_message("~", "grey", message)

    def success(self, message) -> None:
        self.log_message("+", "green", message)

    def warning(self, message) -> None:
        self.log_message("!", "yellow", message)

    def error(self, message) -> None:
        self.log_message("-", "red", message)


def main():
    logger = Logger(output=True)


if __name__ == "__main__":
    main()
