# Import the commands extension
import discord
import logging
from cog import Cog
from discord.ext import commands


logger = logging.getLogger("chomusuke")


class ErrorHandler(Cog):
    """
    An error handling cog.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Task when an error occurs."""

        if isinstance(error, commands.CommandNotFound):
            return logger.info(f"{ctx.author} used {ctx.message.content} but nothing was found.")

        elif isinstance(error, commands.MissingRequiredArgument):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered MissingRequiredArgument error.")
            return await ctx.send(f"`{error.param}` is a required argument.")

        elif isinstance(error, commands.CheckFailure):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered CheckFailure error.")
            return await ctx.send("You do not have permission to use this command!")

        elif isinstance(error, commands.UserInputError) or isinstance(error, commands.BadArgument):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered UserInputError error.")
            return await ctx.send("Invalid arguments.")

        elif isinstance(error, commands.CommandOnCooldown):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered ComamndOnCooldown error.")
            return await ctx.send(f"Command is on cooldown! Please retry after `{error.retry_after}`")

        elif isinstance(error, commands.BotMissingPermissions):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered BotMissingPermissions error.")
            embed = discord.Embed()
            embed.colour = discord.Colour.blue()
            title = "The bot lacks the following permissions to execute the command:"
            embed.title = title
            embed.description = ""
            for perm in error.missing_perms:
                embed.description += str(perm)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.DisabledCommand):
            logger.info(f"{ctx.author} called {ctx.message.content} and triggered DisabledCommand error.")
            return await ctx.send("The command has been disabled!")

        else:
            logger.warning(f"{ctx.author} called {ctx.message.content} and triggered the following error:\n {error}")


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(ErrorHandler(bot))
