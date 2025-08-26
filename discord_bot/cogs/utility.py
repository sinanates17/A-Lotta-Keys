import sys
import json
import discord
import aiohttp
import uuid
import asyncio
import random
import requests
from discord import app_commands
from textwrap import dedent
from os import listdir
from discord.ext import commands, tasks
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_USERS, PATH_DATA, SERVER, DISCORD_GUILD_ID
from utils import Helper
from datetime import datetime, timezone
from api.routes.db import get_pf_db_bot

KEYMODES = [9, 10, 12, 14, 16, 18]
STATES = ["ranked", "unranked", "loved"]
GUILD = discord.Object(id=DISCORD_GUILD_ID)

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pending = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Utility cog online")

    @app_commands.command(name="link",
                          description="Link your Discord, osu!, and ALK profiles together.")
    async def link(self, interaction: discord.Interaction):
        state = str(interaction.user.id)

        url = f"{SERVER}/auth/verify?state={state}"
        msg = f"Click here to link your Discord account with your osu! account: {url}"

        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="suggest",
                          description="Suggest a map that you don't have a score for in the ALK database.")
    @app_commands.describe(keys="Keymode",
                           status="Map status",
                           min_sr="Minimum SR",
                           max_sr="Maximum SR")
    @app_commands.choices(
        keys=[app_commands.Choice(name=f"{key}K", value=key) for key in KEYMODES],
        status=[app_commands.Choice(name=state, value=state ) for state in STATES]
    )
    async def suggest(self,
                      interaction: discord.Interaction,
                      keys: app_commands.Choice[int],
                      status: app_commands.Choice[str],
                      min_sr: float = 0.0,
                      max_sr: float = 69420.0):
        try:
            resp = requests.get(
                f"{SERVER}/api/search/discord/{interaction.user.id}",
                timeout=5)
            row = resp.json()

        except:
            await interaction.response.send_message("Something went wrong. You may not be linked, or you may not have a profile on A Lotta Keys.\nTry `/link`.")
            return

        if not row["discord_uid"] or "error" in row:
            await interaction.response.send_message("You're not linked. Link your osu! account with `/link`")
            return
        
        uid = row["uid"]

        try:
            user = Helper.load_user(uid)
        except:
            await interaction.response.send_message(f"You don't have a profile on A Lotta Keys. Create one by logging in:\n{SERVER}/auth/login")
            return

        played_bids = {score["bid"] for score in user["scores"].values()}

        beatmaps = Helper.load_beatmaps_compact()["beatmaps"]
        available_bids = {int(bid) for bid, beatmap in beatmaps.items() if beatmap["keys"] == keys.value and 
                                                                           beatmap["status"].lower() == status.value and
                                                                           beatmap["sr"] > min_sr and
                                                                           beatmap["sr"] < max_sr}
        target_bids = available_bids - played_bids

        if target_bids == {}:
            await interaction.response.send_message("No beatmaps found. Try different filters.")
            return

        suggestion_bid = str(random.choice(list(target_bids)))
        suggestion_name = beatmaps[suggestion_bid]["name"]
        suggestion_sr = beatmaps[suggestion_bid]["sr"]
        suggestion_desc = f"**Difficulty:** {suggestion_name}\n**SR**: {suggestion_sr}"

        await interaction.response.send_message(f"## Here's a [**random {status.value} {keys.value}K map**](<https://osu.ppy.sh/beatmaps/{suggestion_bid}>) you don't have any scores for in A Lotta Keys:\n\n{suggestion_desc}")

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong!")

async def setup(bot):
    cog = Utility(bot)
    await bot.add_cog(Utility(bot))
    bot.tree.add_command(cog.suggest, guild=GUILD)
    bot.tree.add_command(cog.link, guild=GUILD)
    bot.tree.add_command(cog.ping, guild=GUILD)