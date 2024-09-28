import sqlite3
import asyncio
from logger import *
from random import randint
from config import ConfigVars
from timer import get_time_delta


class DataBase:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("dicktator.db")
            success("База данных подключена...")
        except Exception as ex:
            error(ex)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    # МЕТОДЫ ДЛЯ РАБОТЫ С БД

    # Возвращает выбранное значение по id
    def get_user_value(self, value: str, user_id: int) -> int:
        req = self.cur.execute(f"""SELECT {value} FROM users WHERE id = {user_id}""")
        return req.fetchone()[0]

    # Возвращает выбранные значения всех юзеров
    def get_values(self, value: str, order: str = None, reverse: bool = False) -> list[list[int]]:
        req = f"SELECT {value} FROM users "
        # Порядок сортировки
        if order:
            req += f"ORDER BY {order} "
            if reverse:
                req += "DESC"
        return self.cur.execute(req).fetchall()

    # Изменяет выбранное значение у юзера
    def update_value(self, value: str, new_value: int, user_id: int) -> None:
        self.cur.execute(f"""UPDATE users SET {value} = {new_value} WHERE id = {user_id}""")

    # Добавляет юзера в БД
    def add_user(self, user_id: int) -> None:
        try:
            self.cur.execute(f"""INSERT INTO users VALUES ({user_id}, 0, 1)""")
            inf("Пользователь добавлен")
        except Exception as ex:
            error(ex)

    # Добавляет юзера, если его нет в БД
    def add_user_if_not_exist(self, user_id: int) -> None:
        try:
            req = self.cur.execute(f"""SELECT EXISTS(SELECT 1 FROM users WHERE id={user_id})""")
            print("is user")
            if not bool(req.fetchone()[0]):
                print("add user")
                self.add_user(user_id)
        except Exception as ex:
            error(ex)

    # КОМАНДЫ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    def change_dick_size(self, user_id: int, mention: str, delta: int, is_penalty: bool = False) -> str:
        user_size = self.get_user_value("size", user_id)
        if (user_size + delta) < 0:
            new_size = 0
        else:
            new_size = user_size + delta
        self.update_value("size", new_size, user_id)
        return self.get_dick_answer(user_id, mention, delta, is_penalty)

    # Изменяет размер писюна на случайное число см
    def dick_random(self, user_id: int, mention: str) -> str:
        self.add_user_if_not_exist(user_id)
        attempts = self.get_user_value("attempts", user_id)
        if attempts > 0:
            # Вычитает одну попытку
            attempts -= 1
            self.update_value("attempts", attempts, user_id)
            delta = randint(ConfigVars.MIN_DICK_DELTA, ConfigVars.MAX_DICK_DELTA)
            return self.change_dick_size(user_id, mention, delta)
        else:
            return self.get_dick_answer(user_id, mention)

    # Возвращает текст, которым ответит бот
    def get_dick_answer(self, user_id: int, mention: str, delta: int = 0, is_penalty: bool = False) -> str:
        user_size = self.get_user_value("size", user_id)
        attempts = self.get_user_value("attempts", user_id)
        top_place = self.get_place_in_top(user_id)
        answer = f"{mention}, "
        if attempts > 0:
            if delta > 0:
                answer += f"твой писюн вырос на {delta} см."
            elif delta < 0:
                answer += f"твой писюн уменьшился на {abs(delta)} см."
            else:
                answer += f"твой писюн не изменился."
            now_word = "Теперь"
        else:
            answer += f"у тебя не осталось попыток"
            now_word = "Сейчас"
        answer += f"\n{now_word} он равен {user_size} см.\nТы занимаешь {top_place} место в топе."
        if not is_penalty:
            match attempts:
                case 0:
                    f"\nУ тебя не осталось попыток"
                case 1:
                    f"\nУ тебя осталась 1 попытка"
                case _:
                    answer += f"\nУ тебя осталось {attempts} {self.get_atts_ending(attempts)}"
        return answer

    # КОМАНДЫ БОТА

    # Возвращает количество оставшихся попыток у юзера
    def get_attempts(self, user_id: int, mention: str) -> str:
        atts = self.get_user_value("attempts", user_id)
        answer = f"{mention}, у тебя осталось {atts} {self.get_atts_ending(atts)}"
        return answer

    # Возвращает общий топ юзеров
    def get_top(self) -> list[[int, int, int]]:
        try:
            users = self.get_values("*", "size", True)
        except Exception as ex:
            users = []
            error(ex)
        return users

    # Возвращает позицию юзера в общем топе
    def get_place_in_top(self, user_id: any) -> int:
        top = self.get_top()
        for i, user_inf in enumerate(top):
            if user_id in user_inf:
                return i + 1

    # ДРУГИЕ ФУНКЦИИ

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts(self) -> None:
        try:
            while True:
                # Оставшееся время до добавления попыток
                time_delta = get_time_delta(ConfigVars.ATTS_ADD_HOUR)
                await asyncio.sleep(time_delta)
                users = self.get_values("*")
                if users:
                    for user in users:
                        attempts = self.get_user_value("attempts", user[0])
                        self.cur.execute(f"UPDATE users SET 'attempts' = {attempts + 1} WHERE id = {user[0]}")
                success("Попытки добавлены")
        except Exception as ex:
            error(ex)

    @staticmethod
    # Возвращает "попытка" с правильным окончанием
    def get_atts_ending(num: int | float) -> str:
        if num == 1:
            return "попытка"
        elif num in (2, 3, 4):
            return "попытки"
        else:
            return "попыток"


def main():
    DataBase()


if __name__ == "__main__":
    main()
