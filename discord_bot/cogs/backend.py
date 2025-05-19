import sys
import json
import discord
from textwrap import dedent
from os import listdir
from discord.ext import commands
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DISCORD_BOT_TOKEN, PATH_USERS

class Backend(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
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
            
async def setup(bot):
    await bot.add_cog(Backend(bot))