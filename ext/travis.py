# Import the commands extension
from discord.ext import commands


class Travis(commands.Cog):
    """
    A cog for accessing the Travis CI API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Travis(bot))
