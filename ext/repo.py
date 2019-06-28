# Import our libraries
import copy
import discord
from cog import Cog
from discord.ext import commands
from exceptions import NoTokenSet

# Set of colors that we are going to use
OXIDE_BLUE = 0x3EAAAF  # Travis CI
TURF_GREEN = 0x39AA56  # Travis CI
CANARY_YELLOW = 0xEDDE3F  # Travis CI
BRICK_RED = 0xDB4545  # Travis CI
ASPHALT_GREY = 0x666666  # Travis CI


class Repo(Cog):
    """
    Cog for accessing git repos via their respective APIs.
    """
    def __init__(self, bot, name: str, auth: str = "", headers: dict = {}, endpoints: dict = {}, user_token: bool = True):
        # Save our bot for later use
        self.bot = bot
        # Save the collections
        self.tokens = bot.database[f"{name}_tokens"]
        self.picks = bot.database[f"{name}_picks"]
        # Save our default set of parameters
        self.auth = auth
        self.headers = headers
        self.endpoints = endpoints
        self.user_token = user_token

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

    async def generate_headers(self, ctx):
        """
        Generates a set of headers for the use on aiohttp requests.
        """
        # Create a copy of the default haders
        headers = copy.deepcopy(self.headers)

        # If the cog requires authentication headers
        if self.user_token:
            # Get the current user token
            token = (await self.get_token(ctx.author.id))["token"]
            # Set the token specified by the user
            headers["Authorization"] = f"{self.auth} {token}"

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
            raise NoTokenSet("A service token is required.")
        # Otherwise, return found key
        return existing

    async def format_repos(self, json: dict):
        """
        Formats the JSON returned by the API to a neutral format.
        """
        raise NotImplementedError()

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

    @commands.command()
    async def pick(self, ctx, slug: str):
        """
        Chooses a repo with the specified slug for future operations.
        """
        # Create a list of headers
        headers = await self.generate_headers(ctx)

        # If there is a function to check the repo
        if getattr(self, "check_repo", None):
            picks = await self.check_repo(slug)
        # Otherwise
        else:
            # Request the list of user repos
            async with self.bot.session.get(self.endpoints["repos"], headers=headers) as resp:
                # If we didn't got a code 200, notify the user and return
                if resp.status != 200:
                    await ctx.send(f"Unable to get your list of repos: Code {resp.status}")
                    return
                # Parse the response as JSON
                json = await resp.json()

            # Format the repos returned by the response
            output = await self.format_repos(json)
            # Filter the picks
            picks = {k: v for k, v in output.items() if slug.casefold() == k.casefold()}

        # If there was no matches
        if not picks:
            await ctx.send("We were unable to find a repo with that slug.")
            return

        # Update an item and create it if is not present
        await self.picks.replace_one({"_id": ctx.author.id}, {"_id": ctx.author.id, "slug": list(picks.keys())[0]}, True)
        # Finally notify the user
        await ctx.send("You have choosen {0} for your next operations.".format(list(picks.keys())[0]))

    @commands.command()
    async def repos(self, ctx):
        """
        Lists all of the repositories that you have access to.
        """
        # Send a typing
        await ctx.trigger_typing()
        # Create a place to store the repository data
        desc = ""

        # If there is a function to format the repo URL
        if getattr(self, "get_user", None):
            url = self.endpoints["repos"].format(await self.get_user())
        else:
            url = self.endpoints["repos"]

        # Request the list of user repos
        async with self.bot.session.get(url, headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 200, notify the user and return
            if resp.status != 200:
                await ctx.send(f"Unable to get your list of repos: Code {resp.status}")
                return

            # Parse the response as JSON
            json = await resp.json()

        # Iterate over the list of repos
        for key, item in (await self.format_repos(json)).items():
            # And add the repo information
            desc += "{0} ({1})\n".format(key, item)

        # Create an embed
        embed = discord.Embed()
        embed.color = OXIDE_BLUE
        embed.title = "{0}'s repositories".format(ctx.author.name)
        embed.description = desc
        embed.set_thumbnail(url=self.endpoints["image"])

        # Finally, send the embed
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
