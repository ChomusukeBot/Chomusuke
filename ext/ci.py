# Import all of our libs
import discord
import itertools
import string
from discord.ext import commands
from ext.repo import Repo

# Set of colors that we are going to use
OXIDE_BLUE = 0x3EAAAF  # Travis CI
TURF_GREEN = 0x39AA56  # Travis CI
CANARY_YELLOW = 0xEDDE3F  # Travis CI
BRICK_RED = 0xDB4545  # Travis CI
ASPHALT_GREY = 0x666666  # Travis CI


class ContinuousIntegration(Repo):
    """
    Base cog for interacting with Continuous Integration services.
    """

    async def format_builds(self, json: dict, slug: str):
        """
        Formats the JSON returned by the API to a neutral format.
        """
        raise NotImplementedError()

    @commands.command()
    async def trigger(self, ctx):
        """
        Triggers a build for the specified repo.
        """
        # Send a typing
        await ctx.trigger_typing()
        # Use either the specified repo or the slug
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]

        # Create the data or body
        data = {
            "message": f"Chomusuke: Triggered by {ctx.author.name} from Discord"
        }

        # Get all of the parameters of the endpoint URL
        params = [x[1] for x in string.Formatter().parse(self.endpoints["trigger"]) if x[1] is not None]

        # If there are parameters to format, do it with the URL
        if params:
            url = self.endpoints["trigger"].format(repo.replace("/", "%2F"))
        # Otherwise, is expecting data on the body
        else:
            url = self.endpoints["trigger"]
            data["accountName"] = repo.split("/")[0]
            data["projectSlug"] = repo.split("/")[1]

        # Request the list of user repos
        async with self.bot.session.post(url, data=data,
                                         headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 200 or 202, notify the user and return
            if resp.status != 200 and resp.status != 202:
                await ctx.send(f"We were unable to start a build: Code {resp.status}")
                return

        # After we have the commit created, return the URL of the build
        await ctx.send("A Build has been triggered!\nYou can find your Build at {0}.".format(self.endpoints["u_builds"].format(repo)))

    @commands.command()
    async def builds(self, ctx, slug: str = None):
        """
        Lists the last 10 builds on a specific repo.
        """
        # Use either the specified repo or the slug
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]

        # Get all of the parameters of the endpoint URL
        params = [x[1] for x in string.Formatter().parse("{0}, {1}") if x[1] is not None]

        # If there is only one parameter to format
        if len(params) == 1:
            url = self.endpoints["builds"].format(repo.replace("/", "%2F"))
        # If there are two parameters
        elif len(params) == 2:
            url = self.endpoints["builds"].format(*repo.split("/"))
        # If there are no parameters
        else:
            url = self.endpoints["builds"]

        # Request the list of builds for that repository
        async with self.bot.session.get(url, headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 200, notify the user and return
            if resp.status != 200:
                await ctx.send(f"We were unable to get the list of builds: Code {resp.status}")
                return
            # Generate the JSON
            json = await resp.json()

        # Create an embed and configure the basics
        embed = discord.Embed()
        embed.title = "Last 10 builds of {0}".format(repo)
        embed.url = self.endpoints["u_repo"].format(repo)
        embed.color = OXIDE_BLUE
        embed.description = ""
        embed.set_thumbnail(url=self.endpoints["image"])
        # Iterate over the list of builds
        for key, item in itertools.islice((await self.format_builds(json, repo)).items(), 10):
            # And add the build information
            embed.description += "#[{0}]({1}) ({2})\n".format(key, self.endpoints["u_build"].format(repo, item["id"]), item["state"])

        # Finally, send the embed with the builds
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
