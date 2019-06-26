# Import our libraries
import copy
from cog import Cog
from exceptions import NoTokenSet


class ContinuousIntegration(Cog):
    """
    A cog for accessing common Cotinuous integration APIs.
    """
    def __init__(self, bot, name):
        # Save our bot for later use
        self.bot = bot
        # Save the collections
        self.tokens = bot.database[f"{name}_tokens"]
        self.picks = bot.database[f"{name}_picks"]

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

    async def generate_headers(self, ctx, default: dict, auth_name: str):
        """
        Generates a set of headers for the use on aiohttp requests.
        """
        # Get the current user token
        token = (await self.get_token(ctx.author.id))["token"]
        # Create a copy of the default haders
        headers = copy.deepcopy(default)
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


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    pass
