from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from utils import get_words_right_form
from dataclasses import dataclass

load_dotenv()


# Основные переменные бота
@dataclass
class BotConfig:
    PREFIX: str = "!"
    TOKEN: str = getenv("TOKEN")
    RED_COLOR: str = 0xd95c5c
    FINE: int = -10
    ATTEMPTS_ADD_HOUR: int = 17
    ATTEMPTS_AMOUNT: int = 1
    MIN_DICK_DELTA: int = 0
    MAX_DICK_DELTA: int = 10
    MAX_USERS_IN_TOP: int = 10
    US_DEBT_URL: str = "https://www.pgpf.org/national-debt-clock"

    BANNED_ACTIVITIES: tuple[str] = (
        "dota",
        "unturned",
        "genshin",
        "honkai",
        "league of legends",
        "zenless",
        "destiny",
        "warframe"
    )

    LEAVE_PHRASES: tuple[str] = (
        "ливай с позором",
        "ну и ну! Вы разочаровывать Админ...",
        "ай ай ай...",
        "стыдно...",
        "я всё вижу",
        "не стыдно?",
        "мда...",
        "ууууууу..."
    )

    HELP_RESPONSE: str = (f"\nКаждый день в {ATTEMPTS_ADD_HOUR}:00 всем выдаётся"
                          f"\n{ATTEMPTS_AMOUNT} {get_words_right_form(ATTEMPTS_AMOUNT)[1]} увеличить свой писюн. "
                          f"\nДля этого нужно использовать команду {PREFIX}dick."
                          f"\nРандом выдаёт числа от {MIN_DICK_DELTA} до {MAX_DICK_DELTA} см."
                          f"\nЗапуск Доты, Unturned, Геншина и т.п. запрещён."
                          f"\nЗа нарушение твой писюн уменьшается на {abs(FINE)} см.")


@dataclass
class DBConfig:
    HOST: str = getenv("HOST")
    USER: str = getenv("USER")
    PASSWORD: str = getenv("PASSWORD")
    DATABASE: str = getenv("DATABASE")


@dataclass
class LoggerConfig:
    FILENAME: str = "dicktator.log"
    FILEPATH: str = Path(__file__).resolve().parent / FILENAME
    FILEMODE: str = "a"
