import logging

from discord.ext import commands

LOGGER = logging.getLogger("chomusuke")


class Owner(commands.Cog):
    """
    Set of commands for controlling the Bot by their owners.
    """
    def __init__(self, bot):
        # Just save the bot
        self.bot = bot

    async def __local_check(self, ctx):
        """
        Ensures that the command author is a Bot owner.
        """
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def stop(self, ctx):
        """
        Disconnects the bot and closes all of the API connections.
        """
        # Notify that we are closing the bot
        LOGGER.warning(f"Shutdown requested by \"{ctx.author.name}#{ctx.author.discriminator}\" ({ctx.author.id})")
        # Send a message to show that we are disconnecting
        await ctx.send(f"{ctx.author.mention} Bye!")
        # Close the bot connection
        await self.bot.close()
