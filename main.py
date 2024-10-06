import requests
from logger import *
from random import choice
from bs4 import BeautifulSoup
from config import ConfigVars
from database import DataBase
from discord.ext import commands
from discord import Intents, Member, Message
from discord.ext.commands import Context, errors


class DickTator(commands.Bot):
    def __init__(self, command_prefix="!", intents=Intents.all()):
        super().__init__(command_prefix, intents=intents)
        self.DB = DataBase()

    # Срабатывает при запуске бота
    async def on_ready(self):
        success("Бот запущен...")
        await self.add_commands()
        await self.DB.add_attempts()

    # КОМАНДЫ

    # Добавляет команды
    async def add_commands(self) -> None:

        # Выводит информацию о боте
        @self.command(aliases=["inf", "i", "h", "info"])
        async def infa(ctx: commands.Context):
            await ctx.channel.send(ConfigVars.HELP)

        # Скидывает лицо из Stalcraft
        @self.command(aliases=["sc", "face"])
        async def stalcraft(ctx: commands.Context) -> None:
            await ctx.message.delete()
            await ctx.channel.send(ConfigVars.STALCRAFT_FACE)

        # Изменяет размер писюна на рандомное значение
        @self.command(aliases=["d", "p", "penis", "cock", "4len"])
        async def dick(ctx: commands.Context) -> None:
            user_id = ctx.author.id
            mention = ctx.author.mention
            answer = self.DB.dick_random(user_id, mention)
            await ctx.channel.send(answer)

        # Выводит топ игроков
        @self.command(aliases=["s", "t", "top", "stat", "stas"])
        async def stats(ctx: commands.Context) -> None:
            users = self.DB.get_top()
            if users:
                answer = "Топ игроков:"
                for i, user_inf in enumerate(users):
                    answer += f"\n{i + 1}. {self.get_user(user_inf[0]).display_name} — {user_inf[1]} см"
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
                await ctx.channel.send(self.DB.get_attempts(user_id, mention))
            except Exception as ex:
                await ctx.channel.send("Что-то пошло не так...")
                error(ex)

        # Выводит госдолг США
        @self.command(aliases=["gd", "nd", "usa", "us", "dolg", "debt"])
        async def gosdolg(ctx: commands.Context) -> None:
            try:
                req = requests.get(ConfigVars.US_DEBT_URL).content
                html = BeautifulSoup(req, "html.parser")
                div = html.find("div", {"class": "debt-gross"})
                debt = div.find("span").text
                await ctx.channel.send(
                    f"Госдолг США составляет {debt}"
                )
                await ctx.channel.send(ConfigVars.US_DEBT_GIF)
            except AttributeError:
                await ctx.channel.send("Произошла ошибка...")
            except Exception as ex:
                error(ex)

    # ИВЕНТЫ

    # Срабатывает на любое сообщение
    async def on_message(self, message: Message) -> None:
        # Отсеивает сообщения себя и других ботов
        if not message.author.bot:
            channel = message.channel
            # Отвечает лицом на лицо
            if ConfigVars.STALCRAFT_FACE in message.content:
                await channel.send(ConfigVars.STALCRAFT_FACE)
        await self.process_commands(message)

    # Срабатывает при обновлении активности
    async def on_presence_update(self, before: Member, after: Member) -> None:
        try:
            channel = after.guild.text_channels[0]
            for ban_act in ConfigVars.BANNED_ACT:
                # Если до этого была незапрещённая активность
                if not any(ban_act in prev_act.name.lower() for prev_act in before.activities):
                    # Если у юзера запрещённая активность
                    if any(ban_act in cur_act.name.lower() for cur_act in after.activities):
                        self.DB.add_user_if_not_exist(after.id)
                        await channel.send(
                            f"{after.mention}, {choice(ConfigVars.LEAVE_PHRASES)}"
                        )
                        answer = self.DB.change_dick_size(after.id, after.mention, ConfigVars.PENALTY)
                        await channel.send(answer)
                        inf(f"{after.display_name} наказан за {after.activity.name}")
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


def main() -> None:
    DickTator().run(ConfigVars.TOKEN, log_level=0)


if __name__ == "__main__":
    main()
