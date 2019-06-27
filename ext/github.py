# Import the commands extension
import aiohttp
import discord
import logging
import os

from cog import Cog
from discord.ext import commands


HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "Chomusuke (+https://github.com/justalemon/Chomusuke)"
}
# The information logger
LOGGER: logging.Logger = logging.getLogger("chomusuke")


class Github(Cog):
    """
    A class containing commands/functions for Github Integration.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot

    async def fetch(self, session, url, params={}):
        auth = aiohttp.BasicAuth(os.environ.get("AUTH_EMAIL"), os.environ.get("AUTH_PASS"))
        session.auth = auth
        async with session.get(url=url, headers=HEADERS, params=params) as response:
            return await response.json()

    @commands.group()
    async def github(self, ctx):
        """
        A set of commands to get information from GitHub.
        """

    @github.command(aliases=["r"])
    async def repo(self, ctx, repo_name: str, author: str = None):
        """
            A command to get information about a repository.
            example - c!github r <repository name> <owner of repository>

            Note -
            <owner of repository> is not a compulsary argument.

        """
        embed = discord.Embed(colour=discord.Colour.blue())
        if author is None:
            embed = await self.search_repos(repo_name, 1)
        else:
            url = f"https://api.github.com/repos/{author}/{repo_name}"
            data = await self.fetch(self.bot.session, url)
            if data["message"]:
                return await ctx.send("Invalid Repository name or owner name!")
            embed.title = f"Name : {data['name']}"
            embed.description = f"**:star:{data['stargazers_count']}/:fork_and_knife:{data['forks']}\n\n"
            embed.description += f"**Owner:** {data['owner']['login']}\n"
            embed.description += f"**Description:** {data['description'][0:50]}\n"
            if len(data["description"]) > 50:
                embed.description += "..."
            else:
                pass
            embed.url = data["html_url"]

        await ctx.send(embed=embed)

    @github.command(aliases=["s"])
    async def search(self, ctx, repo_name: str):
        """
        Searches for repositories with the specified name or slug.
        Please note that the search is limited to 5 results.
        """
        embed = await self.search_repos(repo_name, 5)
        await ctx.send(embed=embed)

    async def search_repos(self, repo_name, no_of_repos: int):
        embed = discord.Embed(colour=discord.Colour.blue())
        url = "https://api.github.com/search/repositories"
        params = {
            "q": repo_name,
            "sort": "stars"
        }
        data = await self.fetch(self.bot.session, url, params)
        if data["total_count"] == 0:
            embed.title = "Repository not found!"
            return embed
        embed.url = f"https://github.com/search?q={repo_name}"
        i = 0
        for x in data["items"]:
            if no_of_repos == 5:
                # For search command.
                embed.title = f"Search results for {repo_name}"
                field_name = f"Repo: {x['owner']['login']}/{x['name']}"
            else:
                # For get repository command.
                embed.title = f"Name: {repo_name}"
                field_name = f"Owner: {x['owner']['login']}"
                embed.url = x["html_url"]
            i += 1
            if x["description"] is None:
                message = "No description avilable."
            else:
                message = x["description"][0:50]

            value_field = f"**:star:{x['stargazers_count']}/:fork_and_knife:{x['forks']}\nDescription :** {message}...\nLink : {x['html_url']}\n"
            if no_of_repos != 1:
                if i != no_of_repos:
                    value_field += "."
                else:
                    pass
            embed.add_field(
                name=field_name,
                value=value_field,
                inline=False
            )
            if i == no_of_repos:
                break
        return embed

    @github.command(aliases=["i"])
    async def issue(self, ctx, owner: str, repo: str, issue_id: int):
        """
        Gets the complete information about an issue.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_id}"
        data = await self.fetch(self.bot.session, url)
        if data["message"]:
            return await ctx.send("Invalid Repository name or owner name or issue number!")
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.title = data["title"]
        embed.url = data["html_url"]
        embed.description = data["body"]

        if data["assignee"] is not None:
            # If no one is assigned to the issue.
            msg = data["assignee"]["login"]
        else:
            msg = "None"
        embed.set_footer(text=f"Issue opened by {data['user']['login']} and is assigned to {msg}")

        if len(embed) > 2000:
            # Checking if the embed exceeds 2000 chars to avoid BAD REQUEST.
            embed.description = data["body"][0:1900] + "..."
        await ctx.send(embed=embed)

    @commands.group(aliases=["l"])
    async def labels(self, ctx, owner: str, repo: str):
        """
        Gets all the labels in a repository.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/labels"
        data = await self.fetch(self.bot.session, url)
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.title = "Labels"
        embed.description = ""
        for i, label in enumerate(data, start=1):
            embed.description += f"{i}. **{label['name']}**\n"
        await ctx.send(embed=embed)


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    bot.add_cog(Github(bot))
