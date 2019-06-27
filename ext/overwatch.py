import discord
from discord.ext import commands
from cog import Cog
import lxml.html
import aiohttp


class Overwatch(Cog):
    """
        A cog for getting stats about an Overwatch player.
    """
    def __init__(self, bot):
        self.bot = bot
    
    async def __get_overwatch_source(self, session, platform, player):
        """
            This function retrieves the source of the requested player profile.
            :param session: aiohttp.ClientSession object
            :param platform: str -- This is the platform to check for the player on
            :param player: str -- This is the full player name to check.
            :return: tuple -- Contains full response text (site source), and the status code of the response.
        """
        url = f'https://playoverwatch.com/en-us/career/{platform}/{player}'
        async with session.get(url) as response:
            resp = await response.text()
            resp_code = response.status
        return (resp, resp_code)

    async def __check_profile(self, src):
        """
            This function provides a simple check for whether or not the profile was found.
            :param src: str -- This is the source code.
            :return: bool -- True of found, False if not found.
        """
        if 'Profile Not Found' in src:
            # This profile was not found.
            return False
        else:
            # This profile was found, and is public
            return True

    @commands.command(aliases=['stats', 'ow'])
    async def get_stats(self, ctx, platform=None, player=None):
        """
            Command to get the stats for a given player on a given platform.
        """
        if player is None or platform is None:
            return await ctx.send("You must provide both a player and a platform to retrieve player stats.")
        # Format player name.
        if platform == 'pc':
            if '#' not in player:
                return await ctx.send('PC player names must include a discriminator. Example: `Lemon#13526`')
            else:
                player = player.replace('#', '-')
        
        # Check that the user has provided a valid overwatch platform.
        platforms = ('pc', 'psn', 'xbl')
        if platform not in platforms:
            return await ctx.send(f"`{platform}` is not a valid platform. \nValid platform choices are: `pc`, `psn`, or `xbl`.")
        
        # Check if the player provided in a valid format.
        async with aiohttp.ClientSession() as session:
            content, code = await self.__get_overwatch_source(session, platform, player)

        # If we get anything other than HTTP200: OK something is wrong on BLizzard's end.
        if code != 200:
            return await ctx.send('Having some trouble contacting the Overwatch website. Please try again later.')

        # Check if the player provided was found.
        found = await self.__check_profile(content)

        if found == False:
            return await ctx.send('The profile for the player specified either does not exist or is set private.')

    @commands.command()
    async def test(self, ctx):
        return await ctx.send("👍")


def setup(bot):
    bot.add_cog(Overwatch(bot))