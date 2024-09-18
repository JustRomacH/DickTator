import timer
import asyncio
from config import *
from database import *
from logger import error
from random import choice
from discord.ext import commands
from discord import Intents, Member, Message, RawReactionActionEvent

bot = commands.Bot(command_prefix='!', intents=Intents.all())
db = DataBase()


@bot.event
async def on_ready():
    db.subtract_attempts()
    db.add_attempts()
    await send_gena()


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
        answer = "Похоже топ пустой..."
    await ctx.channel.send(answer)


async def send_gena():
    channel = bot.get_channel(747847558239486085)
    delta_time = timer.randomTime()
    while True:
        await asyncio.sleep(delta_time)
        await channel.send(GENA)


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
        if STALCRAFT_FACE in message.content:
            await message.channel.send(STALCRAFT_FACE)
    await bot.process_commands(message)


@bot.event
async def on_presence_update(before: Member, after: Member):
    try:
        text_channel = after.guild.text_channels[0]
        user_id = after.id
        cur_act = after.activity.name.lower()
        if any(ban_act in cur_act for ban_act in BANNED_ACT):
            await text_channel.send(f"{after.mention} {choice(LEAVE_PHRASES)}")
            answer = db.change_size(user_id, -1, mention=after.mention)
            await text_channel.send(answer)
    except AttributeError:
        pass
    except Exception as ex:
        error(ex)


bot.run(TOKEN)
