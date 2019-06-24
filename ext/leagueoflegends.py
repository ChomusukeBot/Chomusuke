# Import the commands extension
from discord.ext import commands

class LeagueCog(commands.Cog):
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

def setup(bot):
    bot.add_cog(LeagueCog(bot))