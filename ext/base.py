# Import the commands extension
from cog import Cog


class CustomCog(Cog):
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
