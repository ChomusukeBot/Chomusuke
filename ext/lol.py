# Import the commands extension
import discord
from discord.ext import commands
import os
import requests
import json

# Base URL for all API calls
BASE_URL = "https://{}.api.riotgames.com"
# League of Legends Statit Data for profile pictures
PROFILE_IMAGE_URL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png"
# API Operation used to access summoner data
SUMMONER_API = "/lol/summoner/v4/summoners/by-name/{}?api_key={}"
# API Operation used to access summoner ranked data
RANKED_API = "/lol/league/v4/entries/by-summoner/{}?api_key={}"
# API Operation used to access summoner matchlist
MATCH_API = "/lol/match/v4/matchlists/by-account/{}?api_key={}"
# A .json file storing the current and all previous versions of league of legends
LEAGUE_VERSION = "https://ddragon.leagueoflegends.com/api/versions.json"
# A dictionary of RIOT's regional endpoints and their corresponding server shortcuts
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
    """
    A cog for accessing the League of Legends API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        # Save the league api key and the current league version
        self.league_key = os.environ["LEAGUE_TOKEN"]
        self.league_ver = json.loads(requests.get(LEAGUE_VERSION).text)[0]

    @commands.command(name='lolprofile', aliases=["lp"])
    async def lolprofile(self, ctx, *args):
        """
        Generates an embed displaying the specified users LoL Profile.
        """
        # Check if the specified region is correct
        if(args[0].lower() in REGIONS):
            region = REGIONS.get(args[0].lower())
        else:
            await ctx.send("Region not found. Use one of the following: \nBR, EUNE, EUW, JP, KR, LAN, LAS, NA, OCE, TR, RU, PBE")
            return
        # Request the summoner data
        async with self.bot.session.get(BASE_URL.format(region) + SUMMONER_API.format('{}'.format(' '.join(args[1:])), self.league_key)) as resp:
            # If the code is 404
            if(resp.status == 404):
                await ctx.send("Summoner not found")
                return
            # If the code is 200
            elif(resp.status == 200):
                data = await resp.json()

        embed = discord.Embed(title=data.get("name"))
        embed.set_author(name=("Summoner Level - " + str(data.get("summonerLevel"))))
        embed.set_thumbnail(url=PROFILE_IMAGE_URL.format(self.league_ver, data.get("profileIconId")))
        # Request the summoner ranked data
        async with self.bot.session.get(BASE_URL.format(region) + RANKED_API.format(data.get("id"), self.league_key)) as resp:
            rankData = await resp.json()
        # If summoner ranked data exists
        if rankData:
            rankData = rankData[0]
            embed.add_field(name="Rank", value=("{} {}".format(rankData.get("tier"), rankData.get("rank"))), inline=True)
            embed.add_field(name="Ranked W/L", value=("{}/{}".format(rankData.get("wins"), rankData.get("losses"))), inline=True)
            embed.add_field(name="League Points", value=rankData.get("leaguePoints"), inline=True)
        else:
            embed.add_field(name="Unranked", value="\u200b", inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    # Initial check to see if a league of legends api token exists in our enviroment
    if "LEAGUE_TOKEN" in os.environ:
        bot.add_cog(LeagueCog(bot))
    else:
        print("No league api key available")
