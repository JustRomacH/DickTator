import asyncio
from config import *
from random import randint
from timer import get_time_delta
from mysql.connector import connect


class DataBase:
    def __init__(self):
        self.conn = connect(
            host=Config.HOST,
            user=Config.USER,
            password=Config.PASSWORD,
            database=Config.DATABASE
        )
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    # МЕТОДЫ ДЛЯ РАБОТЫ С БД

    # Возвращает выбранное значение по id
    def get_user_value(self, value: str, user_id: int) -> int:
        query = f"SELECT {value} FROM {Config.TABLE} WHERE id = %s"
        self.cur.execute(query, (user_id,))
        return self.cur.fetchone()[0]

    # Возвращает выбранные значения всех юзеров
    def get_values(self, value: str, order: str = None, reverse: bool = False) -> list[tuple]:
        query = f"SELECT {value} FROM {Config.TABLE} "
        # Порядок сортировки
        if order:
            query += f"ORDER BY {order} "
            if reverse:
                query += "DESC"
        self.cur.execute(query)
        return self.cur.fetchall()

    # Изменяет выбранное значение у юзера
    def update_value(self, value: str, new_value: int, user_id: int) -> None:
        query = f"""UPDATE {Config.TABLE} SET {value} = %s WHERE id = %s"""
        self.cur.execute(query, (new_value, user_id))

    # Добавляет юзера в БД
    def add_user(self, user_id: int) -> None:
        try:
            query = f"""INSERT INTO {Config.TABLE} VALUES (%s, 0, 1)"""
            self.cur.execute(query, (user_id,))
            logging.info("User added")
        except Exception as ex:
            logging.error(ex)

    # Добавляет юзера, если его нет в БД
    def add_user_if_not_exist(self, user_id: int) -> None:
        try:
            query = f"""SELECT EXISTS(SELECT 1 FROM {Config.TABLE} WHERE id=%s)"""
            self.cur.execute(query, (user_id,))
            if not bool(self.cur.fetchone()[0]):
                self.add_user(user_id)
        except Exception as ex:
            logging.error(ex)

    # КОМАНДЫ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    def change_dick_size(self, user_id: int, mention: str, delta: int, is_penalty: bool = False) -> str:
        user_size = self.get_user_value("size", user_id)
        self.update_value("size", user_size + delta, user_id)
        return self.get_dick_answer(user_id, mention, delta, is_penalty)

    # Изменяет размер писюна на случайное число см
    def dick_random(self, user_id: int, mention: str) -> str:
        self.add_user_if_not_exist(user_id)
        attempts = self.get_user_value("attempts", user_id)
        if attempts > 0:
            # Вычитает одну попытку
            self.update_value("attempts", attempts - 1, user_id)
            delta = randint(Config.MIN_DICK_DELTA, Config.MAX_DICK_DELTA)
            return self.change_dick_size(user_id, mention, delta)
        else:
            return self.get_dick_answer(user_id, mention, is_atts_were=False)

    # Возвращает текст, которым ответит бот
    def get_dick_answer(self, user_id: int, mention: str, delta: int = 0, is_penalty: bool = False,
                        is_atts_were: bool = True) -> str:
        user_size = self.get_user_value("size", user_id)
        top_place = self.get_place_in_top(user_id)
        answer = f"{mention}, "
        if is_atts_were:
            if delta > 0:
                answer += f"твой писюн вырос на {delta} см."
            elif delta < 0:
                answer += f"твой писюн уменьшился на {abs(delta)} см."
            else:
                answer += f"твой писюн не изменился."
            answer += f"\nТеперь он равен {user_size} см.\nТы занимаешь {top_place} место в топе."
        else:
            answer += f"у тебя не осталось попыток."
            answer += f"\nСейчас твой писюн равен {user_size} см.\nТы занимаешь {top_place} место в топе."
        if not is_penalty:
            answer += "\n" + self.get_attempts(user_id)
        return answer

    # КОМАНДЫ БОТА

    # Возвращает количество оставшихся попыток у юзера
    def get_attempts(self, user_id: int) -> str:
        self.add_user_if_not_exist(user_id)
        attempts = self.get_user_value("attempts", user_id)
        match attempts:
            case 0:
                answer = f"У тебя не осталось попыток"
            case 1:
                answer = f"У тебя осталась 1 попытка"
            case _:
                answer = f"У тебя осталось {attempts} {self.get_atts_ending(attempts)}"
        return answer

    # Возвращает общий топ юзеров
    def get_top(self) -> list[[int, int, int]]:
        try:
            users = self.get_values("*", "size", True)
        except Exception:
            users = list()
        return users

    # Возвращает позицию юзера в общем топе
    def get_place_in_top(self, user_id: int) -> int:
        for i, user_inf in enumerate(self.get_top()):
            if user_id in user_inf:
                return i + 1

    # ДРУГИЕ ФУНКЦИИ

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts(self) -> None:
        try:
            while True:
                # Оставшееся время до добавления попыток
                time_delta = get_time_delta(Config.ATTS_ADD_HOUR)
                await asyncio.sleep(time_delta)
                users = self.get_values("*")
                if users:
                    for user in users:
                        attempts = self.get_user_value("attempts", user[0])
                        self.cur.execute(f"UPDATE {Config.TABLE} SET 'attempts' = {attempts + 1} WHERE id = {user[0]}")
                logging.info("Attempts added")
        except Exception as ex:
            logging.error(ex)

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
