# Import the commands extension
import copy
import discord
from discord.ext import commands

# This is our base URL for all API calls
BASE = "https://api.travis-ci.com"
# A list of available endpoints
EP_USER = "/user"
# Travis CI brand colors (https://travis-ci.com/logo)
OXIDE_BLUE = 0x3EAAAF
TURF_GREEN = 0x39AA56
CANARY_YELLOW = 0xEDDE3F
BRICK_RED = 0xDB4545
ASPHALT_GREY = 0x666666
# Our default headers for all of the requests
DEFAULT_HEADERS = {
    "Travis-API-Version": "3",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}


class Travis(commands.Cog):
    """
    A cog for accessing the Travis CI API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        # Save the tokens collection
        self.tokens = bot.database["travis_tokens"]

    @commands.group()
    async def travis(self, ctx):
        """
        Group of commands for interacting with the Travis CI service.
        """

    @travis.command()
    @commands.dm_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def addtoken(self, ctx, token: str):
        """
        Adds a Travis CI token to your Discord User.

        To get a token:
        * Install the Travis Command Line from https://github.com/travis-ci/travis.rb#installation
        * Log into the command line (run "travis login --pro")
        * Generate a token (run "travis token --pro")
        """
        # Create a copy of the default haders
        headers = copy.deepcopy(DEFAULT_HEADERS)
        # Set the token specified by the user
        headers["Authorization"] = f"token {token}"

        # Request the user data
        async with self.bot.session.get(BASE + EP_USER, headers=headers) as resp:
            # If the code is 403
            if resp.status == 403:
                await ctx.send("The token that has been specified is not valid.")
            # If the code is 200
            elif resp.status == 200:
                # Try to get a document with the user ID
                existing = await self.tokens.find_one({"_id": ctx.author.id})

                # If there is an existing item
                if existing:
                    # Replace the existing values
                    await self.tokens.replace_one({"_id": ctx.author.id}, {"token": token})
                    # Notify the user
                    await ctx.send("Your existing token has been replaced!")
                # Otherwise
                else:
                    # Add a completely new item
                    await self.tokens.insert_one({"_id": ctx.author.id, "token": token})
                    # Notify the user
                    await ctx.send("Your token has been added!")
            # If the code is anything else
            else:
                await ctx.send(f"Error while checking for your token: Code {resp.status}")

        # If the user posted on a public text channel
        if isinstance(ctx.channel, discord.TextChannel):
            # Delete the original message
            await ctx.message.delete()


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Travis(bot))
