import asyncio
from config import *
from config import Config
from random import randint
from mysql.connector import connect
from datetime import datetime, timedelta


class DataBase:
    def __init__(
            self, host: str, user: str, password: str, database: str
    ) -> None:
        self.HOST: str = host
        self.USER: str = user
        self.PASSWORD: str = password
        self.DATABASE: str = database
        self.conn = None
        self.cursor = None

        try:
            self.connect_to_db()
            logging.info("Successfully connected to database")

        except Exception as ex:
            logging.error(ex)

        # finally:
        # asyncio.create_task(self.reconnect_on_error())

    # Подключение к базе данных
    def connect_to_db(self):
        self.conn = connect(
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    # Проверяет подключение и пытается переподключиться
    async def reconnect_on_error(self) -> None:
        while True:
            try:
                if not self.conn:
                    logging.info("Trying to reconnect")
                    self.connect_to_db()
                    logging.info("Successfully reconnected to database")

            except Exception as ex:
                logging.error(ex)

            finally:
                await asyncio.sleep(Config.CONN_RETRY_DELAY)


class Table(DataBase):
    def __init__(
            self, host: str, user: str, password: str, database: str, table: str
    ) -> None:
        super().__init__(host, user, password, database)
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


class Users(Table):
    def __init__(
            self, host: str, user: str, password: str, database: str
    ) -> None:
        super().__init__(host, user, password, database, "users")

    # Добавляет юзера в таблицу
    def add_user(self, user_id: int) -> None:
        try:
            query: str = f"INSERT INTO {self.TABLE} VALUES (%s, 0, 1)"
            self.cursor.execute(query, (user_id,))
            logging.info("User added")

        except Exception as ex:
            logging.error(ex)

    # Проверяет наличие юзера в таблице
    def is_user_exist(self, user_id: int) -> bool:
        try:
            query: str = f"SELECT EXISTS(SELECT 1 FROM {self.TABLE} WHERE id=%s)"
            self.cursor.execute(query, (user_id,))
            return bool(self.cursor.fetchone()[0])

        except Exception as ex:
            logging.error(ex)

    # Добавляет юзера, если его нет в таблице
    def add_user_if_not_exist(self, user_id: int) -> None:
        try:
            if not self.is_user_exist(user_id):
                self.add_user(user_id)

        except Exception as ex:
            logging.error(ex)

    # ФУНКЦИИ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    def change_dick_size(self, user_id: int, delta: int) -> str:
        user_size: int = self.get_value("size", "id", user_id)
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
        user_size: int = self.get_value("size", "id", user_id)
        global_top = self.get_sliced_global_top()
        top_place: int = self.get_place_in_top(user_id, global_top)

        if is_atts_were:  # Если до вызова функции у юзера оставались попытки
            return (f"{self.get_size_change_resp(delta)}"
                    f"\nТеперь он равен {user_size} см"
                    f"\nТы занимаешь {top_place} место в глобальном топе."
                    "\n" + self.get_attempts_resp(user_id))

        else:
            return (f"{self.get_attempts_resp(user_id).lower()}"
                    f"\nСейчас твой писюн равен {user_size} см."
                    f"\nТы занимаешь {top_place} место в глобальном топе.")

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

    # ДРУГИЕ ФУНКЦИИ

    # Возвращает количество оставшихся попыток у юзера
    def get_attempts(self, user_id: int) -> int:
        self.add_user_if_not_exist(user_id)
        return self.get_value("attempts", "id", user_id)

    # Возвращает общий топ юзеров
    def get_global_top(self) -> dict[int, int]:
        try:
            top_list: list[tuple[int, int]] = self.get_values(
                "id, size", "size", True
            )
            top_dict: dict[int, int] = {user_inf[0]: user_inf[1] for user_inf in top_list}
            return top_dict

        except Exception:
            return dict()

    # Возвращает обрезанный топ
    def get_sliced_global_top(self) -> dict[int, int]:
        top = self.get_global_top()
        return self.slice_dict(top, Config.MAX_USERS_IN_TOP)

    # Возвращает позицию юзера в общем топе
    @staticmethod
    def get_place_in_top(user_id: int, top: dict[int, int]) -> int:
        numbered_top: dict[int, int] = {user: i + 1 for i, user in enumerate(top.keys())}
        return numbered_top.get(user_id)

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts(self) -> None:
        try:
            while True:
                # Оставшееся время до добавления попыток
                time_delta: float = self.get_time_delta(Config.ATTS_ADD_HOUR)
                await asyncio.sleep(time_delta)  # Ждёт назначенное время
                users: list[tuple[int, int]] = self.get_values("id, attempts")

                for user in users:
                    user_id: int = user[0]
                    attempts: int = user[1]
                    query: str = f"UPDATE {self.TABLE} SET attempts = %s WHERE id = %s"
                    self.cursor.execute(query, (attempts + Config.ATTS_AMOUNT, user_id))

                logging.info("Attempts added")

        except Exception as ex:
            logging.error(ex)

    # Возвращает кол-во секунд до времени добавления попыток
    @staticmethod
    def get_time_delta(hour: int) -> float:
        cur_time: datetime = datetime.today().astimezone(Config.TIMEZONE)
        next_time: datetime = cur_time.replace(
            day=cur_time.day,
            hour=hour,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=Config.TIMEZONE
        )

        if cur_time > next_time:
            next_time += timedelta(days=1)

        delta_time: float = (next_time - cur_time).total_seconds()
        return delta_time

    # Возвращает текст ответа на изменение размера писюна
    @staticmethod
    def get_size_change_resp(delta: int) -> str:
        if delta > 0:
            return f"твой писюн вырос на {delta} см."
        elif delta < 0:
            return f"твой писюн уменьшился на {abs(delta)} см."
        else:
            return f"твой писюн не изменился."

    # Обрезает словарь
    @staticmethod
    def slice_dict(full_dict: dict, gap: int) -> dict:
        items = full_dict.items()
        return dict(list(items)[:gap])


def main():
    Users(
        Config.HOST,
        Config.USER,
        Config.PASSWORD,
        Config.DATABASE
    )


if __name__ == "__main__":
    main()
