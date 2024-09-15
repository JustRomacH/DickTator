from termcolor import cprint


def success(text: str) -> str:
    response = f"[+] {text}"
    cprint(response, "green")
    return response


def error(ex: Exception) -> str:
    response = f"[-] {ex}"
    cprint(response, "red")
    return response


def info(text: str) -> str:
    response = f"\n[INFO] {text}"
    cprint(response, "yellow")
    return response


def specialInfo(text: str) -> str:
    response = f"\n[INFO] {text}"
    cprint(response, "white")
    return response


def unimportantInfo(text: str) -> str:
    response = f"[~] {text}"
    cprint(response, "light_grey")
    return response


def unimportant(*texts: str) -> None:
    for index, text in enumerate(texts):
        answer = f"{index + 1}. {text}"
        cprint(answer, "light_grey")


def main() -> None:
    success("test")


if __name__ == "__main__":
    main()
