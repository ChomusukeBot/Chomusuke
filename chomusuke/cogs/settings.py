from discord.ext import commands

from chomusuke.exceptions import DatabaseRequired


class Settings(commands.Cog):
    """
    Commands for changing the different guild settings.
    """

    def __init__(self, bot):
        # If there is no database saved
        if not bot.db:
            # Raise an exception
            raise DatabaseRequired("The Settings need to be stored in a database!")
        # Otherwise, save the bot
        self.bot = bot

    @commands.command()
    async def setting(self, ctx: commands.Context, setting: str = None, value=None):
        """
        Store and Fetch the settings for the Guild.
        """
        # If there is no setting, return a list of available settings
        if not setting:
            # Create the readable list of settings
            settings = ", ".join(self.bot.settings)
            # And return it
            await ctx.send("The available settings are: " + settings)
            return

        # Change the setting to lower case
        lower = setting.lower()

        # If the setting is not valid, send an error message and return
        if lower not in self.bot.settings:
            await ctx.send("The specified setting is not valid. "
                           "Make sure that is written correctly and try again.")
            return

        # If there is no parameter to set
        if not value:
            # Get the value of it
            existing = await self.bot.get_setting(ctx, lower)
            # And show it
            await ctx.send(f"The existing value of {lower} is {existing}")

        # If we got here, there is a setting to save
        # Go ahead and save it
        await self.bot.save_setting(ctx, lower, value)
        # And notify about it
        await ctx.send(f"Setting for {lower} was saved!")
