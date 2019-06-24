# Import the commands extension
import discord
from discord.ext import commands
import os
import pprint

BASE_URL = "https://na1.api.riotgames.com"
SUMMONER_API = "/lol/summoner/v4/summoners/by-name/{}?api_key={}"


class LeagueCog(commands.Cog):
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        self.league_key = os.environ["LEAGUE_TOKEN"]
        # self.league_ver =

    @commands.command(name='lolprofile', aliases=["lp"])
    async def lolprofile(self, ctx, args):
        async with self.bot.session.get(BASE_URL + SUMMONER_API.format(args, self.league_key)) as resp:
            if(resp.status == 404):
                await ctx.send("Summoner not found")
            data = await resp.json()
        pprint.pprint(data)
        embed = discord.Embed(title=data.get("name"))
        embed.set_author(name=("Summoner Level - " + str(data.get("summonerLevel"))))
        embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/9.12.1/img/profileicon/{}.png".format(data.get("profileIconId")))

        await ctx.send(embed=embed)


def setup(bot):
    if "LEAGUE_TOKEN" in os.environ:
        bot.add_cog(LeagueCog(bot))
    else:
        print("No league api key available")
