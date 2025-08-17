import sys
import json
import discord
from textwrap import dedent
from os import listdir
from discord.ext import commands, tasks
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_USERS
from utils import Helper
from datetime import datetime, timezone

class Backend(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        

    def cog_unload(self):
        self.mapfeed.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.previous_mapfeed = datetime.now(timezone.utc)
        self.mapfeed.start()
        print("Backend cog online")

    @commands.command(name="user")
    async def user(self, ctx, name: str):
        embed = discord.Embed(
            title=name,
            color=discord.Colour.from_str("#5B3758")
        )

        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open (f"{PATH_USERS}/{file}", "r", encoding="utf-8") as f:
                text = f.read()
                user = json.loads(text)

            if user["name"] == name:
                uid = user["id"]
                days = user["days ago"]
                no_scores = len(user["scores"])
                tracking = user["tracking"]
                hist = list(user["beatmap plays history"].values()) if user["beatmap plays history"] else [0]
                map_plays = hist[-1]

                embed.add_field(name="UID", value=uid, inline=False)
                embed.add_field(name="Days since last score", value=days, inline=False)
                embed.add_field(name="Tracking", value=tracking, inline=False)
                embed.add_field(name="Tracked scores", value=no_scores, inline=False)
                embed.add_field(name="Beatmap plays", value=map_plays, inline=False)
                await ctx.send(embed=embed)
                return
        
        await ctx.send(f"User {name} not in A Lotta Keys database!")

    @tasks.loop(minutes=3)
    async def mapfeed(self):
        channel = self.bot.get_channel(1405791012533829645)
        helper = Helper()
        recents = helper.recent_beatmaps()
        del helper
        
        for mapset in recents:
            artist = mapset["artist"]
            mapper = mapset["creator"]
            title = mapset["title"]
            id = mapset["id"]
            url = f"https://osu.ppy.sh/beatmapsets/{id}"
            status = mapset["ranked"]
            submitted = datetime.strptime(mapset["submitted_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            updated = datetime.strptime(mapset["last_updated"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            
            if status in [1, 3, 4]:
                ranked = datetime.strptime(mapset["ranked_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            
            #card_url = mapset.covers.card

            if submitted > self.previous_mapfeed:
                msg = f"{mapper} just uploaded **[{artist} - {title}]({url})**, give it a playtest!"
                await channel.send(msg)

            elif updated > self.previous_mapfeed:
                msg = f"{mapper} just updated **[{artist} - {title}]({url})**, give it a playtest!"
                await channel.send(msg)

            elif status == 3 and ranked > self.previous_mapfeed:
                msg = f"@rankfeed\n**[{artist} - {title}]({url})**, hosted by {mapper}, has just been qualified!**"
                await channel.send(msg)

            elif status == 1 and ranked > self.previous_mapfeed:
                msg = f"@rankfeed\n**[{artist} - {title}]({url})**, hosted by {mapper}, has just been ranked!**"
                await channel.send(msg)

            elif status == 4 and ranked > self.previous_mapfeed:
                msg = f"@rankfeed\n**[{artist} - {title}]({url})**, hosted by {mapper}, has just been loved!**"
                await channel.send(msg)

        self.previous_mapfeed = datetime.now(timezone.utc)

async def setup(bot):
    await bot.add_cog(Backend(bot))