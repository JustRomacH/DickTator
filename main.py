import timer
import asyncio
from config import *
from logger import *
from random import choice
from database import DataBase
from discord.ext import commands
from discord import Intents, Member, Message
from discord.ext.commands import Context, errors


class DickTator(commands.Bot):
    def __init__(self, command_prefix="!", intents=Intents.all()):
        super().__init__(command_prefix, intents=intents)
        self.DB = DataBase()
        self.BULL_TEXT = self.get_channel(747847558239486085)

    # Срабатывает при запуске бота
    async def on_ready(self):
        success("Бот запущен...")
        await self.add_commands()
        self.DB.subtract_attempts()
        self.DB.add_attempts()
        await self.send_gena()

    # КОМАНДЫ

    # Добавляет команды
    async def add_commands(self) -> None:

        # Выводит информацию о боте
        @self.command(aliases=["inf", "i", "h", "info"])
        async def infa(ctx: commands.Context):
            await ctx.channel.send(HELP)

        # Скидывает лицо из Stalcraft
        @self.command(aliases=["sc", "face"])
        async def stalcraft(ctx: commands.Context) -> None:
            await ctx.message.delete()
            await ctx.channel.send(STALCRAFT_FACE)

        # Изменяет размер писюна на рандомное значение
        @self.command(aliases=["d", "p", "penis"])
        async def dick(ctx: commands.Context) -> None:
            user_id = ctx.author.id
            mention = ctx.author.mention
            answer = self.DB.dick_db(user_id, mention)
            await ctx.channel.send(answer)

        # Выводит топ игроков
        @self.command(aliases=["s", "t", "top", "stat"])
        async def stats(ctx: commands.Context) -> None:
            users = self.DB.get_top()
            if users:
                answer = "Топ игроков:"
                for i, user in enumerate(users):
                    answer += f"\n{i + 1}. {self.get_user(user[0]).display_name} - {user[1]} см"
            else:
                answer = "Похоже топ пустой..."
                warning(answer)
            await ctx.channel.send(answer)

        # Выводит количество оставшихся попыток
        @self.command(aliases=["a", "att", "atts", "try", "tries"])
        async def attempts(ctx: commands.Context) -> None:
            try:
                user_id = ctx.author.id
                mention = ctx.author.mention
                atts = self.DB.get_value("attempts", user_id)
                answer = f"{mention}, у тебя осталось {atts} {self.get_atts_ending(atts)}"
                await ctx.channel.send(answer)
            except Exception as ex:
                await ctx.channel.send("Что-то пошло не так...")
                error(ex)

    # ИВЕНТЫ

    # Срабатывает на любое сообщение
    async def on_message(self, message: Message) -> None:
        # Отсеивает сообщения себя и других ботов
        if not message.author.bot:
            channel = message.channel
            # Отвечает лицом на лицо
            if STALCRAFT_FACE in message.content:
                await channel.send(STALCRAFT_FACE)
        await self.process_commands(message)

    # Срабатывает при обновлении активности
    async def on_presence_update(self, after: Member) -> None:
        try:
            user_id = after.id
            cur_act = after.activity.name.lower()
            # Если у юзера запрещённая активность
            if any(ban_act in cur_act for ban_act in BANNED_ACT):
                await self.BULL_TEXT.send(f"{after.mention} {choice(LEAVE_PHRASES)}")
                answer = self.DB.change_size(user_id, BotVars.PENALTY, mention=after.mention)
                await self.BULL_TEXT.send(answer)
        except AttributeError:
            pass
        except Exception as ex:
            error(ex)

    # Отлавливает ошибки команд
    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        if isinstance(exception, errors.CommandNotFound):
            await context.channel.send(
                f"{context.author.mention}, такой команды не существует..."
            )
        else:
            error(exception)

    # ФУНКЦИИ

    # Скидывает гену с яблоком раз в рандомное время
    async def send_gena(self) -> None:
        while True:
            delta_time = timer.randomTime(BotVars.GENA_MIN_HOURS, BotVars.GENA_MAX_HOURS)
            inf(f"Гена в {timer.convertTime(delta_time)}")
            await asyncio.sleep(delta_time)
            await self.BULL_TEXT.send(GENA)

    @staticmethod
    # Проверяет, есть ли GIF в сообщении
    def is_gif(content: str) -> bool:
        attrs = ("tenor", "gif")
        if any(attr in content for attr in attrs):
            return True
        else:
            return False

    @staticmethod
    # Возвращает "попытка" с правильным окончанием
    def get_atts_ending(num: int | float) -> str:
        if num == 1:
            return "попытка"
        elif num in (2, 3, 4):
            return "попытки"
        else:
            return "попыток"


def main() -> None:
    bot = DickTator()
    bot.run(TOKEN, log_level=0)


if __name__ == "__main__":
    main()
