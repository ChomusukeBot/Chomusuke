# Import the commands extension
import discord
import io
import json
from cog import Cog
from discord.ext import commands

REMOVAL = ("Cogs that had data and was removed: {0}\n"
           "Cogs that didn't had data or were unable to delete it: {1}\n\n"
           "Please note that data owned by 3rd parties (GitHub, Travis CI, Discord) can't be deleted by us.")


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

    @gdpr.command()
    @commands.cooldown(1, 60 * 12, commands.BucketType.user)
    async def forget(self, ctx):
        """
        Removes all of your data from the bot, and then sends you the list of cogs that removed your data.
        """
        # Notify the user
        await ctx.author.send("Your data is being removed, please wait...")

        # Create a place to store the names
        yes = []
        no = []

        # Iterate over the bot cogs
        for name, cog in self.bot.cogs.items():
            # If it was possible to remove data, add the name on the yes list
            if await cog.forget_data(ctx):
                yes.append(name)
            # Otherwise, add it into the no list
            else:
                no.append(name)

        # Finish by notifying the user
        await ctx.author.send(REMOVAL.format(", ".join(yes), ", ".join(no)))


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(GDPR(bot))
