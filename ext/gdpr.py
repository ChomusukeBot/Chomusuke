# Import the commands extension
import discord
import io
import json
from cog import Cog
from discord.ext import commands


class GDPR(Cog):
    """
    A class for helping people with their GDPR requests.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    @commands.group()
    async def gdpr(self, ctx):
        """
        Group of commands for managing your GDPR needs.
        """

    @gdpr.command()
    @commands.cooldown(1, 60 * 12, commands.BucketType.user)
    async def dump(self, ctx):
        """
        Sends a JSON file via private messages containing all of your data.
        """
        # Tell the command author to wait because this is going to take time
        await ctx.author.send("Please wait while we gather your data...")

        # Create a dict to store our data
        data = {}

        # Iterate over the bot cogs
        for name, cog in self.bot.cogs.items():
            # Run the function for dumping data and store it
            data[name] = await cog.dump_data(ctx)

        # Create a string io
        string = io.StringIO(json.dumps(data, sort_keys=True))
        # Create a discord file
        file = discord.File(string, "data.json")
        # Send the JSON via private messages
        await ctx.author.send(file=file)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(GDPR(bot))
