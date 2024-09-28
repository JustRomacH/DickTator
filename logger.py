from timer import get_time
from termcolor import cprint


def success(text: str) -> str:
    response = f"[{get_time()}] [+] {text}"
    cprint(response, "green")
    return response


def error(ex: Exception) -> str:
    response = f"[{get_time()}] [-] {ex}"
    cprint(response, "red")
    return response


def warning(text: str) -> str:
    response = f"[{get_time()}] [!] {text}"
    cprint(response, "yellow")
    return response


def inf(text: str) -> str:
    response = f"[{get_time()}] [~] {text}"
    cprint(response, "white")
    return response


def unimportantInfo(text: str) -> str:
    response = f"[{get_time()}] [~] {text}"
    cprint(response, "light_grey")
    return response


def main() -> None:
    success("test")


if __name__ == "__main__":
    main()
