import os
import platform

import discord
from discord.ext import commands
from git import NoSuchPathError, Repo

DESCRIPTION = "Chomusuke is a Discord Bot created by Lemon#6947 for making servers more productive and fun."
REVISION = "[{0}](https://github.com/ChomusukeBot/Chomusuke/tree/{1}) from {2}"
SUPPORT = "[GitHub](https://github.com/ChomusukeBot/Chomusuke/issues) & [Discord](https://discord.gg/Cf6sspj)"


class Basics(commands.Cog):
    """
    A set of basic information commands for Chomusuke.
    """
    def __init__(self, bot):
        """
        Initializes a new instance of the Basics cog.
        """
        # Save the branch and latest commit
        self.bot = bot

    @commands.command(aliases=["info"])
    async def about(self, ctx: commands.Context):
        """
        Shows some basic information about the Bot.
        """
        try:
            # Get some information from the git repository
            repo = Repo(".git")
            short_hash = repo.git.rev_parse(repo.head, short=True)
            long_hash = repo.head.commit
            branch = repo.head.ref
            # And save it
            git_info = REVISION.format(short_hash, long_hash, branch)
        except NoSuchPathError:
            # If the repo was not found, say it
            git_info = "No Git Repo Found"

        # If we have a DYNO environment variable, we are using Heroku
        if "DYNO" in os.environ:
            system = "Heroku"
        # Otherwise, save the name of the system
        else:
            system = platform.system()

        # Create an embed for showing the info
        embed = discord.Embed(title=f"About Chomusuke", description=DESCRIPTION,
                              url="https://github.com/ChomusukeBot", color=0xE40025)
        # Set the thumbnail to the image of the GitHub organization
        embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/52353631")
        # And add a couple of fields that we need
        embed.add_field(name="Version", value=git_info, inline=True)
        embed.add_field(name="Support", value=SUPPORT, inline=True)
        embed.add_field(name="Stats", value="{0} guilds\n{1} users".format(len(self.bot.guilds), len(self.bot.users)))
        embed.add_field(name="Running on", value=system)
        # And finally send the embed
        await ctx.send(embed=embed)
