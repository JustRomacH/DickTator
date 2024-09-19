from typing import Callable
from threading import Timer
from random import randrange
from datetime import datetime, timedelta, timezone

tz = timezone(timedelta(hours=3))


def getTime() -> str:
    time = datetime.today().replace(tzinfo=tz)
    return time.strftime("%d-%m %H:%M:%S")


def convertTime(secs: float) -> str:
    time = datetime.today().replace(tzinfo=tz)
    time += timedelta(seconds=secs)
    return time.strftime("%d-%m %H:%M:%S")


def randomTime() -> float:
    cur_time = datetime.today().replace(tzinfo=tz)
    rand_hour = randrange(6, 18)
    rand_min = randrange(0, 60)
    next_time = cur_time + timedelta(hours=rand_hour, minutes=rand_min)
    delta_time = (next_time - cur_time).total_seconds()
    return delta_time


def startCoroutine(func: Callable, start_hour: int = 17) -> None:
    cur_time = datetime.today().replace(tzinfo=tz)
    next_time = cur_time.replace(
        day=cur_time.day,
        hour=start_hour,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=tz
    )
    if cur_time > next_time:
        next_time += timedelta(days=1)
    delta_time = (next_time - cur_time).total_seconds()
    t = Timer(delta_time, func)
    t.start()


def test():
    print("test")
    startCoroutine(test)


def main():
    test()


if __name__ == "__main__":
    main()
