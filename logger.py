import inspect
import platform
from utils import *
from config import *
from termcolor import cprint


class Logger:
    _instance = None

    def __init__(self):
        self.FILE = open(
            file=LoggerConfig.FILENAME,
            mode=LoggerConfig.FILEMODE,
            encoding="utf-8"
        )
        self.OS = platform.system()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_caller() -> str:
        caller_frame = inspect.stack()[2]

        caller_function = caller_frame.function
        caller_class = None
        f_locals = caller_frame.frame.f_locals

        # Проверяем, был ли вызов из класса
        if 'self' in f_locals:
            caller_class = f_locals['self'].__class__.__name__
        elif 'cls' in f_locals:
            caller_class = f_locals['cls'].__name__

        if caller_class:
            return f"{caller_class}.{caller_function}"
        else:
            return caller_function

    def output(self, log, color) -> None:
        if self.OS == "Windows":
            cprint(log, color)
        self.FILE.write(log + "\n")

    def debug(self, message) -> None:
        time: str = get_current_time_formatted()
        caller: str = self.get_caller()
        log: str = f"[~] [{time}] {caller} >>> {message}"
        self.output(log, "grey")

    def success(self, message) -> None:
        time: str = get_current_time_formatted()
        caller: str = self.get_caller()
        log: str = f"[+] [{time}] {caller} >>> {message}"
        self.output(log, "green")

    def warning(self, message) -> None:
        time: str = get_current_time_formatted()
        caller: str = self.get_caller()
        log: str = f"[!] [{time}] {caller} >>> {message}"
        self.output(log, "yellow")

    def error(self, message) -> None:
        time: str = get_current_time_formatted()
        caller: str = self.get_caller()
        log: str = f"[-] [{time}] {caller} >>> {message}"
        self.output(log, "red")


def main():
    logger = Logger()


if __name__ == "__main__":
    main()
