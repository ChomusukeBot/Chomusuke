# Import the commands extension
from discord.ext import commands


class Owner(commands.Cog):
    """
    Commands for the bot owner.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    async def __local_check(self, ctx):
        """
        The check for the entire Cog.
        """
        # Make sure that we are only allowing Bot owners
        # TODO: Check if this works with multiple users on a Discord Dev Team
        return await self.bot.is_owner(ctx.author)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Owner(bot))
