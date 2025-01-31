import asyncio
from utils import *
from config import *
from logger import Logger
from random import randint
from mysql.connector import connect


class DataBase:
    def __init__(
            self, host: str, user: str, password: str, database: str, reconnect: bool = True
    ) -> None:
        self.HOST: str = host
        self.USER: str = user
        self.PASSWORD: str = password
        self.DATABASE: str = database
        self.LOGGER = Logger()

        try:
            self.conn = connect(
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
                database=self.DATABASE
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            self.LOGGER.success(f"Successfully connected to {Config.DATABASE} database")

        except Exception as ex:
            self.LOGGER.error(f"Error connecting to the {Config.DATABASE}: {ex}")

        finally:

            if not reconnect:
                return

            if __name__ == "__main__":
                asyncio.run(self.reconnect_on_error())
            else:
                asyncio.create_task(self.reconnect_on_error())

    # Проверяет подключение и пытается переподключиться
    async def reconnect_on_error(self) -> None:
        while True:
            try:
                if not self.conn:
                    self.LOGGER.debug("Attempting to reconnect to the database...")

                    self.conn = connect(
                        host=self.HOST,
                        user=self.USER,
                        password=self.PASSWORD,
                        database=self.DATABASE
                    )
                    self.conn.autocommit = True
                    self.cursor = self.conn.cursor()

                    self.LOGGER.success("Successfully reconnected to database")

            except Exception as ex:
                self.LOGGER.error(f"Reconnection failed: {ex}")

            finally:
                await asyncio.sleep(Config.RECONNECT_DELAY)


class Table(DataBase):
    def __init__(
            self, host: str, user: str, password: str, database: str, table: str, reconnect: bool = True
    ) -> None:
        super().__init__(host, user, password, database, reconnect)
        self.TABLE: str = table

    # МЕТОДЫ ДЛЯ РАБОТЫ С ТАБЛИЦЕЙ

    # Возвращает выбранное значение по id
    def get_value(self, value: str, cond: str, cond_value: any) -> int:
        query: str = f"SELECT {value} FROM {self.TABLE} WHERE {cond} = %s"
        self.cursor.execute(query, (cond_value,))
        return self.cursor.fetchone()[0]

    # Возвращает выбранные значения всех юзеров
    def get_values(
            self, value: str, order: str = None, reverse: bool = False
    ) -> list[any]:
        query: str = f"SELECT {value} FROM {self.TABLE}"
        # Порядок сортировки
        if order:
            query += f" ORDER BY {order}"
            if reverse:
                query += " DESC"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # Изменяет выбранное значение у юзера
    def update_value(
            self, value: str, new_value: int, cond: str, cond_value: any
    ) -> None:
        query: str = f"UPDATE {self.TABLE} SET {value} = %s WHERE {cond} = %s"
        self.cursor.execute(query, (new_value, cond_value))

    # Удаляет выбранную строку
    def remove_string(self, cond: str, cond_value: any) -> None:
        query: str = f"DELETE FROM {self.TABLE} WHERE {cond} = %s"
        self.cursor.execute(query, (cond_value,))


class UsersTable(Table):
    def __init__(
            self, host: str, user: str, password: str, database: str, reconnect: bool = True
    ) -> None:
        super().__init__(host, user, password, database, "users", reconnect)

    # Добавляет юзера в таблицу
    def add_user(self, user_id: int) -> None:
        try:
            query: str = f"INSERT INTO {self.TABLE} VALUES (%s, 0, 1)"
            self.cursor.execute(query, (user_id,))
            self.LOGGER.success(f"User {user_id} added successfully")

        except Exception as ex:
            self.LOGGER.error(f"Error adding user {user_id}: {ex}")

    # Проверяет наличие юзера в таблице
    def is_user_exist(self, user_id: int) -> bool | None:
        try:
            query: str = f"SELECT EXISTS(SELECT 1 FROM {self.TABLE} WHERE id=%s)"
            self.cursor.execute(query, (user_id,))
            return bool(self.cursor.fetchone()[0])

        except Exception as ex:
            self.LOGGER.error(ex)

    # Добавляет юзера, если его нет в таблице
    def add_user_if_not_exist(self, user_id: int) -> None:
        try:
            if not self.is_user_exist(user_id):
                self.add_user(user_id)

        except Exception as ex:
            self.LOGGER.error(ex)

    # ФУНКЦИИ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    def change_dick_size(self, user_id: int, delta: int) -> str:
        user_size: int = self.get_dick_size(user_id)
        self.update_value("size", user_size + delta, "id", user_id)
        return self.get_dick_resp(user_id, delta=delta)

    # Изменяет размер писюна на случайное число см
    def dick_random(self, user_id: int) -> str:
        self.add_user_if_not_exist(user_id)
        attempts: int = self.get_value("attempts", "id", user_id)

        if attempts > 0:
            # Вычитает одну попытку
            self.update_value("attempts", attempts - 1, "id", user_id)
            delta: int = randint(Config.MIN_DICK_DELTA, Config.MAX_DICK_DELTA)
            return self.change_dick_size(user_id, delta=delta)

        else:
            return self.get_dick_resp(user_id, is_atts_were=False)

    # Возвращает текст, которым ответит бот
    def get_dick_resp(
            self, user_id: int, delta: int = 0, is_atts_were: bool = True
    ) -> str:
        user_size: int = self.get_dick_size(user_id)
        global_top = self.get_global_top()
        top_place: int = self.get_place_in_top(user_id, global_top)

        if is_atts_were:  # Если до вызова функции у юзера оставались попытки
            return (f"{self.get_size_change_resp(delta)}"
                    f"\nТеперь он равен {user_size} см"
                    f"\nТы занимаешь {top_place} место в глобальном топе"
                    "\n" + self.get_attempts_resp(user_id))

        else:
            return (f"{self.get_attempts_resp(user_id).lower()}"
                    f"\nСейчас твой писюн равен {user_size} см"
                    f"\nТы занимаешь {top_place} место в глобальном топе")

    # КОМАНДЫ БОТА

    # Возвращает текст с количеством попыток
    def get_attempts_resp(self, user_id: int) -> str:
        attempts: int = self.get_attempts(user_id)
        left_form, attempts_form = get_words_right_form(attempts)

        match attempts:
            case 0:
                return f"У тебя не осталось попыток"
            case _:
                return f"У тебя {left_form} {attempts} {attempts_form}"

    # Возвращает текст с размером писюна
    def get_dick_size_resp(self, user_id: int) -> str:
        size: int = self.get_dick_size(user_id)
        return f"Сейчас твой писюн имеет размер {size} см"

    # ДРУГИЕ ФУНКЦИИ

    # Возвращает количество оставшихся попыток у юзера
    def get_attempts(self, user_id: int) -> int:
        self.add_user_if_not_exist(user_id)
        return self.get_value("attempts", "id", user_id)

    # Возвращает размер писюна юзера
    def get_dick_size(self, user_id: int) -> int:
        self.add_user_if_not_exist(user_id)
        return self.get_value("size", "id", user_id)

    # Возвращает общий топ юзеров
    def get_global_top(self) -> dict[int, int]:
        try:
            top_list: list[tuple[int, int]] = self.get_values(
                "id, size", "size", True
            )
            top_dict: dict[int, int] = {
                user_inf[0]: user_inf[1]
                for user_inf in top_list
            }
            return top_dict

        except Exception:
            return dict()

    # Возвращает обрезанный топ
    def get_sliced_global_top(self) -> dict[int, int]:
        top = self.get_global_top()
        return slice_dict(top, Config.MAX_USERS_IN_TOP)

    # Возвращает позицию юзера в общем топе
    @staticmethod
    def get_place_in_top(user_id: int, top: dict[int, int]) -> int:
        numbered_top: dict[int, int] = {user: i + 1 for i, user in enumerate(top.keys())}
        return numbered_top.get(user_id)

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts_coroutine(self) -> None:
        try:
            while True:
                # Оставшееся время до добавления попыток
                time_delta: float = get_time_delta(Config.ATTEMPTS_ADD_HOUR)
                await asyncio.sleep(time_delta)  # Ждёт назначенное время
                self.add_attempts()
                self.LOGGER.debug("Attempts added")

        except Exception as ex:
            self.LOGGER.error(ex)

    def add_attempts(self):
        users: list[tuple[int, int]] = self.get_values("id, attempts")

        for user_id, attempts in users:
            query: str = f"UPDATE {self.TABLE} SET attempts = %s WHERE id = %s"
            self.cursor.execute(query, (attempts + Config.ATTEMPTS_AMOUNT, user_id))

    # Возвращает текст ответа на изменение размера писюна
    @staticmethod
    def get_size_change_resp(delta: int) -> str:
        if delta > 0:
            return f"твой писюн вырос на {delta} см"
        elif delta < 0:
            return f"твой писюн уменьшился на {abs(delta)} см"
        else:
            return f"твой писюн не изменился"


def main():
    UsersTable(
        Config.HOST,
        Config.USER,
        Config.PASSWORD,
        Config.DATABASE,
        reconnect=False
    ).add_attempts()


if __name__ == "__main__":
    main()
