import asyncio
import requests
from config import *
from random import choice
from database import Users
from typing import Sequence
from discord import TextChannel
from discord.ext import commands
from bs4 import BeautifulSoup as BS, Tag
from discord import Intents, Member, Message
from discord.ext.commands import Context, Command, errors


class DickTator(commands.Bot):
    def __init__(self):
        super().__init__(
            help_command=None,
            intents=Intents.all(),
            command_prefix=Config.PREFIX,
        )
        self.USERS = Users(
            Config.HOST,
            Config.USER,
            Config.PASSWORD,
            Config.DATABASE
        )

    # Срабатывает при запуске бота
    async def on_ready(self):
        await self.add_commands()
        self.add_funcs_info()
        logging.info("Bot started...")
        await self.USERS.add_attempts_coroutine()

    # Добавляет информацию о функциях в HELP_RESPONSE в config
    def add_funcs_info(self) -> None:
        commands_list: list = list()
        aliases_list: list = list()
        bot_commands: list[Command] = sorted(
            self.commands, key=lambda f: len(f.name)
        )

        for func in bot_commands:
            command_str: str = f"\n{self.command_prefix}{func.name} - {func.help}"
            commands_list.append(command_str)
            aliases: list[str] = sorted(func.aliases, key=len)

            if not aliases:
                continue

            alias_str = f"\n{self.command_prefix}{func.name} - {", ".join(aliases)}"
            aliases_list.append(alias_str)

        Config.HELP_RESPONSE += ("\n\n**Команды:**"
                                 + str().join(commands_list)
                                 + "\n\n**Алиасы:**"
                                 + str().join(aliases_list))

    # КОМАНДЫ

    # Добавляет команды
    async def add_commands(self) -> None:

        # Выводит информацию о боте
        @self.command(
            aliases=["i", "h", "inf", "info", "infa"],
            help="Выводит это сообщение"
        )
        async def help(ctx: commands.Context):
            await ctx.channel.send(Config.HELP_RESPONSE)

        # Скидывает лицо из Stalcraft
        @self.command(
            aliases=["sc", "face"],
            help="Скидывает Gif с лицом из Stalcraft"
        )
        async def stalcraft(ctx: commands.Context) -> None:
            await ctx.message.delete()
            await ctx.channel.send(Config.STALCRAFT_FACE)

        # Изменяет размер писюна на рандомное значение
        @self.command(
            aliases=["d", "penis", "cock", "4len"],
            help="Изменяет размер писюна"
        )
        async def dick(ctx: commands.Context) -> None:
            user_id: int = ctx.author.id
            mention: str = ctx.author.mention
            resp: str = self.USERS.dick_random(user_id)
            await ctx.channel.send(f"{mention}, {resp}")

        # Выводит топ писюнов сервера
        @self.command(
            aliases=["s", "t", "stats", "stat", "stas"],
            help="Выводит топ писюнов сервера"
        )
        async def top(ctx: commands.Context) -> None:
            members: Sequence[Member] = ctx.guild.members
            local_top = self.get_sliced_local_top(members)
            resp = self.get_top_resp(ctx, local_top)
            await ctx.channel.send(resp)

        # Выводит глобальный топ писюнов
        @self.command(
            aliases=["gs", "gt", "gstats", "gstat", "gstas"],
            help="Выводит глобальный топ писюнов"
        )
        async def gtop(ctx: commands.Context) -> None:
            global_top: dict[int, int] = self.USERS.get_sliced_global_top()
            resp = self.get_top_resp(ctx, global_top, True)
            await ctx.channel.send(resp)

        # Выводит место в топе сервера
        @self.command(
            aliases=["p", "n", "num", "number"],
            help="Выводит место в топе сервера"
        )
        async def place(ctx: commands.Context) -> None:
            members: Sequence[Member] = ctx.guild.members
            local_top = self.get_local_top(members)
            resp = self.get_place_resp(ctx, local_top)
            await ctx.channel.send(resp)

        # Выводит место в глобальном топе
        @self.command(
            aliases=["gp", "gn", "gnum", "gnumber"],
            help="Выводит место в глобальном топе"
        )
        async def gplace(ctx: commands.Context) -> None:
            global_top = self.USERS.get_global_top()
            resp = self.get_place_resp(ctx, global_top, True)
            await ctx.channel.send(resp)

        # Выводит количество оставшихся попыток
        @self.command(
            aliases=["a", "att", "atts", "try", "tries"],
            help="Выводит количество оставшихся попыток"
        )
        async def attempts(ctx: commands.Context) -> None:
            try:
                user_id: int = ctx.author.id
                mention: str = ctx.author.mention
                attempts_resp: str = self.USERS.get_attempts_resp(user_id)
                await ctx.channel.send(f"{mention}, {attempts_resp.lower()}")

            except Exception:
                await ctx.channel.send("Что-то пошло не так...")

        # Выводит госдолг США
        @self.command(
            aliases=["gd", "nd", "usa", "us", "dolg", "debt"],
            help="Выводит госдолг США"
        )
        async def gosdolg(ctx: commands.Context) -> None:
            try:
                req: bytes = requests.get(Config.US_DEBT_URL).content
                html: BS = BS(req, "html.parser")
                el: Tag = html.find("span", {"class": "debt-number"})
                debt: str = el.text
                await ctx.channel.send(
                    f"Госдолг США составляет ${debt}"
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
        if message.author.bot:
            return

        # Отвечает лицом на лицо
        if Config.STALCRAFT_FACE in message.content:
            await message.channel.send(Config.STALCRAFT_FACE)
            return

        await self.process_commands(message)

    async def on_presence_update(self, before: Member, after: Member) -> None:
        try:
            channel: TextChannel = after.guild.text_channels[0]

            for ban_act in Config.BANNED_ACTIVITIES:

                # Если до этого была запрещённая активность
                if any(ban_act in prev_act.name.lower() for prev_act in before.activities):
                    continue

                for cur_act in after.activities:

                    if not ban_act in cur_act.name.lower():
                        continue

                    self.USERS.add_user_if_not_exist(after.id)
                    await channel.send(
                        f"{after.mention}, {choice(Config.LEAVE_PHRASES)}"
                    )
                    resp: str = self.USERS.change_dick_size(after.id, Config.FINE)
                    await channel.send(f"{after.mention}, {resp}")
                    logging.info(f"{after.display_name} was punished for {cur_act.name}")

        except Exception as ex:
            logging.error(ex)

    # Отлавливает ошибки команд
    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        if isinstance(exception, errors.CommandNotFound):
            await context.channel.send(
                f"{context.author.mention}, такой команды не существует..."
            )

    # ДРУГИЕ ФУНКЦИИ

    def get_top_resp(self, ctx: Context, users_top: dict[int, int], is_global: bool = False) -> str:
        if not users_top:  # Если топ пустой
            return "Похоже топ пустой..."

        if not is_global:
            if len(users_top.keys()) < Config.MAX_USERS_IN_TOP:
                resp: str = f"**Топ писюнов сервера:**"
            else:
                resp: str = f"**Топ {Config.MAX_USERS_IN_TOP} писюнов сервера:**"

        else:
            resp = f"**Топ {Config.MAX_USERS_IN_TOP} писюнов:**"

        for i, user_id in enumerate(users_top):

            if is_global:
                user_name: str = self.get_user(user_id).display_name
            else:
                user_name: str = ctx.guild.get_member(user_id).display_name

            user_size: int = users_top.get(user_id)
            resp += f"\n{i + 1}. {user_name} — {user_size} см"

        return resp

    # Возвращает текст с местом в топе
    def get_place_resp(
            self, ctx: Context, users_top: dict[int, int], is_global: bool = False
    ) -> str:
        try:
            user_id: int = ctx.author.id
            mention: str = ctx.author.mention
            place_in_top: int = self.USERS.get_place_in_top(user_id, users_top)

            if is_global:
                return f"{mention}, ты занимаешь {place_in_top} место в глобальном топе"
            else:
                return f"{mention}, ты занимаешь {place_in_top} место в топе сервера"

        except Exception:
            return "Что-то пошло не так..."

    # Возвращает топ сервера
    def get_local_top(self, members: Sequence[Member]) -> dict[int, int]:
        global_top: dict[int, int] = self.USERS.get_global_top()
        top_ids = global_top.keys()
        members_ids: list[int] = [member.id for member in members]
        common_ids: list[int] = list(filter(lambda x: x in members_ids, top_ids))
        return {user_id: global_top.get(user_id) for user_id in common_ids}

    def get_sliced_local_top(self, members: Sequence[Member]) -> dict[int, int]:
        local_top = self.get_local_top(members)
        return self.USERS.slice_dict(local_top, Config.MAX_USERS_IN_TOP)


async def main() -> None:
    await DickTator().start(Config.TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logging.info("Bot disabled...")

    except Exception as exc:
        logging.error(exc)
