import sys
import json
import discord
import aiohttp
import uuid
import asyncio
import random
from textwrap import dedent
from os import listdir
from discord.ext import commands, tasks
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_USERS, PATH_DATA
from utils import Helper
from datetime import datetime, timezone
from api.routes.db import get_pf_db_bot

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Utility cog online")

    @commands.command(name="link")
    async def link(self, ctx):
        state = str(ctx.author.id)

        url = f"http://127.0.0.1:5000/auth/verify?state={state}"
        msg = f"Click here to link your Discord account with your osu! account: {url}"

        await ctx.author.send(msg)

    @commands.command(name="suggest")
    async def suggest(self, ctx, keys=10, status="ranked"):
        status = status.lower()
        if status not in ["ranked", "loved", "unranked"] or keys not in [9, 10, 12, 14, 16, 18]:
            await ctx.channel.send("Command usage:\n`!suggest <keys> <status>`\n`<keys>` must be one of `9`, `10`, `12`, `14`, `16`, or `18`. Default `10`.\n<status must be one of `ranked`, `loved`, or `unranked`. Deafult `ranked`.>")
            return

        pf_db = get_pf_db_bot()
        cur = pf_db.cursor()
        cur.execute("SELECT * FROM profiles WHERE discord_uid = ?", (ctx.author.id,))
        row = cur.fetchone()

        if not row:
            await ctx.channel.send("You're not linked. Link your osu! account with `!link`")
            return
        
        uid = row["uid"]

        user = Helper.load_user(uid)

        played_bids = {score["bid"] for score in user["scores"].values()}
        available_bids = {int(bid) for bid, beatmap in Helper.load_beatmaps_compact()["beatmaps"].items() if beatmap["keys"] == keys and beatmap["status"].lower() == status}
        target_bids = available_bids - played_bids

        suggestion = random.choice(list(target_bids))

        await ctx.channel.send(f"Here's a random {status} {keys}K map you don't have any scores for in A Lotta Keys:\nhttps://osu.ppy.sh/beatmaps/{suggestion}")
        
async def setup(bot):
    await bot.add_cog(Utility(bot))