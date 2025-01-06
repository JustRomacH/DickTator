import logging
from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import timezone, timedelta

load_dotenv()


# Возвращает слова с правильными окончаниями
def get_words_right_form(num: int | float) -> tuple[str, str]:
    if 11 <= num % 100 <= 14:
        return "осталось", "попыток"
    match num % 10:
        case 1:
            return "осталась", "попытка"
        case 2 | 3 | 4:
            return "осталось", "попытки"
        case _:
            return "осталось", "попыток"


def setup_logging() -> None:
    format_str: str = "[%(asctime)s] [%(levelname)s] %(message)s"
    logging.basicConfig(
        filename="dicktator.log",
        filemode="a",
        format=format_str,
        level=logging.INFO,
        datefmt='%d-%m-%Y %H:%M'
    )


# Основные переменные бота
@dataclass
class Config:
    PREFIX: str = "!"
    TOKEN: str = getenv("TOKEN")
    HOST: str = getenv("HOST")
    USER: str = getenv("USER")
    PASSWORD: str = getenv("PASSWORD")
    DATABASE: str = getenv("DATABASE")
    RECONNECT_DELAY: int = 30
    FINE: int = -10
    ATTEMPTS_ADD_HOUR: int = 17
    ATTEMPTS_AMOUNT: int = 1
    MIN_DICK_DELTA: int = 0
    MAX_DICK_DELTA: int = 10
    MAX_USERS_IN_TOP: int = 10
    TIMEZONE: timezone = timezone(timedelta(hours=3))
    US_DEBT_URL: str = "https://www.pgpf.org/national-debt-clock"
    US_DEBT_GIF: str = "https://media1.tenor.com/m/inHdJJ90TKEAAAAd/%D0%B4%D0%BE%D0%BB%D0%B3-%D1%81%D1%88%D0%B0.gif"
    STALCRAFT_FACE: str = "https://tenor.com/view/stalcraft-%D1%81%D0%BD%D1%8E%D1%81-minecraft-gif-19986730"

    BANNED_ACTIVITIES: tuple[str] = (
        "stalcraft",
        "dota",
        "unturned",
        "genshin",
        "honkai",
        "zenless",
        "destiny",
        "warframe",
        "zzz"
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

    HELP_RESPONSE: str = ("**Общая информация:**"
                          f"\nКаждый день в {ATTEMPTS_ADD_HOUR}:00 всем выдаётся"
                          f"\n{ATTEMPTS_AMOUNT} {get_words_right_form(ATTEMPTS_AMOUNT)[1]} увеличить свой писюн. "
                          f"\nДля этого нужно использовать команду {PREFIX}dick."
                          f"\nРандом выдаёт числа от {MIN_DICK_DELTA} до {MAX_DICK_DELTA} см."
                          f"\nЗапуск Доты, Unturned, Stalcraft и т.п. запрещён."
                          f"\nЗа нарушение твой писюн уменьшается на {abs(FINE)} см.")


setup_logging()
