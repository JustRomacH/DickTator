from random import randrange
from config import Config
from datetime import datetime, timedelta


# Возвращает текущее время в виде строки
def get_time() -> str:
    time = datetime.today().astimezone(Config.TIMEZONE)
    return time.strftime("%d-%m %H:%M:%S")


# Возвращает кол-во секунд до n-ого часа
def get_time_delta(hour: int) -> float:
    cur_time = datetime.today().astimezone(Config.TIMEZONE)
    next_time = cur_time.replace(
        day=cur_time.day,
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=Config.TIMEZONE
    )
    if cur_time > next_time:
        next_time += timedelta(days=1)
    delta_time = (next_time - cur_time).total_seconds()
    return delta_time


# Возвращает кол-во секунд до случайного времени
def get_random_time_delta(hours_min: int, hours_max: int) -> float:
    cur_time = datetime.today().astimezone(Config.TIMEZONE)
    rand_hour = randrange(hours_min, hours_max)
    rand_min = randrange(0, 60)
    next_time = cur_time + timedelta(hours=rand_hour, minutes=rand_min)
    delta_time = (next_time - cur_time).total_seconds()
    return delta_time


def main():
    print(get_time())


if __name__ == "__main__":
    main()
