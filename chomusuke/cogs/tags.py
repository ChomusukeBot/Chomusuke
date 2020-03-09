from datetime import datetime, timezone

import discord
from discord.ext import commands

from chomusuke.exceptions import DatabaseRequired


class Tags(commands.Cog):
    """
    Shows small snippets of text for specific guilds.
    """
    def __init__(self, bot):
        # If there is no database saved
        if not bot.db:
            # Raise an exception
            raise DatabaseRequired("The tags need to be stored in a database")
        # Otherwise, save the bot instance
        self.bot = bot

    @commands.group(aliases=["tags", "snippet"], invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, name: str, to: discord.Member = None):
        """
        Shows the content of a tag.

        A tag is just a snippet of plain text.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]
        # Try to get an item with the specified name
        item = await collection.find_one({"_id": name})

        # If there is a tag
        if item:
            # Select the correct user to mention
            mention = to or ctx.author
            # And send it
            await ctx.send(mention.mention + "\n" + item["content"])
        # Otherwise
        else:
            # Tell the user that the tag does not exists
            await ctx.send(f"The tag `{name}` does not exists!")

    @tag.command(aliases=["make", "add"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def create(self, ctx: commands.Context, name: str, *, contents: str):
        """
        Creates a tag with the specified name and contents.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]

        # Try to get an item with the specified name
        item = await collection.find_one({"_id": name})
        # If something was found, notify about it and return
        if item:
            await ctx.send("There is already a tag with that name!")
            return

        # Otherwise, add the item into the collection
        await collection.insert_one({"_id": name, "content": contents, "author": ctx.author.id,
                                     "discriminator": f"{ctx.author.name}#{ctx.author.discriminator}",
                                     "created": datetime.now(timezone.utc), "edited": None,
                                     "usage": None})
        # And notify about it
        await ctx.send(f"The tag `{name}` was created!")

    @tag.command(aliases=["remove"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def delete(self, ctx: commands.Context, name: str):
        """
        Deletes the specified tag.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]
        # And try to delete a single item with that name
        count = await collection.delete_one({"_id": name})
        # If we removed something, notify it
        if count:
            await ctx.send(f"The tag `{name}` was deleted!")
        # Otherwise, say that no tags were found
        else:
            await ctx.send(f"No tag with a name of `{name}` could be found.")

    @tag.command(aliases=["replace"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def edit(self, ctx: commands.Context, name: str, contents: str):
        """
        Replaces the text of the specified tag.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]
        # Try to update the tag
        result = await collection.find_one_and_update({"_id": name},
                                                      {"$set": {"content": contents,
                                                                "edited": datetime.now(timezone.utc)}})
        # And tell the user if we managed to update it
        if result:
            await ctx.send(f"The text of the tag `{name}` was changed!")
        else:
            await ctx.send(f"There are no tags with a name of `{name}`")

    @tag.command(aliases=["use"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def usage(self, ctx: commands.Context, name: str, *, text: str):
        """
        Gets or sets the usage for the specified tag.

        You can remove the text by specifying "remove".
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]
        # And select the correct usage
        usage = None if text.lower() == "remove" else text

        # Try to update the tag
        result = await collection.find_one_and_update({"_id": name},
                                                      {"$set": {"usage": usage,
                                                                "edited": datetime.now(timezone.utc)}})
        # And tell the user if we managed to update it
        if result:
            await ctx.send(f"The usage of the tag `{name}` was changed!")
        else:
            await ctx.send(f"There are no tags with a name of `{name}`")

    @tag.command()
    @commands.guild_only()
    async def all(self, ctx: commands.Context):
        """
        Lists all of the tags on this guild.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]

        # If there are no items, say so and return
        if not await collection.count_documents({}):
            await ctx.send("This guild doesn't have any tags.")
            return

        # Create an embed and set the values
        embed = discord.Embed()
        embed.title = f"Tags on {ctx.guild.name}"
        embed.description = ", ".join([tag["_id"] async for tag in collection.find({})])
        # And send it
        await ctx.send(embed=embed)

    @tag.command(aliases=["info"])
    @commands.guild_only()
    async def about(self, ctx: commands.Context, name: str):
        """
        Shows the information of a Tag.
        """
        # Get the collection of tags for this guild
        collection = self.bot.db[f"tag_{ctx.guild.id}"]

        # Try to get the tag with the specified name
        item = await collection.find_one({"_id": name})
        # If there is no tag, say so and return
        if not item:
            await ctx.send("There is no tag with that name!")
            return

        # Try to get the current user
        member = ctx.guild.get_member(item["author"])
        # Format the parameters
        creation = item["created"].strftime("%B %d, %Y %H:%M:%S UTC")
        author = member.mention if member else item["discriminator"]
        edited = item["edited"].strftime("%B %d, %Y %H:%M:%S UTC") if item["edited"] else None
        usage = item.get("usage", None) or "No usage specified"

        # Otherwise, create an embed
        embed = discord.Embed()
        # Add the information
        embed.title = "About the tag \"{0}\"".format(item["_id"])
        embed.description = item["content"] + "\n\n"
        embed.description += f"Usage: {usage}\n"
        embed.description += f"Created by {author} on **{creation}**"
        embed.description += f"\nEdited on **{edited}**" if edited else ""
        # And send it
        await ctx.send(embed=embed)
