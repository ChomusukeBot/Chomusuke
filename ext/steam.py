# Import the commands extension
import discord
from discord.ext import commands
import os
from cog import Cog


BASE_URL = "https://api.steampowered.com"
PROFILE_API = "/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
CSGO_API = "/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={}&steamid={}"



# cog stuff
class SteamCog(Cog):

    def __init__(self, bot):
        # save dat stuff 4 ltr
        self.bot = bot
        self.steam_key = os.environ["STEAM_TOKEN"]

# don't know if this works
    async def getProfileData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + PROFILE_API.format(self.steam_key, profile)) as resp:
            return await resp.json()

    async def getCSData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + CSGO_API.format(self.steam_key, profile)) as resp:
            return await resp.json()



# make the command
    @commands.command(name='profile', aliases=["myp"])
    async def profile(self, ctx, char):
        """
        Generates an embed displaying the specified user's STEAM profile, needs steam id.
        """
        # creates embeded profile
        steamprofile = char
        data = await self.getProfileData(self, steamprofile)
        #await ctx.send(data)
        #await ctx.send(steamprofile)
        if not data:
            await ctx.send("profile not found")
            return
        # do all the embed stuff
        embed = discord.Embed(title=("Real name: " + (data.get("response").get("players")[0].get("realname"))))      
        embed.set_author(name=("Name:" + str(data.get("response").get("players")[0].get("personaname"))))
        embed.add_field(name='country code:', value=data.get("response").get("players")[0].get("locstatecode"), inline=True) 
        
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        await ctx.send(embed=embed)

    # make the command
    @commands.command(name='csgo', aliases=["csg"])
    async def csgo(self, ctx, char):
        """
        embed displaying the specified user's stats for CSGO
        private steam profiles will return nothing
        """
        # creates embeded profile
        steamprofile = char
        data = await self.getProfileData(self, steamprofile)
        data2 = await self.getCSData(self, steamprofile)
        #await ctx.send(data)
        #await ctx.send(steamprofile)
        if not data2:
            await ctx.send("stats not found")
            return
        #IGNORE non working vars:
        #kills = str([x for x in data2["playerstats"]["stats"] if x["name"] == ["total_kills"][0]["value"]])
        #deaths = str([x for x in data2["playerstats"]["stats"] if x["name"] == ["total_deaths"][0]["value"]])

        # do all the embed stuff
        embed = discord.Embed(title=("CSGO Stats for " + str(data.get("response").get("players")[0].get("personaname"))))
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        embed.add_field(name="Total Kills: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_kills"][0]["value"]), inline=True)
        embed.add_field(name="Deaths: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_deaths"][0]["value"]), inline=True)
        embed.add_field(name="Kills by HS: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_kills_headshot"][0]["value"]), inline=True)
        embed.add_field(name="Total damage done: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_damage_done"][0]["value"]), inline=True)
        embed.add_field(name="Last match kills: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "last_match_kills"][0]["value"]), inline=True)
        embed.add_field(name="Last match deaths: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "last_match_deaths"][0]["value"]), inline=True)
        await ctx.send(embed=embed)

# setup the bot ith cog
def setup(bot):

    if "STEAM_TOKEN" in os.environ:
        # if steam token findable launch the cog
        bot.add_cog(SteamCog(bot))

    else:
        print("No steam api key available")
