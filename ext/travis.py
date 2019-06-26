# Import the commands extension
from discord.ext import commands
from ext.ci import ContinuousIntegration

# The list of endpoints that we are going to use
ENDPOINTS = {
    "image": "https://travis-ci.com/images/logos/TravisCI-Mascot-1.png",
    "u_repo": "https://travis-ci.com/{0}",
    "u_build": "https://travis-ci.com/{0}/builds/{1}",
    "u_builds": "https://travis-ci.com/{0}/builds",
    "validity": "https://api.travis-ci.com/user",
    "repos": "https://api.travis-ci.com/repos",
    "trigger": "https://api.travis-ci.com/repo/{0}/requests",
    "builds": "https://api.travis-ci.com/repo/{0}/builds?limit=10"
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
        self.travis.add_command(self.trigger)
        self.travis.add_command(self.builds)

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

    async def format_builds(self, json: dict, slug: str):
        """
        Formats the JSON response from a native Travis CI response to a simple dict.
        """
        # Create an output dictionary
        output = {}
        # Iterate over the builds
        for build in json["builds"]:
            # Save the slug and default branch
            output[build["number"]] = {"id": build["id"], "state": build["previous_state"]}
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
