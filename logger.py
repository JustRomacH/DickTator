from timer import getTime
from termcolor import cprint


def success(text: str) -> str:
    time = getTime()
    response = f"[{time}] [+] {text}\n"
    cprint(response, "green")
    return response


def error(ex: Exception) -> str:
    time = getTime()
    response = f"[{time}] [-] {ex}\n"
    cprint(response, "red")
    return response


def warning(text: str) -> str:
    time = getTime()
    response = f"[{time}] [!] {text}\n"
    cprint(response, "yellow")
    return response


def inf(text: str) -> str:
    time = getTime()
    response = f"[{time}] [~] {text}\n"
    cprint(response, "white")
    return response


def unimportantInfo(text: str) -> str:
    time = getTime()
    response = f"[{time}] [~] {text}\n"
    cprint(response, "light_grey")
    return response


def main() -> None:
    success("test")


if __name__ == "__main__":
    main()
