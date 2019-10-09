from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog


class Basics(Cog):
    """
    A set of basic information commands for Chomusuke.
    """
    def __init__(self, bot):
        """
        Initializes a new instance of the Basics cog.
        """
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        """
        Shows some basic information about the Bot.
        """
        # Format the description for adding it later
        description = "Chomusuke is a Discord Bot created with the intention of " \
                      "providing productive integrations for Developers and Gamers.\n\n" \
                      "[Support (GitHub)](https://github.com/ChomusukeBot/Chomusuke/issues) | " \
                      "[Support (Discord)](https://discord.gg/Cf6sspj) | " \
                      "[Roadmap](https://github.com/ChomusukeBot/Chomusuke/projects)\n\n" \
                      ""
        # Create an embed for showing the info
        embed = Embed(title=f"About {self.bot.user.name}", description=description,
                      url="https://github.com/ChomusukeBot", color=0xE40025)
        # Set the thumbnail to the image of the repository
        embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/52353631")
        # And finally send the embed
        await ctx.send(embed=embed)
