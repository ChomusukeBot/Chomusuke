# Import the commands extension
import discord
import os
from cog import Cog
from discord.ext import commands
from ext.lol import REGIONS


APIs = {
    "github": "https://api.github.com/zen",
    "travis": "https://api.travis-ci.com/",
    "appveyor": "https://ci.appveyor.com",
    "overwatch": "https://overwatchy.com/"
}
ALL_AUTH = {
    "api_key": os.environ.get("LEAGUE_TOKEN")
}

BASE_URL = "https://{}.api.riotgames.com"
SHARD_STATUS_URL = "/lol/status/v3/shard-data?api_key={}"


class Status(Cog):
    """
    A cog that monitors API status.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        # guild = self.bot.get_guild(591570953771810820)
        await ctx.send("Fetching status...this may take some time.")
        emoji1 = "\U00002705"
        emoji2 = "\U0001F6AB"

        riot_status = ""
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.title = "API statuses"
        for key, value in APIs.items():
            async with self.bot.session.get(url=value) as response:
                if response.status == 200:
                    embed.add_field(name=f"{key} API", value=emoji1, inline=True)
                else:
                    embed.add_field(name=f"{key} API", value=emoji2, inline=True)
        for key, value in REGIONS.items():
            url = BASE_URL.format(value) + SHARD_STATUS_URL.format(ALL_AUTH["api_key"])
            async with self.bot.session.get(url=url) as response:
                if response.status == 200:
                    pass
                else:
                    riot_status += key + ", "
        riot_status = riot_status[:-2]
        if riot_status != "":
            riot_status = " - except " + riot_status
        embed.add_field(name="League of Legends API", value=f"{emoji1}{riot_status}", inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Status(bot))
