from os import getenv
from pathlib import Path
from dataclasses import dataclass
from datetime import timezone, timedelta

COMMANDS: dict = {
    "infa": "выводит это сообщение",
    "dick": "изменяет размер писюна",
    "attempts": "выводит количество попыток",
    "stats": "выводит глобальный топ игроков",
    "stalcraft": "скидывает лицо из Stalcraft",
    "gosdolg": "выводит госдолг США"
}


# Основные переменные бота
@dataclass
class ConfigVars:
    TOKEN = getenv("TOKEN")
    PENALTY: int = -3
    ATTS_ADD_HOUR: int = 17
    MIN_DICK_DELTA: int = -5
    MAX_DICK_DELTA: int = 10
    TIMEZONE: timezone = timezone(timedelta(hours=3))
    GIT_REPO: str = Path(__file__).parent.resolve().joinpath(".git")
    US_DEBT_URL = "https://www.pgpf.org/national-debt-clock"
    US_DEBT_GIF = "https://media1.tenor.com/m/inHdJJ90TKEAAAAd/%D0%B4%D0%BE%D0%BB%D0%B3-%D1%81%D1%88%D0%B0.gif"
    STALCRAFT_FACE = "https://tenor.com/view/stalcraft-%D1%81%D0%BD%D1%8E%D1%81-minecraft-gif-19986730"

    BANNED_ACT: tuple[str] = (
        "stalcraft",
        "dota",
        "unturned",
        "genshin",
        "honkai",
        "zenless",
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
нужно использовать команду !dick. Рандом
выдаёт числа от {MIN_DICK_DELTA} до {MAX_DICK_DELTA} см. За запуск
Доты, Unturned и т.п. твой писюн
уменьшается на {abs(PENALTY)} см.

Команды:

Алиасы:"""
