# Import the commands extension
import discord
from discord.ext import commands
import os
import requests
import json

BASE_URL = "https://{}.api.riotgames.com"
SUMMONER_API = "/lol/summoner/v4/summoners/by-name/{}?api_key={}"

REGIONS = {
    "br": "br1",
    "eune": "eun1",
    "euw": "euw1",
    "jp": "jp1",
    "kr": "kr",
    "lan": "la1",
    "las": "la2",
    "na": "na1",
    "oce": "oc1",
    "tr": "tr1",
    "ru": "ru",
    "pbe": "pbe1"
}


class LeagueCog(commands.Cog):
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        self.league_key = os.environ["LEAGUE_TOKEN"]
        self.league_ver = json.loads(requests.get("https://ddragon.leagueoflegends.com/api/versions.json").text)[0]

    @commands.command(name='lolprofile', aliases=["lp"])
    async def lolprofile(self, ctx, *args):
        if(args[0].lower() in REGIONS):
            region = REGIONS.get(args[0].lower())
        else:
            await ctx.send("Region not found. Use one of the following: \n BR, EUNE, EUW, JP, KR, LAN, LAS, NA, OCE, TR, RU, PBE")
            return

        async with self.bot.session.get(BASE_URL.format(region) + SUMMONER_API.format('{}'.format(' '.join(args[1:])), self.league_key)) as resp:
            if(resp.status == 404):
                await ctx.send("Summoner not found")
                return
            data = await resp.json()

        embed = discord.Embed(title=data.get("name"))
        embed.set_author(name=("Summoner Level - " + str(data.get("summonerLevel"))))
        embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(self.league_ver, data.get("profileIconId")))

        await ctx.send(embed=embed)


def setup(bot):
    if "LEAGUE_TOKEN" in os.environ:
        bot.add_cog(LeagueCog(bot))
    else:
        print("No league api key available")
