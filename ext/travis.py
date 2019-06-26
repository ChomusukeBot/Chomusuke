# Import the commands extension
import discord
from discord.ext import commands
from ext.ci import ContinuousIntegration

# This is our base URL for all API calls
BASE = "https://api.travis-ci.com"
# The image for our embeds
IMAGE = "https://travis-ci.com/images/logos/TravisCI-Mascot-1.png"
# A list of available endpoints
EP_REPOS = "/repos"
EP_REQUESTS = "/repo/{0}/requests"
EP_BUILDS = "/repo/{0}/builds?limit=10"
# The list of endpoints that we are going to use
ENDPOINTS = {
    "validity": "https://api.travis-ci.com/user"
}
# Travis CI brand colors (https://travis-ci.com/logo)
OXIDE_BLUE = 0x3EAAAF
TURF_GREEN = 0x39AA56
CANARY_YELLOW = 0xEDDE3F
BRICK_RED = 0xDB4545
ASPHALT_GREY = 0x666666
# Our default headers for all of the requests
HEADERS = {
    "Travis-API-Version": "3",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}


class Travis(ContinuousIntegration):
    """
    A cog for accessing the Travis CI API.
    """
    def __init__(self, *args, **kwargs):
        # Call the normal function
        super().__init__(*args, **kwargs)
        # Add the commands to our group
        self.travis.add_command(self.addtoken)

    @commands.group()
    async def travis(self, ctx):
        """
        Group of commands for interacting with the Travis CI service.
        """

    @travis.command()
    async def pick(self, ctx, slug: str):
        """
        Chooses a repo with the specified slug for future operations.
        """
        # Create a list of headers
        headers = await self.generate_headers(ctx, HEADERS, "token")

        # Request the list of user repos
        async with self.bot.session.get(BASE + EP_REPOS, headers=headers) as resp:
            # If we didn't got a code 200, notify the user and return
            if resp.status != 200:
                await ctx.send(f"Unable to get your list of repos: Code {resp.status}")
                return

            # Parse the response as JSON
            json = await resp.json()

        # Store the picks
        picks = [x for x in json["repositories"] if slug.casefold() == x["slug"].casefold()]

        # If there was no matches
        if not picks:
            await ctx.send("We were unable to find a repo with that slug.")
            return

        # Update an item and create it if is not present
        await self.picks.replace_one({"_id": ctx.author.id}, {"_id": ctx.author.id, "slug": picks[0]["slug"]}, True)
        # Finally notify the user
        await ctx.send("You have choosen {0} for your next operations.".format(picks[0]["slug"]))

    @travis.command()
    async def repos(self, ctx):
        """
        Lists all of the repositories that the User has access to.
        """
        # Send a typing
        await ctx.trigger_typing()
        # Create a place to store the repository data
        desc = ""

        # Request the list of user repos
        async with self.bot.session.get(BASE + EP_REPOS, headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 200, notify the user and return
            if resp.status != 200:
                await ctx.send(f"Unable to get your list of repos: Code {resp.status}")
                return

            # Parse the response as JSON
            json = await resp.json()

        # Iterate over the list of repos
        for repo in [x for x in json["repositories"] if x["active"] and not x["private"]]:
            # And add the repo information
            desc += "{0} ({1})\n".format(repo["slug"], repo["default_branch"]["name"])

        # Create an embed
        embed = discord.Embed()
        embed.color = OXIDE_BLUE
        embed.title = "{0}'s repositories on Travis CI".format(ctx.author.name)
        embed.description = desc
        embed.set_thumbnail(url=IMAGE)

        # Finally, send the embed
        await ctx.send(embed=embed)

    @travis.command()
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

        # Request the list of user repos
        async with self.bot.session.post(BASE + EP_REQUESTS.format(repo.replace("/", "%2F")), data=data,
                                         headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 202, notify the user and return
            if resp.status != 202:
                await ctx.send(f"We were unable to start a build: Code {resp.status}")
                return

        # After we have the commit created, return the URL of the build
        await ctx.send(f"A Build has been triggered!\nYou can find your Build at https://travis-ci.com/{repo}/builds.")

    @travis.command()
    async def builds(self, ctx, slug: str = None):
        """
        Lists the builds on a specific Travis CI repo.
        """
        # Send a typing
        await ctx.trigger_typing()

        # Use either the specified repo or the slug
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]

        # Request the list of builds for that repository
        async with self.bot.session.get(BASE + EP_BUILDS.format(repo.replace("/", "%2F")), headers=await self.generate_headers(ctx)) as resp:
            # If we didn't got a code 200, notify the user and return
            if resp.status != 200:
                await ctx.send(f"We were unable to get the list of builds: Code {resp.status}")
                return
            # Generate the JSON
            json = await resp.json()

        # Create an embed and configure the basics
        embed = discord.Embed()
        embed.color = OXIDE_BLUE
        embed.title = "Builds of {0}".format(repo)
        embed.url = f"https://travis-ci.com/{repo}"
        embed.set_thumbnail(url=IMAGE)
        embed.description = ""
        # Iterate over the builds
        for build in json["builds"]:
            embed.description += "#[{0}]({1}) ({2})\n".format(build["number"], "https://travis-ci.com/{0}/builds/{1}".format(repo, build["id"]),
                                                              build["previous_state"])

        # Finally, send the embed with the builds
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Travis(bot, "travis", "token", HEADERS, ENDPOINTS))
