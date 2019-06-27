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
        async with self.bot.session.get(BASE_URL + PROFILE_API.format(self.steam_key, profile)) as resp:
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
        #embed.set_thumbnail(url=(data.get("avatar")))       
        embed.set_author(name=("Name:" + str(data.get("response").get("players")[0].get("personaname"))))
        #embed.add_field(name="Country & City", value=("{} {}".format(data.get("response").get("players")[0].get("loccountrycode")), (data.get("response").get("players")[0].get("loccountrycode"))), inline=True)
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        await ctx.send(embed=embed)

# setup the bot ith cog
def setup(bot):

    if "STEAM_TOKEN" in os.environ:
        # if steam token findable launch the cog
        bot.add_cog(SteamCog(bot))

    else:
        print("No steam api key available")
