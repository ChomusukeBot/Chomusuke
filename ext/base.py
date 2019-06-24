# Import the commands extension
from discord.ext import commands


class CustomCog(commands.Cog):
    """
    The base class for our custom cog.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(CustomCog(bot))
