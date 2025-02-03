import asyncio
import aiomysql
from utils import *
from config import *
from logger import Logger
from random import randint
from typing import Optional, Tuple, List, Any


class DataBase:
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.HOST: str = host
        self.USER: str = user
        self.PASSWORD: str = password
        self.DATABASE: str = database
        self.LOGGER: Logger = Logger()
        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self) -> None:
        try:
            self.pool = await aiomysql.create_pool(
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
                db=self.DATABASE,
                autocommit=True,
                minsize=1,
                maxsize=25
            )
            await self.LOGGER.success(f"Successfully connected to '{self.DATABASE}' database")

        except Exception as ex:
            await self.LOGGER.error(ex)

    async def execute(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)

        except Exception as ex:
            await self.LOGGER.error(ex)

    async def execute_one(self, query: str, params: Tuple[Any, ...] = ()) -> Any:
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    return await cur.fetchone()

        except Exception as ex:
            await self.LOGGER.error(ex)
            return None

    async def execute_many(
            self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[Tuple[Any, ...]]:
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    return await cur.fetchall()

        except Exception as ex:
            await self.LOGGER.error(ex)
            return list()


class Table(DataBase):
    def __init__(
            self, host: str, user: str, password: str, database: str, table: str
    ) -> None:
        super().__init__(host, user, password, database)
        self.TABLE: str = table

    async def get_value(self, value: str, cond: str, cond_value: Any) -> Optional[int]:
        query = f"SELECT {value} FROM {self.TABLE} WHERE {cond} = %s"
        result = await self.execute_one(query, (cond_value,))
        return result[0] if result else None

    async def get_values(
            self, value: str, order: Optional[str] = None, reverse: bool = False
    ) -> List[Tuple[Any, ...]]:
        query = f"SELECT {value} FROM {self.TABLE}"
        if order:
            query += f" ORDER BY {order} {'DESC' if reverse else 'ASC'}"
        result = await self.execute_many(query)
        return result

    async def update_value(self, value: str, new_value: int, cond: str, cond_value: Any) -> None:
        query = f"UPDATE {self.TABLE} SET {value} = %s WHERE {cond} = %s"
        await self.execute(query, (new_value, cond_value))

    async def remove_string(self, cond: str, cond_value: Any) -> None:
        query = f"DELETE FROM {self.TABLE} WHERE {cond} = %s"
        await self.execute(query, (cond_value,))


class UsersTable(Table):
    def __init__(
            self, host: str, user: str, password: str, database: str
    ) -> None:
        super().__init__(host, user, password, database, "users")

    # Добавляет юзера в таблицу
    async def add_user(self, user_id: int) -> None:
        try:
            query = f"INSERT INTO {self.TABLE} VALUES (%s, 0, 1)"
            await self.execute(query, (user_id,))
            await self.LOGGER.success(f"User {user_id} added successfully")

        except Exception as ex:
            await self.LOGGER.error(ex)

    # Добавляет юзера, если его нет в таблице
    async def add_user_if_not_exist(self, user_id: int) -> None:
        query = (f"INSERT INTO {self.TABLE} (id, size, attempts) "
                 f"VALUES (%s, 0, 1) ON DUPLICATE KEY UPDATE id=id")
        await self.execute(query, (user_id,))

    # ФУНКЦИИ ДЛЯ !dick

    # Изменяет размер писюна на delta см
    async def change_dick_size(self, user_id: int, delta: int) -> str:
        query = f"UPDATE {self.TABLE} SET size = size + %s WHERE id = %s"
        await self.execute(query, (delta, user_id))
        return await self.get_dick_resp(user_id, delta=delta)

    # Изменяет размер писюна на случайное число см
    async def dick_random(self, user_id: int) -> str:
        await self.add_user_if_not_exist(user_id)
        attempts = await self.get_attempts(user_id)
        if attempts > 0:
            await self.update_value("attempts", attempts - 1, "id", user_id)
            delta = randint(BotConfig.MIN_DICK_DELTA, BotConfig.MAX_DICK_DELTA)
            return await self.change_dick_size(user_id, delta)
        return await self.get_dick_resp(user_id, is_atts_were=False)

    # Возвращает текст, которым ответит бот
    async def get_dick_resp(
            self, user_id: int, delta: int = 0, is_atts_were: bool = True
    ) -> str:
        user_size: int = await self.get_dick_size(user_id)
        global_top = await self.get_global_top()
        top_place: int = self.get_place_in_top(user_id, global_top)
        attempts_resp: str = await self.get_attempts_resp(user_id)

        if is_atts_were:  # Если до вызова функции у юзера оставались попытки
            return (f"{self.get_size_change_resp(delta)}"
                    f"\nТеперь он равен {user_size} см"
                    f"\nТы занимаешь {top_place} место в глобальном топе"
                    "\n" + attempts_resp)

        else:
            return (f"{attempts_resp.lower()}"
                    f"\nСейчас твой писюн равен {user_size} см"
                    f"\nТы занимаешь {top_place} место в глобальном топе")

    # КОМАНДЫ БОТА

    # Возвращает текст с количеством попыток
    async def get_attempts_resp(self, user_id: int) -> str:
        attempts: int = await self.get_attempts(user_id)
        left_form, attempts_form = get_words_right_form(attempts)

        match attempts:
            case 0:
                return f"У тебя не осталось попыток"
            case _:
                return f"У тебя {left_form} {attempts} {attempts_form}"

    # Возвращает текст с размером писюна
    async def get_dick_size_resp(self, user_id: int) -> str:
        size: int = await self.get_dick_size(user_id)
        return f"Сейчас твой писюн имеет размер {size} см"

    # ДРУГИЕ ФУНКЦИИ

    # Возвращает количество оставшихся попыток у юзера
    async def get_attempts(self, user_id: int) -> int:
        await self.add_user_if_not_exist(user_id)
        return await self.get_value("attempts", "id", user_id)

    # Возвращает размер писюна юзера
    async def get_dick_size(self, user_id: int) -> int:
        await self.add_user_if_not_exist(user_id)
        return await self.get_value("size", "id", user_id)

    # Возвращает общий топ юзеров
    async def get_global_top(self) -> dict[int, int]:
        try:
            top_list: list[tuple[Any, ...]] = await self.get_values(
                "id, size", "size", True
            )
            return dict(top_list)

        except Exception as ex:
            await self.LOGGER.error(ex)
            return dict()

    # Возвращает обрезанный топ
    async def get_sliced_global_top(self) -> dict[int, int]:
        top = await self.get_global_top()
        return slice_dict(top, BotConfig.MAX_USERS_IN_TOP)

    # Возвращает позицию юзера в общем топе
    @staticmethod
    def get_place_in_top(user_id: int, top: dict[int, int]) -> int:
        return list(top.keys()).index(user_id) + 1 if user_id in top else -1

    # Добавляет 1 попытку всем юзерам каждый день
    async def add_attempts_coroutine(self) -> None:
        while True:
            time_delta = get_time_delta(BotConfig.ATTEMPTS_ADD_HOUR)
            await asyncio.sleep(time_delta)
            await self.add_attempts()
            await self.LOGGER.debug("Attempts added")

    async def add_attempts(self) -> None:
        query = f"UPDATE {self.TABLE} SET attempts = attempts + {BotConfig.ATTEMPTS_AMOUNT}"
        await self.execute(query)

    # Возвращает текст ответа на изменение размера писюна
    @staticmethod
    def get_size_change_resp(delta: int) -> str:
        if delta > 0:
            return f"твой писюн вырос на {delta} см"
        elif delta < 0:
            return f"твой писюн уменьшился на {abs(delta)} см"
        else:
            return f"твой писюн не изменился"


async def main():
    users = UsersTable(
        DBConfig.HOST,
        DBConfig.USER,
        DBConfig.PASSWORD,
        DBConfig.DATABASE
    )
    await users.add_attempts()


if __name__ == "__main__":
    asyncio.run(main())
