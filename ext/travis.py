# Import the commands extension
from discord.ext import commands
from ext.ci import ContinuousIntegration

# This is our base URL for all API calls
BASE = "https://api.travis-ci.com"
# A list of available endpoints
EP_REPOS = "/repos"
EP_REQUESTS = "/repo/{0}/requests"
EP_BUILDS = "/repo/{0}/builds?limit=10"
# The list of endpoints that we are going to use
ENDPOINTS = {
    "image": "https://travis-ci.com/images/logos/TravisCI-Mascot-1.png",
    "validity": "https://api.travis-ci.com/user",
    "repos": "https://api.travis-ci.com/repos"
}
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
        self.travis.add_command(self.pick)
        self.travis.add_command(self.repos)

    async def format_repos(self, json: dict):
        """
        Formats the JSON response from a native Travis CI response to a simple dict.
        """
        # Create an output dictionary
        output = {}
        # Iterate over the repos
        for repo in json["repositories"]:
            # Save the slug and default branch
            output[repo["slug"]] = repo["default_branch"]["name"]
        # Finally, return the output dictionary
        return output

    @commands.group()
    async def travis(self, ctx):
        """
        Group of commands for interacting with the Travis CI service.
        """


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Travis(bot, "travis", "token", HEADERS, ENDPOINTS))
