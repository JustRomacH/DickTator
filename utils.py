from datetime import timezone
from datetime import datetime, timedelta


# Делает
def lower_first(text: str) -> str:
    return text[0].lower() + text[1:] if text else text


# Делает текст заголовком
def big(text: str) -> str:
    return "\n".join(f"### {line}" for line in text.split("\n"))


# Делает текст жирным
def bold(text: str) -> str:
    return f"**{text}**"


# Обрезает словарь
def slice_dict(full_dict: dict, gap: int) -> dict:
    items = full_dict.items()
    return dict(list(items)[:gap])


def get_current_time() -> datetime:
    tz: timezone = timezone(timedelta(hours=3))
    return datetime.today().astimezone(tz)


def get_current_time_formatted() -> str:
    time = get_current_time()
    return time.strftime("%d-%m-%Y %H:%M")


# Возвращает кол-во секунд до времени добавления попыток
def get_time_delta(target_hour: int) -> float:
    current_time = get_current_time()
    target_time: datetime = current_time.replace(
        day=current_time.day,
        hour=target_hour,
        minute=0,
        second=0,
        microsecond=0
    )

    if current_time > target_time:
        target_time += timedelta(days=1)

    return (target_time - current_time).total_seconds()


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
