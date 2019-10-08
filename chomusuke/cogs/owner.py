import logging

from discord.ext import commands

from chomusuke.bot import Chomusuke

LOGGER = logging.getLogger("chomusuke")


class Owner(commands.Cog):
    """
    Commands for the Bot owner (controlled by the Discord team).
    """
    def __init__(self, bot):
        """
        Starts a new instance of the Owner cog.
        """
        self.bot: Chomusuke = bot

    async def __local_check(self, ctx):
        """
        Makes sure that the user triggering the command is a Bot owner.
        """
        # TODO: Check if this works with multiple users on a Discord Dev Team
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def stop(self, ctx):
        """
        Disconnects the bot and closes all of the API connections.

        If the bot is running as a service or on Heroku, is probably going to restart.
        """
        # Notify that we are closing the bot
        LOGGER.warning(f"Shutdown requested by '{ctx.author.name}#{ctx.author.discriminator}' "
                       f"({ctx.author.id})")
        # Send a message to show that we are disconnecting
        await ctx.send(f"{ctx.author.mention} Bye!")
        # Close the bot connection
        await self.bot.close()
