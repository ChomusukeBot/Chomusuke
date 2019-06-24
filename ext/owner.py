# Import the commands extension and the rest of our tools
from discord.ext import commands
from os.path import isfile


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

    @commands.command()
    async def unload(self, ctx, extension: str):
        """
        Unloads a specific extension file.
        """
        # Just try to unload the file and notify the user
        try:
            self.bot.unload_extension(f"ext.{extension}")
            await ctx.send(f"{extension} has been unloaded.")
        # In the case of an exception
        except Exception as e:
            # Just send the traceback
            await ctx.send(f"```{e.print_exc()}```")

    @commands.command()
    async def load(self, ctx, extension: str):
        """
        Loads a specific extension file.
        """
        # If the specific file does not exists
        if not isfile(f"ext/{extension}.py"):
            # Notify the user and return
            await ctx.send(f"The extension {extension} does not exists!")
            return

        # Try to load the file as usual
        try:
            self.bot.load_extension(f"ext.{extension}")
            await ctx.send(f"{extension} has been loaded.")
        # In the case of an exception
        except Exception as e:
            # Just send the traceback
            await ctx.send(f"```{e.print_exc()}```")


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Owner(bot))
