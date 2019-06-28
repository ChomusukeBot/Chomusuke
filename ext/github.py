# Import the commands extension
import discord
import logging
import os
from ext.repo import Repo
from discord.ext import commands

# The list of endpoints that we are going to use
ENDPOINTS = {
    "image": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
    "repos": "https://api.github.com/users/{0}/repos?sort=updated"
}
# Default request parameters
PARAMETERS = {
    "client_id": os.environ.get("GITHUB_ID"),
    "client_secret": os.environ.get("GITHUB_SECRET")
}
# Our default headers for all of the requests
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}
# The information logger
LOGGER: logging.Logger = logging.getLogger("chomusuke")


class GitHub(Repo):
    """
    A class containing commands/functions for Github Integration.
    """
    def __init__(self, *args, **kwargs):
        # Call the normal function
        super().__init__(*args, **kwargs)
        # Add the commands to our group
        self.github.add_command(self.pick)
        self.github.add_command(self.repos)

    async def format_repos(self, json: dict):
        """
        Formats the JSON response from a native AppVeyor response to a simple dict.
        """
        # Create an output dictionary
        output = {}
        # Iterate over the repos
        for repo in json[0:15]:
            # Save the slug and default branch
            output[repo["full_name"]] = repo.get("language", "")
        # Finally, return the output dictionary
        return output

    async def get_user(self):
        """
        Gets the GitHub user that corresponds for the Discord ID.
        """
        return "justalemon"

    async def check_repo(self, slug: str):
        """
        Checks if the specified repo is valid.
        """
        async with self.bot.session.get(f"https://api.github.com/repos/{slug}", headers=HEADERS, params=PARAMETERS) as resp:
            if resp.status != 200:
                return
            json = await resp.json()
            return {json["full_name"]: json["default_branch"]}

    @commands.group()
    async def github(self, ctx):
        """
        A set of commands to get information from GitHub.
        """
        # If there was no subcommands invoked and there is a Client ID
        if not ctx.invoked_subcommand and PARAMETERS["client_id"]:
            # Generate the auth URL
            redirect = f"https://chomusuke.justalemon.ml/{ctx.author.id}/github"
            url = "https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}".format(PARAMETERS["client_id"], redirect)
            # Then send the URL
            await ctx.send(url)

    @github.command(aliases=["r"])
    async def repo(self, ctx):
        """
        Shows the information for your repository.
        """
        # Use the stored repo
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]

        # Make the request
        async with self.bot.session.get(f"https://api.github.com/repos/{repo}", headers=HEADERS, params=PARAMETERS) as resp:
            # And parse the JSON
            json = await resp.json()

        # Create an embed and fill the
        embed = discord.Embed()
        embed.title = f"Information of {repo}"
        embed.url = json["html_url"]
        embed.description = "{0} 👀 / {1} ⭐ / {2} 🍴".format(json["watchers_count"], json["stargazers_count"], json["forks_count"])
        embed.description += "\n\n{0}\n\n".format(json["description"])
        if json["license"]:
            embed.description += "Released under the " + json["license"]["name"] + "\n\n"
        embed.description += "Created on {0}\n".format(json["created_at"])
        embed.description += "Updated on {0}\n".format(json["updated_at"])
        embed.description += "Last Push on {0}\n".format(json["pushed_at"])
        if json["fork"]:
            embed.set_footer("This is a fork.")
        embed.set_thumbnail(url=json["owner"]["avatar_url"])
        # Finally, send the embed
        await ctx.send(embed=embed)

    @github.command(aliases=["i"])
    async def issue(self, ctx, _id: int):
        """
        Gets the complete information about an issue.
        """
        # Use the stored repo
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]

        # Make the request
        async with self.bot.session.get(f"https://api.github.com/repos/{repo}/issues/{_id}", headers=HEADERS, params=PARAMETERS) as resp:
            # And parse the JSON
            json = await resp.json()

        # Create an embed and add the basic data
        embed = discord.Embed()
        embed.title = json["title"]
        embed.url = json["html_url"]
        embed.description = json["body"]
        embed.set_footer(text=f"Issue opened by {json['user']['login']}")

        # If the total data length of the embed is higher than 200
        if len(embed) > 2000:
            # Trim the last 100 characters just in case
            embed.description = json["body"][0:1900] + "..."
        # Finally, send the embed
        await ctx.send(embed=embed)

    @github.group(aliases=["l"])
    async def labels(self, ctx):
        """
        Gets all the labels in a repository.
        """
        # Use the stored repo
        repo = (await self.picks.find_one({"_id": ctx.author.id}))["slug"]
        # Make the request
        async with self.bot.session.get(f"https://api.github.com/repos/{repo}/labels", headers=HEADERS, params=PARAMETERS) as resp:
            # And parse the JSON
            json = await resp.json()

        # Create an embed and format it
        embed = discord.Embed()
        embed.title = "Labels of {0}".format(repo)
        embed.description = ""
        for label in json:
            embed.description += "*{0}* (#{1})\n".format(label["name"], label["color"].upper())
        # Finally, send the embed
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    if not bot.mongo:
        LOGGER.error(f"{GitHub} has not been loaded because MongoDB is required")
    elif "GITHUB_ID" not in os.environ or "GITHUB_SECRET" not in os.environ:
        LOGGER.error(f"{GitHub} has not been loaded because a GitHub Client ID/Secret is required")
    else:
        bot.add_cog(GitHub(bot, "github", "Bearer", HEADERS, ENDPOINTS, False))
