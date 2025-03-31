import re
import asyncio
import aiohttp
import discord
from utils import *
from config import *
from logger import Logger
from random import choice
from typing import Sequence
from database import UsersTable
from discord.ext import commands
from bs4 import BeautifulSoup as BS, Tag
from discord.ext.commands import Context, errors
from discord import Intents, Member, User, Message, TextChannel, Embed


class DickTator(commands.Bot):
    def __init__(self):
        self.LOGGER = Logger()
        super().__init__(
            help_command=None,
            intents=Intents.all(),
            command_prefix=BotConfig.PREFIX,
        )
        self.commands_list: list = list()
        self.aliases_list: list = list()
        self.processed_activities: {int: set} = dict()
        self.USERS = UsersTable(
            DBConfig.HOST,
            DBConfig.USER,
            DBConfig.PASSWORD,
            DBConfig.DATABASE,
        )

    # Срабатывает при запуске бота
    async def on_ready(self):
        await self.USERS.connect()
        await self.add_commands()
        await self.add_funcs_info()
        await self.LOGGER.success("Bot started")
        await self.USERS.add_attempts_coroutine()

    # Добавляет информацию о функциях в HELP_RESPONSE в config
    async def add_funcs_info(self) -> None:
        await self.LOGGER.debug("Adding functions info...")
        bot_commands = sorted(self.commands, key=lambda f: len(f.name))

        for func in bot_commands:
            command_str = f"\n{self.command_prefix}{func.name} - {func.help}."
            self.commands_list.append(command_str)
            aliases = sorted(func.aliases, key=len)

            if aliases:
                alias_str = f"\n{self.command_prefix}{func.name} - {", ".join(aliases)}"
                self.aliases_list.append(alias_str)

        await self.LOGGER.debug("Functions info added")

    # КОМАНДЫ

    # Добавляет команды
    async def add_commands(self) -> None:
        await self.LOGGER.debug("Adding commands...")

        @self.command(aliases=["i", "h", "inf", "info", "infa"], help="Выводит это сообщение")
        async def help(ctx: commands.Context):
            embed = Embed(
                title="Общая информация:",
                description=BotConfig.HELP_RESPONSE,
                color=ctx.me.color
            )
            embed.add_field(
                name="Команды:",
                value=str().join(self.commands_list)
            )
            embed.add_field(
                name="Алиасы:",
                value=str().join(self.aliases_list)
            )
            await ctx.channel.send(embed=embed)

        await self.LOGGER.success("Commands added")

        # Изменяет размер писюна на рандомное значение
        @commands.cooldown(1, 1, commands.BucketType.user)
        @self.command(
            aliases=["d", "penis", "cock", "4len"],
            help="Изменяет размер писюна, используя указанное количество попыток"
        )
        async def dick(ctx: commands.Context, atts: int = 1) -> None:
            resp: str = await self.USERS.dick_random(ctx.author.id, atts)
            embed = Embed(
                description=bold(f"{ctx.author.mention}, {lower_first(resp)}"),
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Изменяет размер писюна на рандомное значение
        @commands.cooldown(1, 1, commands.BucketType.user)
        @self.command(
            aliases=["da", "df", "allin", "all", "full"],
            help="Использует все попытки для !dick"
        )
        async def dickall(ctx: commands.Context) -> None:
            atts: int = await self.USERS.get_attempts(ctx.author.id)
            resp: str = await self.USERS.dick_random(ctx.author.id, atts)
            embed = Embed(
                description=bold(f"{ctx.author.mention}, {lower_first(resp)}"),
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Выводит топ писюнов сервера
        @self.command(
            aliases=["t", "stats", "stat", "stas"],
            help="Выводит топ писюнов сервера"
        )
        async def top(ctx: commands.Context) -> None:
            members: Sequence[Member] = ctx.guild.members
            local_top = await self.get_sliced_local_top(members)

            if not local_top:
                await ctx.channel.send("Похоже топ пустой...")

            title, users_top = self.get_local_top_resp(ctx, local_top)
            embed = Embed(
                title=title,
                description=users_top,
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Выводит глобальный топ писюнов
        @self.command(
            aliases=["gs", "gt", "gstats", "gstat", "gstas"],
            help="Выводит глобальный топ писюнов"
        )
        async def gtop(ctx: commands.Context) -> None:
            global_top: dict[int, int] = await self.USERS.get_sliced_global_top()

            if not global_top:
                await ctx.channel.send("Похоже топ пустой...")

            title, users_top = await self.get_global_top_resp(global_top)
            embed = Embed(
                title=title,
                description=users_top,
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Выводит место в топе сервера
        @self.command(
            aliases=["p", "n", "num", "number", "spot", "place"],
            help="Выводит место в топе сервера"
        )
        async def pos(ctx: commands.Context) -> None:
            members: Sequence[Member] = ctx.guild.members
            local_top = await self.get_local_top(members)
            resp: str = self.get_pos_resp(ctx, local_top)
            embed = Embed(
                description=big(resp),
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Выводит место в глобальном топе
        @self.command(
            aliases=["gp", "gn", "gnum", "gnumber", "gspot", "gplace"],
            help="Выводит место в глобальном топе"
        )
        async def gpos(ctx: commands.Context) -> None:
            global_top = await self.USERS.get_global_top()
            resp: str = self.get_pos_resp(ctx, global_top, True)
            embed = Embed(
                description=big(resp),
                color=ctx.me.color
            )
            await ctx.channel.send(embed=embed)

        # Выводит количество оставшихся попыток
        @self.command(
            aliases=["a", "att", "atts", "try", "tries"],
            help="Выводит количество оставшихся попыток"
        )
        async def attempts(ctx: commands.Context) -> None:
            try:
                user_id: int = ctx.author.id
                mention: str = ctx.author.mention
                resp: str = await self.USERS.get_attempts_resp(user_id)
                embed = Embed(
                    description=big(f"{mention}, {resp.lower()}"),
                    color=ctx.me.color
                )
                await ctx.channel.send(embed=embed)

            except Exception as ex:
                await self.LOGGER.error(ex)
                await ctx.channel.send("Что-то пошло не так...")

        # Выводит размер писюна
        @self.command(
            aliases=["s"],
            help="Выводит размер писюна"
        )
        async def size(ctx: commands.Context) -> None:
            try:
                user_id: int = ctx.author.id
                mention: str = ctx.author.mention
                resp: str = await self.USERS.get_dick_size_resp(user_id)
                embed = Embed(
                    description=big(f"{mention}, {resp.lower()}"),
                    color=ctx.me.color
                )
                await ctx.channel.send(embed=embed)

            except Exception as ex:
                await ctx.channel.send("Что-то пошло не так...")
                await self.LOGGER.error(ex)

        # Выводит госдолг США
        @self.command(
            aliases=["gd", "nd", "usa", "us", "dolg", "debt"],
            help="Выводит госдолг США"
        )
        async def gosdolg(ctx: commands.Context) -> None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(BotConfig.US_DEBT_URL) as resp:
                        req = await resp.read()

                html: BS = BS(req, "html.parser")
                el: Tag = html.find("span", {"class": "debt-number"})
                debt: str = el.text
                await self.LOGGER.debug("Got US Government Debt")
                
                embed = Embed(
                    title=f"Госдолг США составляет ${debt}",
                    color=ctx.me.color
                )
                with open("static/us-debt.gif", "rb") as f:
                    file = discord.File(f, filename="us-debt.gif")
                    embed.set_image(url="attachment://us-debt.gif")

                await ctx.channel.send(embed=embed, file=file)

            except AttributeError as ex:
                await self.LOGGER.warning(ex)
                await ctx.channel.send("Произошла ошибка...")

            except Exception as ex:
                await self.LOGGER.error(ex)

    # ИВЕНТЫ

    # Срабатывает на любое сообщение
    async def on_message(self, message: Message) -> None:
        # Отсеивает сообщения себя и других ботов
        if message.author.bot:
            return

        if any(
                re.search(rf"\b{word}\b", message.content.split('http')[0], re.IGNORECASE)
                for word in ("sieg", "зиг", "сиг")
        ):
            await message.reply("Heil!")
            return

        await self.process_commands(message)

    async def on_presence_update(self, before: Member, after: Member) -> None:
        try:
            self.processed_activities.setdefault(after.id, set())

            # Получаем множества активностей до и после
            before_activities = {act.name.lower() for act in before.activities if act.name}
            after_activities = {act.name.lower() for act in after.activities if act.name}
            new_activities = after_activities - before_activities

            # Находим новые запрещенные активности
            new_banned_activities = {
                activity for activity in new_activities
                if any(
                    banned_activity in activity for banned_activity in BotConfig().BANNED_ACTIVITIES
                )
            }

            if not new_banned_activities:
                return

            for cur_act in after.activities:
                act_name = cur_act.name.lower()

                if act_name not in new_banned_activities:
                    continue

                start_time = cur_act.timestamps.get("start")
                activity_key = (act_name, start_time)

                if activity_key in self.processed_activities[after.id]:
                    continue

                # Добавляем активность в список обработанных
                self.processed_activities[after.id].add(activity_key)

                resp: str = await self.USERS.change_dick_size(after.id, BotConfig.FINE)

                embed = Embed(
                    description=bold(
                        f"{after.mention}, {choice(BotConfig.LEAVE_PHRASES)}\n{resp}"
                    ),
                    color=BotConfig.RED_COLOR
                )

                for guild in self.guilds:

                    if after not in guild.members:
                        continue

                    channel: TextChannel = guild.system_channel or guild.text_channels[0]
                    await channel.send(embed=embed)

                await self.LOGGER.debug(f"{after.display_name} was punished for {cur_act.name}")

        except Exception as ex:
            await self.LOGGER.error(ex)

    # Отлавливает ошибки команд
    async def on_command_error(self, ctx: Context, ex: errors.CommandError) -> None:
        if isinstance(ex, errors.CommandNotFound):
            await self.LOGGER.warning(
                f"Unknown command used by {ctx.author}: {ctx.message.content}"
            )
            await ctx.channel.send(
                f"{ctx.author.mention}, такой команды не существует..."
            )

        elif isinstance(ex, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, подожди ещё {ex.retry_after:.1f} сек")

        elif isinstance(ex, errors.BadArgument):
            await ctx.channel.send(
                f"{ctx.author.mention}, ты ввёл что-то не то..."
            )

        else:
            await self.LOGGER.error(ex)

    # ДРУГИЕ ФУНКЦИИ

    def get_local_top_resp(self, ctx: Context, users_top: dict[int, int]) -> tuple[str, str]:
        if len(users_top.keys()) < BotConfig.MAX_USERS_IN_TOP:
            title: str = f"Топ писюнов сервера:"
        else:
            title: str = f"Топ {BotConfig.MAX_USERS_IN_TOP} писюнов сервера:"

        top: str = str()

        for i, user_id in enumerate(users_top):
            try:
                user: Member = ctx.guild.get_member(user_id)
                user_name = user.display_name
                user_size: int = users_top.get(user_id)
                top += f"\n{i + 1}. **{user_name} — {user_size} см**"

            except Exception as ex:
                self.LOGGER.error(ex)
                continue

        return title, top

    async def get_global_top_resp(self, users_top: dict[int, int]) -> tuple[str, str]:
        if len(users_top.keys()) < BotConfig.MAX_USERS_IN_TOP:
            title: str = f"Топ писюнов:"
        else:
            title: str = f"Топ {BotConfig.MAX_USERS_IN_TOP} писюнов:"

        top: str = str()

        for i, user_id in enumerate(users_top):
            try:
                user: User = self.get_user(user_id)

                user_name: str = user.display_name
                user_size: int = users_top.get(user_id)
                top += f"\n{i + 1}. **{user_name} — {user_size} см**"

            except AttributeError as ex:
                await self.LOGGER.error(ex)
                await self.USERS.remove_string("id", user_id)

            except Exception as ex:
                await self.LOGGER.error(ex)

        return title, top

    # Возвращает текст с местом в топе
    def get_pos_resp(
            self, ctx: Context, users_top: dict[int, int], is_global: bool = False
    ) -> str:
        try:
            user_id: int = ctx.author.id
            mention: str = ctx.author.mention
            pos: int = self.USERS.get_pos_in_top(user_id, users_top)

            if pos == -1:
                return f"{mention}, тебя пока нет в топе..."

            if is_global:
                return f"{mention}, ты занимаешь {pos} место в глобальном топе"
            else:
                return f"{mention}, ты занимаешь {pos} место в топе сервера"

        except Exception as ex:
            self.LOGGER.error(ex)
            return "Что-то пошло не так..."

    # Возвращает топ сервера
    async def get_local_top(self, members: Sequence[Member]) -> dict[int, int]:
        global_top: dict[int, int] = await self.USERS.get_global_top()
        top_ids = global_top.keys()
        members_ids: list[int] = [member.id for member in members]
        common_ids: list[int] = list(filter(lambda x: x in members_ids, top_ids))
        return {user_id: global_top.get(user_id) for user_id in common_ids}

    async def get_sliced_local_top(self, members: Sequence[Member]) -> dict[int, int]:
        local_top = await self.get_local_top(members)
        return slice_dict(local_top, BotConfig.MAX_USERS_IN_TOP)


async def main() -> None:
    logger = Logger(output=True)

    try:
        await logger.debug("Bot is starting...")
        await DickTator().start(BotConfig.TOKEN)

    except KeyboardInterrupt:
        await logger.debug("Bot disabled...")

    except Exception as exc:
        await logger.error(exc)


if __name__ == "__main__":
    asyncio.run(main())
