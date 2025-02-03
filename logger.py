import inspect
import asyncio
import aiofiles
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
        self.filename = LoggerConfig.FILENAME
        self.filemode = LoggerConfig.FILEMODE
        self.lock = asyncio.Lock()

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
            asyncio.create_task(self.error(ex))
            return "Unknown"

    async def output(self, log, color: str = "grey") -> None:
        if self.terminal_out:
            cprint(log, color)
        async with self.lock:  # Предотвращает одновременную запись
            async with aiofiles.open(self.filename, mode=self.filemode, encoding="utf-8", errors="ignore") as file:
                await file.write(log + "\n")

    async def log_message(self, level, color, message):
        time = get_current_time_formatted()
        caller = self.get_caller()
        log = f"[{level}] [{time}] {caller} >>> {message}"
        await self.output(log, color)

    async def debug(self, message) -> None:
        await self.log_message("~", "grey", message)

    async def success(self, message) -> None:
        await self.log_message("+", "green", message)

    async def warning(self, message) -> None:
        await self.log_message("!", "yellow", message)

    async def error(self, message) -> None:
        await self.log_message("-", "red", message)


async def main():
    logger = Logger(output=True)
    await logger.success("Logger initialized successfully")


if __name__ == "__main__":
    asyncio.run(main())
