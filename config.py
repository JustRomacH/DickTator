import logging
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import timezone, timedelta

load_dotenv()

COMMANDS: dict = {
    "info": "выводит это сообщение",
    "dick": "изменяет размер писюна",
    "attempts": "выводит количество попыток",
    "top": "выводит глобальный топ игроков",
    "stalcraft": "скидывает лицо из Stalcraft",
    "gosdolg": "выводит госдолг США",
    "place": "выводит место в топе"
}


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
    CONN_RETRY_DELAY: int = 30
    DICK_PENALTY: int = -10
    ATTS_ADD_HOUR: int = 17
    MIN_DICK_DELTA: int = 0
    MAX_DICK_DELTA: int = 10
    USERS_IN_TOP: int = 10
    TIMEZONE: timezone = timezone(timedelta(hours=3))
    GIT_REPO: str = Path(__file__).parent.resolve().joinpath(".git")
    US_DEBT_URL: str = "https://www.pgpf.org/national-debt-clock"
    US_DEBT_GIF: str = "https://media1.tenor.com/m/inHdJJ90TKEAAAAd/%D0%B4%D0%BE%D0%BB%D0%B3-%D1%81%D1%88%D0%B0.gif"
    STALCRAFT_FACE: str = "https://tenor.com/view/stalcraft-%D1%81%D0%BD%D1%8E%D1%81-minecraft-gif-19986730"

    BANNED_ACT: tuple[str] = (
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

    HELP: str = f"""Каждый день в {ATTS_ADD_HOUR}:00 всем выдаётся 
1 попытка увеличить свой писюн. Для этого
нужно использовать команду {PREFIX}dick. Рандом
выдаёт числа от {MIN_DICK_DELTA} до {MAX_DICK_DELTA} см. За запуск
Доты, Unturned и т.п. твой писюн
уменьшается на {abs(DICK_PENALTY)} см."""


setup_logging()
