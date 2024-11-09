import asyncio
from config import *
from random import randint
from timer import get_time_delta
from mysql.connector import connect, Error as MySQLError


class DataBase:
    def __init__(
            self, host: str, user: str, password: str, database: str
    ) -> None:
        self.HOST = host
        self.USER = user
        self.PASSWORD = password
        self.DATABASE = database
        try:
            self.connect_to_db()
            logging.info("Successfully connected to database")
        except MySQLError as ex:
            self.conn = None
            self.cur = None
            logging.error(ex)
        finally:
            if __name__ == "__main__":
                asyncio.run(self.reconnect_on_error())
            else:
                asyncio.create_task(self.reconnect_on_error())

    # Подключение к базе данных
    def connect_to_db(self):
        self.conn = connect(
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE
        )
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    # Проверяет подключение и пытается переподключиться
    async def reconnect_on_error(self) -> None:
        while True:
            try:
                if not self.conn.is_connected():
                    logging.info("Trying to reconnect")
                    self.connect_to_db()
                    logging.info("Successfully reconnected to database")
            except MySQLError as ex:
                logging.error(ex)
            await asyncio.sleep(Config.CONN_RETRY_DELAY)


class Table(DataBase):
    def __init__(
            self, host: str, user: str, password: str, database: str, table: str
    ) -> None:
        super().__init__(host, user, password, database)
        self.TABLE = table

    # МЕТОДЫ ДЛЯ РАБОТЫ С ТАБЛИЦЕЙ

    # Возвращает выбранное значение по id
    def get_value(self, value: str, cond: str, cond_value: any) -> int:
        query = f"SELECT {value} FROM {self.TABLE} WHERE {cond} = %s"
        self.cur.execute(query, (cond_value,))
        return self.cur.fetchone()[0]

    # Возвращает выбранные значения всех юзеров
    def get_values(
            self, value: str, order: str = None, reverse: bool = False
    ) -> list[tuple]:
        query = f"SELECT {value} FROM {self.TABLE} "
        # Порядок сортировки
        if order:
            query += f"ORDER BY {order} "
            if reverse:
                query += "DESC"
        self.cur.execute(query)
        return self.cur.fetchall()

    # Изменяет выбранное значение у юзера
    def update_value(
            self, value: str, new_value: int, cond: str, cond_value: any
    ) -> None:
        query = f"""UPDATE {self.TABLE} SET {value} = %s WHERE {cond} = %s"""
        self.cur.execute(query, (new_value, cond_value))


class Users(Table):
    def __init__(
            self, host: str, user: str, password: str, database: str
    ) -> None:
        super().__init__(host, user, password, database, "users")

    # Добавляет юзера в таблицу
    def add_user(self, user_id: int) -> None:
        try:
            query = f"INSERT INTO {self.TABLE} VALUES (%s, 0, 1)"
            self.cur.execute(query, (user_id,))
            logging.info("User added")
        except Exception as ex:
            logging.error(ex)

    # Добавляет юзера, если его нет в таблице
    def add_user_if_not_exist(self, user_id: int) -> None:
        try:
            query = f"SELECT EXISTS(SELECT 1 FROM {self.TABLE} WHERE id=%s)"
            self.cur.execute(query, (user_id,))
            if not bool(self.cur.fetchone()[0]):
                self.add_user(user_id)
        except Exception as ex:
            logging.error(ex)

    # ФУНКЦИИ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    def change_dick_size(
            self, user_id: int, mention: str, delta: int,
    ) -> str:
        user_size = self.get_value("size", "id", user_id)
        self.update_value("size", user_size + delta, "id", user_id)
        return self.get_dick_resp(user_id, mention, delta)

    # Изменяет размер писюна на случайное число см
    def dick_random(self, user_id: int, mention: str) -> str:
        self.add_user_if_not_exist(user_id)
        attempts = self.get_value("attempts", "id", user_id)
        if attempts > 0:
            # Вычитает одну попытку
            self.update_value("attempts", attempts - 1, "id", user_id)
            delta = randint(Config.MIN_DICK_DELTA, Config.MAX_DICK_DELTA)
            return self.change_dick_size(user_id, mention, delta)
        else:
            return self.get_dick_resp(user_id, mention, is_atts_were=False)

    # Возвращает текст, которым ответит бот
    def get_dick_resp(
            self, user_id: int, mention: str, delta: int = 0, is_atts_were: bool = True
    ) -> str:
        user_size = self.get_value("size", "id", user_id)
        top_place = self.get_place_in_top(user_id)
        if is_atts_were:  # Если до вызова функции у юзера оставались попытки
            resp = (f"{mention}, {self.get_change_resp(delta)}"
                    f"\nТеперь он равен {user_size} см."
                    f"\nТы занимаешь {top_place} место в топе."
                    "\n" + self.get_attempts_resp(user_id))
        else:
            resp = (f"{mention}, у тебя не осталось попыток."
                    f"\nСейчас твой писюн равен {user_size} см."
                    f"\nТы занимаешь {top_place} место в топе.")
        return resp

    # КОМАНДЫ БОТА

    # Возвращает текст с количеством попыток
    def get_attempts_resp(self, user_id: int) -> str:
        attempts = self.get_attempts(user_id)
        word_forms = self.get_words_right_form(attempts)
        left_form = word_forms[0]
        attempts_form = word_forms[1]
        if attempts == 0:
            return f"У тебя не осталось попыток"
        else:
            return f"У тебя {left_form} {attempts} {attempts_form}"

    # Возвращает общий топ юзеров
    def get_top(self) -> list[[int, int, int]]:
        try:
            users = self.get_values("id, size", "size", True)
        except Exception:
            users = list()
        return users

    # ДРУГИЕ ФУНКЦИИ

    # Возвращает количество оставшихся попыток у юзера
    def get_attempts(self, user_id: int) -> int:
        self.add_user_if_not_exist(user_id)
        return self.get_value("attempts", "id", user_id)

    # Возвращает позицию юзера в общем топе
    def get_place_in_top(self, user_id: int) -> int:
        for i, user_inf in enumerate(self.get_top()):
            if user_id in user_inf:
                return i + 1

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts(self) -> None:
        try:
            while True:
                # Оставшееся время до добавления попыток
                time_delta = get_time_delta(Config.ATTS_ADD_HOUR)
                await asyncio.sleep(time_delta)
                users = self.get_values("id")
                if users:
                    for user in users:
                        user_id = user[0]
                        attempts = self.get_value("attempts", "id", user_id)
                        query = f"UPDATE {self.TABLE} SET attempts = {attempts + 1} WHERE id = {user_id}"
                        self.cur.execute(query)
                        logging.info("Attempts added")
        except Exception as ex:
            logging.error(ex)

    @staticmethod
    def get_change_resp(delta: int) -> str:
        if delta > 0:
            return f"твой писюн вырос на {delta} см."
        elif delta < 0:
            return f"твой писюн уменьшился на {abs(delta)} см."
        else:
            return f"твой писюн не изменился."

    # Возвращает слова с правильными окончаниями
    @staticmethod
    def get_words_right_form(num: int | float) -> tuple[str, str]:
        if num == 1:
            return "осталась", "попытка"
        elif num in (2, 3, 4):
            return "осталось", "попытки"
        else:
            return "осталось", "попыток"


def main():
    DataBase(
        Config.HOST,
        Config.USER,
        Config.PASSWORD,
        Config.DATABASE
    )


if __name__ == "__main__":
    main()
