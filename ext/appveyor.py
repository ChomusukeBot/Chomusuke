# Import the commands extension
import logging
from ext.ci import ContinuousIntegration
from discord.ext import commands

# The list of endpoints that we are going to use
ENDPOINTS = {
    "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Appveyor_logo.svg/600px-Appveyor_logo.svg.png",
    "u_repo": "https://ci.appveyor.com/project/{0}",
    "u_build": "https://ci.appveyor.com/project/{0}/builds/{1}",
    "u_builds": "https://ci.appveyor.com/project/{0}/history",
    "validity": "https://ci.appveyor.com/api/users",
    "repos": "https://ci.appveyor.com/api/projects",
    "trigger": "https://ci.appveyor.com/api/builds",
    "builds": "https://ci.appveyor.com/api/projects/{0}/{1}/history?recordsNumber=10"
}
# Our default headers for all of the requests
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}
# The information logger
LOGGER: logging.Logger = logging.getLogger("chomusuke")


class AppVeyor(ContinuousIntegration):
    """
    A cog for accessing the AppVeyor API.
    """
    def __init__(self, *args, **kwargs):
        # Call the normal function
        super().__init__(*args, **kwargs)
        # Add the commands to our group
        self.appveyor.add_command(self.addtoken)
        self.appveyor.add_command(self.pick)
        self.appveyor.add_command(self.repos)
        self.appveyor.add_command(self.trigger)
        self.appveyor.add_command(self.builds)

    async def format_repos(self, json: dict):
        """
        Formats the JSON response from a native AppVeyor response to a simple dict.
        """
        # Create an output dictionary
        output = {}
        # Iterate over the repos
        for repo in json:
            # Save the slug and default branch
            output[repo["repositoryName"]] = repo["repositoryBranch"]
        # Finally, return the output dictionary
        return output

    async def format_builds(self, json: dict, slug: str):
        """
        Formats the JSON response from a native AppVeyor response to a simple dict.
        """
        # Create an output dictionary
        output = {}
        # Iterate over the builds
        for build in json["builds"]:
            # Save the slug and default branch
            output[build["version"]] = {"id": build["buildId"], "state": build["status"]}
        # Finally, return the output dictionary
        return output

    @commands.group()
    async def appveyor(self, ctx):
        """
        Group of commands for interacting with the AppVeyor service.
        """


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    if bot.mongo:
        bot.add_cog(AppVeyor(bot, "appveyor", "Bearer", HEADERS, ENDPOINTS))
    else:
        LOGGER.error(f"{AppVeyor} has not been loaded because MongoDB is required")
