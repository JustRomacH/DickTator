from typing import Callable
from threading import Timer
from random import randrange
from config import ConfigVars
from datetime import datetime, timedelta


def get_time() -> str:
    time = datetime.today().astimezone(ConfigVars.TIMEZONE)
    return time.strftime("%d-%m %H:%M:%S")


def convert_time(secs: float) -> str:
    time = datetime.today().astimezone(ConfigVars.TIMEZONE)
    time += timedelta(seconds=secs)
    return time.strftime("%d-%m %H:%M:%S")


def get_time_delta(hour: int) -> float:
    cur_time = datetime.today().astimezone(ConfigVars.TIMEZONE)
    next_time = cur_time.replace(
        day=cur_time.day,
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=ConfigVars.TIMEZONE
    )
    if cur_time > next_time:
        next_time += timedelta(days=1)
    delta_time = (next_time - cur_time).total_seconds()
    return delta_time


def get_random_time_delta(hours_min: int, hours_max: int) -> float:
    cur_time = datetime.today().astimezone(ConfigVars.TIMEZONE)
    rand_hour = randrange(hours_min, hours_max)
    rand_min = randrange(0, 60)
    next_time = cur_time + timedelta(hours=rand_hour, minutes=rand_min)
    delta_time = (next_time - cur_time).total_seconds()
    return delta_time


def start_coroutine(func: Callable, delta_time: float) -> None:
    t = Timer(delta_time, func)
    t.start()


def main():
    print(get_time())


if __name__ == "__main__":
    main()
