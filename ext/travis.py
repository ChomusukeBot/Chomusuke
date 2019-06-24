# Import the commands extension
from discord.ext import commands

# This is our base URL for all API calls
BASE = "https://api.travis-ci.com"
# Our default headers for all of the requests
DEFAULT_HEADERS = {
    "Travis-API-Version": "3",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}


class Travis(commands.Cog):
    """
    A cog for accessing the Travis CI API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    @commands.group()
    async def travis(self, ctx):
        """
        The base for all of our Travis CI calls.
        """
        pass


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Travis(bot))
