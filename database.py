import random
import sqlite3
from logger import *
from timer import startCoroutine


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("dicktator.db")
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def get_dick_answer(self, user_id: int, mention, delta: int, user_size: int, is_penalty: bool,
                        attempts: int = 0) -> str:
        if not is_penalty:
            if delta > 0:
                return f"""{mention}, твой писюн вырос на {delta} см.
Теперь он равен {user_size} см.
Ты занимаешь {self.get_place_in_top(user_id)} место в топе.
Осталось попыток: {attempts}"""
            elif delta < 0:
                return f"""{mention}, твой писюн уменьшился на {abs(delta)} см.
Теперь он равен {user_size} см.
Ты занимаешь {self.get_place_in_top(user_id)} место в топе.
Осталось попыток: {attempts}"""
            else:
                return f"""{mention}, твой писюн не изменился.
Сейчас он равен {user_size} см.
Ты занимаешь {self.get_place_in_top(user_id)} место в топе.
Осталось попыток: {attempts}"""
        else:
            return f"""{mention}, твой писюн уменьшился на {abs(delta)} см.
Теперь он равен {user_size} см.
Ты занимаешь {self.get_place_in_top(user_id)} место в топе."""

    def get_value(self, value: str, cond: str, cond_value: any) -> any:
        req = self.cur.execute(f"""SELECT {value} FROM users WHERE {cond} = {cond_value}""")
        return req.fetchone()[0]

    def update_value(self, value: str, new_value: any, cond: str, cond_value: any) -> None:
        self.cur.execute(f"""UPDATE users SET {value} = {new_value} WHERE {cond} = {cond_value}""")

    def is_user_exist(self, user_id: int) -> bool:
        req = self.cur.execute(f"""SELECT EXISTS(SELECT 1 FROM users WHERE id={user_id})""")
        return bool(req.fetchone()[0])

    def add_user(self, user_id: int) -> None:
        try:
            self.cur.execute(f"""INSERT INTO users VALUES ({user_id}, 0, 1)""")
            inf("Пользователь добавлен")
        except Exception as ex:
            error(ex)

    def add_attempts(self) -> None:
        try:
            conn = sqlite3.connect("dicktator.db")
            conn.autocommit = True
            cur = conn.cursor()
            users = cur.execute("""SELECT * FROM users""").fetchall()
            if users:
                for user in users:
                    attempts = cur.execute(f"SELECT attempts FROM users WHERE id = {user[0]}").fetchone()[0]
                    cur.execute(f"UPDATE users SET 'attempts' = {attempts + 1} WHERE id = {user[0]}")
            cur.close()
            conn.close()
            success("Попытки добавлены")
            startCoroutine(self.add_attempts)
        except Exception as ex:
            error(ex)

    def change_size(self, user_id: int, delta: int, is_penalty: bool = True, mention="User", attempts: int = 0) -> str:
        if not self.is_user_exist(user_id):
            self.add_user(user_id)
        user_size = self.get_value("size", "id", user_id)
        if user_size + delta < 0:
            new_size = 0
            self.update_value("size", new_size, "id", user_id)
        else:
            new_size = user_size + delta
            self.update_value("size", new_size, "id", user_id)
        return self.get_dick_answer(user_id, mention, delta, new_size, is_penalty, attempts)

    def dick_db(self, user_id: int, mention="User") -> str:
        if not self.is_user_exist(user_id):
            self.add_user(user_id)
        attempts = self.get_value("attempts", "id", user_id)
        user_size = self.get_value("size", "id", user_id)
        if attempts > 0:
            attempts -= 1
            self.update_value("attempts", attempts, "id", user_id)
            delta = random.randint(-5, 10)
            return self.change_size(user_id, delta, False, mention, attempts)
        else:
            return f"""{mention}, у тебя не осталось попыток.
Сейчас у тебя {user_size} см.
Ты занимаешь {self.get_place_in_top(user_id)} место в топе."""

    def get_top(self) -> list:
        try:
            users = self.cur.execute("SELECT * FROM users ORDER BY size DESC").fetchall()
        except Exception as ex:
            users = []
            error(ex)
        return users

    def get_place_in_top(self, user_id: int) -> int:
        for i, user in enumerate(self.get_top()):
            if user_id == user[0]:
                return i + 1

    def subtract_attempts(self):
        try:
            for user in self.cur.execute("""SELECT id FROM users""").fetchall():
                attempts = self.get_value("attempts", "id", user[0])
                self.update_value("attempts", attempts - 1, "id", user[0])
            success("Попытки вычтены")
        except Exception as ex:
            error(ex)


def main():
    db = DataBase()
    # db.subtractAttempts()
    db.cur.execute("""DELETE FROM users""")
    # db.cur.execute("""CREATE TABLE users (id integer PRIMARY KEY, size integer, attempts integer)""")


if __name__ == "__main__":
    main()
