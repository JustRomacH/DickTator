import timer
import asyncio
from config import *
from database import *
from random import choice
from threading import Timer
from discord.ext import commands
from discord import Intents, Member, Message, RawReactionActionEvent

bot = commands.Bot(command_prefix='!', intents=Intents.all())
db = DataBase()


@bot.event
async def on_ready():
    success("Бот запущен...")
    db.subtract_attempts()
    db.add_attempts()
    await send_gena()


async def send_gena():
    channel = bot.get_channel(747847558239486085)
    while True:
        delta_time = timer.randomTime()
        inf(f"Гена в {timer.convertTime(delta_time)}")
        await asyncio.sleep(delta_time)
        await channel.send(GENA)


@bot.command()
async def auto(ctx: commands.Context, *args):
    try:
        user_id = ctx.author.id
        if BotVars.auto_mode and args[0] == "off":
            if BotVars.last_user == user_id:
                BotVars.auto_mode = False
                answer = "Режим AUTO GIF выключен"
                inf(answer)
            else:
                user_name = bot.get_user(BotVars.last_user).display_name
                answer = f"""Выключить AUTO GIF сейчас может только {user_name}"""
        else:
            match args[0]:
                case "on":
                    BotVars.auto_mode = True
                    answer = "Режим AUTO GIF включен"
                    BotVars.last_user = user_id
                    inf(answer)
                    time = 30 * 60
                    Timer(time, disable_auto_mode).start()
                case "off":
                    answer = "Режим AUTO GIF и так выключен"
                case _:
                    answer = "Неверный аргумент..."
        await ctx.channel.send(answer)
    except IndexError:
        pass
    except Exception as ex:
        error(ex)


def is_gif(content: str):
    attrs = ("tenor", "gif")
    if any(attr in content for attr in attrs):
        return True
    else:
        return False


def disable_auto_mode() -> None:
    if BotVars.auto_mode:
        BotVars.auto_mode = False
        BotVars.last_user = int()
        inf("Режим AUTO GIF был автоматически выключен")


@bot.command(aliases=["sc", "face"])
async def stalcraft(ctx: commands.Context):
    await ctx.message.delete()
    await ctx.channel.send(STALCRAFT_FACE)


@bot.command(aliases=["f", "t", "talk", "talking"])
async def furry(ctx: commands.Context):
    await ctx.message.delete()
    await ctx.channel.send(choice(FURRY_GIFS))


@bot.command(aliases=["inf", "i", "h", "info"])
async def infa(ctx: commands.Context):
    await ctx.channel.send(HELP)


@bot.command(aliases=["d", "p", "penis"])
async def dick(ctx: commands.Context):
    user_id = ctx.author.id
    mention = ctx.author.mention
    answer = db.dick_db(user_id, mention)
    await ctx.channel.send(answer)


@bot.command(aliases=["top", "stat"])
async def stats(ctx: commands.Context):
    users = db.get_top()
    if users:
        answer = "Топ игроков:"
        for i, user in enumerate(users):
            answer += f"\n{i + 1}. {bot.get_user(user[0]).display_name} - {user[1]} см"
    else:
        warning("Похоже топ пустой...")
        answer = "Похоже топ пустой..."
    await ctx.channel.send(answer)


@bot.command(aliases=["a", "att", "atts", "try", "tries"])
async def attempts(ctx: commands.Context):
    try:
        user_id = ctx.author.id
        mention = ctx.author.mention
        atts = db.get_value("attempts", "id", user_id)
        answer = f"{mention}, у тебя осталось {atts} попыт{get_ending(atts)}"
        await ctx.channel.send(answer)
    except Exception as ex:
        await ctx.channel.send("Что-то пошло не так...")
        error(ex)


def get_ending(num: int | float) -> str:
    if num == 1:
        return "ка"
    elif num in (2, 3, 4):
        return "ки"
    else:
        return "ок"


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    msg_id = payload.message_id
    user_id = payload.user_id
    emoji = payload.emoji
    channel = bot.get_channel(payload.channel_id)
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(user_id)
    msg = await channel.fetch_message(msg_id)
    if emoji.name in EMOJIS:
        await msg.remove_reaction(emoji, member)
        await channel.send(choice(FURRY_GIFS))


@bot.event
async def on_message(message: Message):
    if not message.author.bot:
        content = message.content
        channel = message.channel
        if STALCRAFT_FACE in content:
            await channel.send(STALCRAFT_FACE)
        elif BotVars.auto_mode and (is_gif(content) or message.attachments):
            await channel.send(choice(FURRY_GIFS))
    await bot.process_commands(message)


@bot.event
async def on_presence_update(before: Member, after: Member):
    try:
        penalty = -3
        text_channel = after.guild.text_channels[0]
        user_id = after.id
        cur_act = after.activity.name.lower()
        prev_act = before.activity.name.lower()
        if not any(ban_act in prev_act for ban_act in BANNED_ACT):
            if any(ban_act in cur_act for ban_act in BANNED_ACT):
                await text_channel.send(f"{after.mention} {choice(LEAVE_PHRASES)}")
                answer = db.change_size(user_id, penalty, mention=after.mention)
                await text_channel.send(answer)
    except AttributeError:
        pass
    except Exception as ex:
        error(ex)


bot.run(TOKEN, log_level=0)
