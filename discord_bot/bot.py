import sys
import discord
import asyncio
from os import listdir
from discord.ext import commands
from discord import app_commands
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_DISCORD_BOT, DISCORD_GUILD_ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
    bot.guild = await bot.fetch_guild(DISCORD_GUILD_ID)
    synced = await bot.tree.sync(guild=bot.guild)
    print(f'{bot.user} has connected to Discord!')
    print(synced)

async def setup():
    for file in listdir(f"{PATH_DISCORD_BOT}/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            print(file)
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    await setup()
    await bot.start(DISCORD_BOT_TOKEN)
    
asyncio.run(main())
