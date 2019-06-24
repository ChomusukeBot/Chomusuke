# Start by loading the important stuff
from discord.ext import commands


class Chomusuke(commands.AutoShardedBot):
    """
    Custom base class for the Chomusuke bot.
    """
    def __init__(self, *args, **kwargs):
        # Initialize the usual bot
        super().__init__(*args, **kwargs)
