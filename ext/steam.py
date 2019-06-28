# Import the commands extension
import discord
from discord.ext import commands
import os
from cog import Cog

BASE_URL = "https://api.steampowered.com"
PROFILE_API = "/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
CSGO_API = "/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={}&steamid={}"
TFII_API = "/ISteamUserStats/GetUserStatsForGame/v0002/?appid=440&key={}&steamid={}"
RUST_API = "/ISteamUserStats/GetUserStatsForGame/v0002/?appid=252490&key={}&steamid={}"

# cog stuff
class Steam(Cog):

    def __init__(self, bot):
        # save dat stuff 4 ltr
        self.bot = bot
        self.steam_key = os.environ["STEAM_TOKEN"]

    #DATAHELP
    #profile
    async def getProfileData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + PROFILE_API.format(self.steam_key, profile)) as resp:
            return await resp.json()

    #CSGOProfile
    async def getCSData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + CSGO_API.format(self.steam_key, profile)) as resp:
            return await resp.json()

    #TF2Data
    async def getTFIIData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + TFII_API.format(self.steam_key, profile)) as resp:
            return await resp.json()

    #RustData
    async def getRustData(self, ctx, profile):
        async with self.bot.session.get(BASE_URL + RUST_API.format(self.steam_key, profile)) as resp:
            return await resp.json()

    #COMMANDS
    # PROFILE COMMAND
    @commands.command(name='profile', aliases=["myp"])
    async def profile(self, ctx, char):
        """
        Generates an embed displaying the specified user's STEAM profile, needs steam id.
        """
        # creates embeded profile
        steamprofile = char
        data = await self.getProfileData(self, steamprofile)

        #create var for checking
        
        if not data:
            await ctx.send("profile not found")
            return
        # do all the embed stuff

        embed = discord.Embed(title=("Real name: " + (data.get("response").get("players")[0].get("realname"))))         
        embed.set_author(name=("Name:" + str(data.get("response").get("players")[0].get("personaname"))))
        embed.add_field(name='country code:', value=data.get("response").get("players")[0].get("loccountrycode"), inline=True)
        
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        await ctx.send(embed=embed)

    #PROFILE SEARCH Command
    @commands.command(name="inprofile", aliases=["fip"])
    async def inprofile(self, ctx, char, search):
        """
        Generates an embed displaying the specified user's STEAM profile with a custom search parameter
        ex "inprofile [steam id] 
        """
        # get data and needed variables
        steamprofile = char
        findData = search
        data = await self.getProfileData(self, steamprofile)

        if not data:
            await ctx.send("profile not found")
            return

        # create and send embeded
        embed = discord.Embed(title=("Real name: " + (data.get("response").get("players")[0].get("realname"))))      
        embed.set_author(name=("Name:" + str(data.get("response").get("players")[0].get("personaname"))))
        embed.add_field(name=findData + "(custom):", value=data.get("response").get("players")[0].get(findData), inline=True) 
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        
        await ctx.send(embed=embed)


    #CSGO Command
    @commands.command(name="csgo", aliases=["csg"])
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

        # embed and send embeded
        embed = discord.Embed(title=("CSGO Stats for " + str(data.get("response").get("players")[0].get("personaname"))))
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        embed.add_field(name="Total Kills: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_kills"][0]["value"]), inline=True)
        embed.add_field(name="Deaths: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_deaths"][0]["value"]), inline=True)
        embed.add_field(name="Kills by HS: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_kills_headshot"][0]["value"]), inline=True)
        embed.add_field(name="Total damage done: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "total_damage_done"][0]["value"]), inline=True)
        embed.add_field(name="Last match kills: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "last_match_kills"][0]["value"]), inline=True)
        embed.add_field(name="Last match deaths: ", value=str([x for x in data2["playerstats"]["stats"] if x["name"] == "last_match_deaths"][0]["value"]), inline=True)
        
        await ctx.send(embed=embed)

    # TEAM FORTERESS TWO command
    @commands.command(name='tfii', aliases=["tf2"])
    async def tfii(self, ctx, char):
        """
        embed displaying the specified user's stats for 
        Team forteress II
        ex: tfii [steam ID code]
        """
        # creates vars needed
        steamprofile = char
        data = await self.getProfileData(self, steamprofile)
        data3 = await self.getTFIIData(self, steamprofile)
        
        if not data3:
            await ctx.send("stats not found")
            return

        # do all the embed stuff
        embed = discord.Embed(title=("TF II Stats for " + str(data.get("response").get("players")[0].get("personaname"))))
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        embed.add_field(name="Scout kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Scout.accum.iNumberOfKills"][0]["value"]), inline=True)
        embed.add_field(name="Soldier kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Soldier.accum.iNumberOfKills"][0]["value"]), inline=True)
        embed.add_field(name="Pyro kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Pyro.accum.iNumberOfKills"][0]["value"]), inline=True)
        embed.add_field(name="Medic kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Medic.accum.iNumberOfKills"][0]["value"]), inline=True)
        embed.add_field(name="Engineer kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Engineer.accum.iNumberOfKills"][0]["value"]), inline=True)
        embed.add_field(name="Engineer sentry kills: ", value=str([x for x in data3["playerstats"]["stats"] if x["name"] == "Engineer.max.iSentryKills"][0]["value"]), inline=True)
        await ctx.send(embed=embed)


    # make the command
    @commands.command(name='rust', aliases=["rst"])
    async def rust(self, ctx, char):
        """
        embed displaying the specified user's stats for 
        Rust
        ex: rust [steam id code]
        """
        # get necessary data into vars
        steamprofile = char
        data = await self.getProfileData(self, steamprofile)
        data4 = await self.getRustData(self, steamprofile)

        if not data4:
            await ctx.send("stats not found")
            return

        # do all the embed stuff
        embed = discord.Embed(title=("Rust Stats for " + str(data.get("response").get("players")[0].get("personaname"))))
        embed.set_thumbnail(url=(data.get("response").get("players")[0].get("avatarmedium")))
        embed.add_field(name="Deaths: ", value=str([x for x in data4["playerstats"]["stats"] if x["name"] == "deaths"][0]["value"]), inline=True)
        embed.add_field(name="Kills: ", value=str([x for x in data4["playerstats"]["stats"] if x["name"] == "kill_player"][0]["value"]), inline=True)
        embed.add_field(name="Mele strikes: ", value=str([x for x in data4["playerstats"]["stats"] if x["name"] == "melee_strikes"][0]["value"]), inline=True)
        embed.add_field(name="Wounds: ", value=str([x for x in data4["playerstats"]["stats"] if x["name"] == "wounded"][0]["value"]), inline=True)
        await ctx.send(embed=embed)


# setup the bot ith cog
def setup(bot):

    if "STEAM_TOKEN" in os.environ:
        # if steam token findable launch the cog
        bot.add_cog(Steam(bot))

    else:
        print("No steam api key available")
        