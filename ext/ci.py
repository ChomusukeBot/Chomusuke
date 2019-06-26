# Import our libraries
import copy
import discord
from cog import Cog
from discord.ext import commands
from exceptions import NoTokenSet


class ContinuousIntegration(Cog):
    """
    A cog for accessing common Cotinuous integration APIs.
    """
    def __init__(self, bot, name: str, auth: str, headers: dict, endpoints: dict):
        # Save our bot for later use
        self.bot = bot
        # Save the collections
        self.tokens = bot.database[f"{name}_tokens"]
        self.picks = bot.database[f"{name}_picks"]
        # Save our default set of parameters
        self.auth = auth
        self.headers = headers
        self.endpoints = endpoints

    async def dump_data(self, ctx):
        """
        Returns user data stored by the Cog.
        """
        # Get the token of the user and stored pick
        token = await self.tokens.find_one({"_id": ctx.author.id})
        pick = await self.picks.find_one({"_id": ctx.author.id})
        # Create a place to store the dict
        data = {}
        # If there is a token found, add it into the group
        if token:
            data["token"] = token["token"]
        # If there is a pick found, add it into the group
        if pick:
            data["pick"] = pick["slug"]
        # Finally, return the data
        return data

    async def forget_data(self, ctx):
        """
        Removes the user data from the AppVeyor collections.
        """
        # Just delete those with the id of the user
        self.tokens.delete_many({"_id": ctx.author.id})
        self.picks.delete_many({"_id": ctx.author.id})
        return True

    async def generate_headers(self, ctx, auth_name: str):
        """
        Generates a set of headers for the use on aiohttp requests.
        """
        # Get the current user token
        token = (await self.get_token(ctx.author.id))["token"]
        # Create a copy of the default haders
        headers = copy.deepcopy(self.headers)
        # Set the token specified by the user
        headers["Authorization"] = f"{auth_name} {token}"
        # Finally, return the headers
        return headers

    async def get_token(self, _id: int):
        """
        Makes sure that a command is ready for the user.
        """
        # Get the user token
        existing = await self.tokens.find_one({"_id": _id})
        # If there is no token
        if not existing:
            raise NoTokenSet("A Travis CI.com token is required.")
        # Otherwise, return found key
        return existing

    @commands.command()
    async def addtoken(self, ctx, token: str):
        """
        Adds a Personal Token to our database.
        Please note that we check the validity of the tokens prior to storing them.
        """
        # Send a typing
        await ctx.trigger_typing()

        # Create a copy of the default haders
        headers = copy.deepcopy(self.headers)
        # Set the token specified by the user
        headers["Authorization"] = f"{self.auth} {token}"

        # Request the user data
        async with self.bot.session.get(self.endpoints["validity"], headers=headers) as resp:
            # If the code is 403
            if resp.status == 403:
                await ctx.send("The token that has been specified is not valid.")
            # If the code is 200
            elif resp.status == 200:
                # Update an item and create it if is not present
                await self.tokens.replace_one({"_id": ctx.author.id}, {"_id": ctx.author.id, "token": token}, True)
                # Notify the user
                await ctx.send("Your token has been updated!")
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
    pass
