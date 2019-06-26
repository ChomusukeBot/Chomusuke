# Import the commands extension
import discord
from discord.ext import commands
import os
from cog import Cog


BASE_URL = "https://api.steampowered.com"
PROFILE_API = "/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"


# cog stuff
class SteamCog(Cog):

    def __init__(self, bot):
        # save dat stuff 4 ltr
        self.bot = bot
        self.steam_key = os.environ["STEAM_TOKEN"]

# don't know if this works
    async def getProfileData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + PROFILE_API.format(self. steam_key, profile)) as resp:
            return await resp.json()

# make the command
    @commands.command(name='profile', aliases=["myp"])
    async def profile(self, ctx, *args):
        # creates embeded profile
        steamprofile = '{}'.format(' '.join(args[1:]))
        data = await self.getProfileData(self, steamprofile)
        if not data:
            await ctx.send("profile not found")
            return
        # do all the embed stuff
        embed = discord.Embed(title=data.get("personaname"))
        embed.set_author(name=("Real name: " + str(data.get("realname"))))
        embed.set_thumbnail(url=(data.get("avatar")))
        await ctx.send(embed=embed)


# setup the bot ith cog
def setup(bot):

    if "STEAM_TOKEN" in os.environ:
        # if steam token findable launch the cog
        bot.add_cog(SteamCog(bot))

    else:
        print("No steam api key available")
