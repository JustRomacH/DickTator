from config import *
from database import *
from logger import error
from random import choice
from discord.ext import commands
from discord import Intents, Member

bot = commands.Bot(command_prefix='/', intents=Intents.all())
db = DataBase()


@bot.command()
async def infa(ctx: commands.Context):
    await ctx.channel.send(HELP)


@bot.command()
async def dick(ctx: commands.Context):
    user_id = ctx.author.id
    mention = ctx.author.mention
    answer = db.dick_db(user_id, mention)
    await ctx.channel.send(answer)


@bot.command()
async def top(ctx: commands.Context):
    users = db.get_top()
    if users:
        answer = "Топ игроков:"
        for i, user in enumerate(users):
            answer += f"\n{i + 1}. {bot.get_user(user[0]).name.capitalize()} - {user[1]} см"
    else:
        answer = "Похоже топ пустой..."
    await ctx.channel.send(answer)


@bot.event
async def on_ready():
    db.subtractAttempts()
    db.add_attempts()


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
