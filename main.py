import asyncio
import requests
from config import *
from random import choice
from bs4 import BeautifulSoup
from database import DataBase
from discord.ext import commands
from discord import Intents, Member, Message
from discord.ext.commands import Context, errors


class DickTator(commands.Bot):
    def __init__(self, command_prefix=Config.PREFIX, intents=Intents.all()):
        super().__init__(command_prefix, intents=intents)
        self.DB = DataBase()

    # Срабатывает при запуске бота
    async def on_ready(self):
        await self.add_commands()
        self.add_funcs_info()
        logging.info("Bot started...")
        await self.DB.add_attempts()

    # Добавляет информацию о функциях в HELP в config
    def add_funcs_info(self) -> None:
        Config.HELP += "\n\nКоманды:"
        for func in self.commands:
            name = func.name
            if not name == 'help':
                Config.HELP += f"\n{self.command_prefix}{name} - {COMMANDS.get(name)}"

        Config.HELP += "\n\nАлиасы:"
        for func in self.commands:
            name = func.name
            if not name == 'help':
                aliases = sorted(func.aliases, key=len)
                Config.HELP += f"\n{self.command_prefix}{name} - {", ".join(aliases)}"

    # КОМАНДЫ

    # Добавляет команды
    async def add_commands(self) -> None:

        # Выводит информацию о боте
        @self.command(aliases=["i", "h", "inf", "info"])
        async def infa(ctx: commands.Context):
            await ctx.channel.send(Config.HELP)

        # Скидывает лицо из Stalcraft
        @self.command(aliases=["sc", "face"])
        async def stalcraft(ctx: commands.Context) -> None:
            await ctx.message.delete()
            await ctx.channel.send(Config.STALCRAFT_FACE)

        # Изменяет размер писюна на рандомное значение
        @self.command(aliases=["d", "p", "penis", "cock", "4len"])
        async def dick(ctx: commands.Context) -> None:
            user_id = ctx.author.id
            mention = ctx.author.mention
            await ctx.channel.send(self.DB.dick_random(user_id, mention))

        # Выводит топ игроков
        @self.command(aliases=["s", "t", "top", "stat", "stas"])
        async def stats(ctx: commands.Context) -> None:
            users = self.DB.get_top()
            if users:
                resp = "Топ игроков:"
                for i, user_inf in enumerate(users):
                    resp += f"\n{i + 1}. {self.get_user(user_inf[0]).display_name} — {user_inf[1]} см"
            else:
                resp = "Похоже топ пустой..."
            await ctx.channel.send(resp)

        # Выводит количество оставшихся попыток
        @self.command(aliases=["a", "att", "atts", "try", "tries"])
        async def attempts(ctx: commands.Context) -> None:
            try:
                user_id = ctx.author.id
                mention = ctx.author.mention
                await ctx.channel.send(f"{mention}, {self.DB.get_attempts(user_id).lower()}")
            except Exception:
                await ctx.channel.send("Что-то пошло не так...")

        # Выводит госдолг США
        @self.command(aliases=["gd", "nd", "usa", "us", "dolg", "debt"])
        async def gosdolg(ctx: commands.Context) -> None:
            try:
                req = requests.get(Config.US_DEBT_URL).content
                html = BeautifulSoup(req, "html.parser")
                div = html.find("div", {"class": "debt-gross"})
                debt = div.find("span").text
                await ctx.channel.send(
                    f"Госдолг США составляет {debt}"
                )
                logging.info("Got US Government Debt")
                await ctx.channel.send(Config.US_DEBT_GIF)
            except AttributeError as ex:
                logging.warning(ex)
                await ctx.channel.send("Произошла ошибка...")
            except Exception as ex:
                logging.error(ex)

    # ИВЕНТЫ

    # Срабатывает на любое сообщение
    async def on_message(self, message: Message) -> None:
        # Отсеивает сообщения себя и других ботов
        if not message.author.bot:
            channel = message.channel
            # Отвечает лицом на лицо
            if Config.STALCRAFT_FACE in message.content:
                await channel.send(Config.STALCRAFT_FACE)
        await self.process_commands(message)

    # Срабатывает при обновлении активности
    async def on_presence_update(self, before: Member, after: Member) -> None:
        try:
            channel = after.guild.text_channels[0]
            for ban_act in Config.BANNED_ACT:
                # Если до этого была незапрещённая активность
                if not any(ban_act in prev_act.name.lower() for prev_act in before.activities):
                    # Если у юзера запрещённая активность
                    for cur_act in after.activities:
                        if ban_act in cur_act.name.lower():
                            self.DB.add_user_if_not_exist(after.id)
                            await channel.send(
                                f"{after.mention}, {choice(Config.LEAVE_PHRASES)}"
                            )
                            resp = self.DB.change_dick_size(
                                after.id, after.mention, Config.PENALTY
                            )
                            await channel.send(resp)
                            logging.info(f"{after.display_name} was punished for {cur_act.name}")
        except Exception as ex:
            logging.error(ex)

    # Отлавливает ошибки команд
    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        if isinstance(exception, errors.CommandNotFound):
            await context.channel.send(
                f"{context.author.mention}, такой команды не существует..."
            )


async def main() -> None:
    await DickTator().start(Config.TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot disabled...")
    except Exception as exc:
        logging.error(exc)
