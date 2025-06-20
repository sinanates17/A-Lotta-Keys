import sys
import discord
import asyncio
from os import listdir
from discord.ext import commands
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_DISCORD_BOT

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong!")

async def load_extensions():
    for file in listdir(f"{PATH_DISCORD_BOT}/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            print(file)
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    await load_extensions()
    await bot.start(DISCORD_BOT_TOKEN)

asyncio.run(main())

#https://discord.com/oauth2/authorize?client_id=1373138929573691443&scope=bot&permissions=8
