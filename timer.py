from typing import Callable
from threading import Timer
from datetime import datetime, timedelta


def startCoroutine(func: Callable, start_hour: int = 17) -> None:
    cur_time = datetime.today()
    next_time = cur_time.replace(
        day=cur_time.day + 1,
        hour=start_hour,
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(days=1)
    # next_time = cur_time + timedelta(seconds=1)
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
