import logging

import discord
from discord.ext import commands

from chomusuke.exceptions import DatabaseRequired

LOGGER = logging.getLogger("chomusuke")


class Welcome(commands.Cog):
    """
    Shows a custom join message for new users.
    """
    def __init__(self, bot):
        # If there is no database saved
        if not bot.db:
            # Raise an exception
            raise DatabaseRequired("The Welcome Messages need a database")
        # And save the bot
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """
        Group of commands for modifying the custom welcome messages.
        """
        # Try to get the settings for the current guild and channel
        settings = await self.bot.db["welcome"].find_one({"_id": ctx.guild.id}) or {}
        channel = self.bot.get_channel(settings.get("channel", 0))
        # Create the message with the correct contents
        message = "Welcome messages are " + ("enabled" if settings.get("enabled", False) else "disabled") + "\n"
        message += (f"They will be sent to {channel.mention}" if channel else "No channel is set or is invalid") + "\n"
        message += ("The message is\n```\n" + settings["msg"] + "\n```" if settings.get("msg", None)
                    else "There is no message set")
        # And send it
        await ctx.send(message)

    @welcome.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def activation(self, ctx: commands.Context, enabled: bool):
        """
        Enables or Disables the custom welcome messages.
        """
        # Save the activation of the welcome messages
        await self.bot.db["welcome"].find_one_and_update({"_id": ctx.guild.id},
                                                         {"$set": {"enabled": enabled}},
                                                         upsert=True)
        # And notify about it
        await ctx.send("The welcome messages have been " + ("enabled" if enabled else "disabled"))

    @welcome.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def message(self, ctx: commands.Context, *, message: str):
        """
        Sets the welcome message for this server.
        """
        # Save the welcome message
        await self.bot.db["welcome"].find_one_and_update({"_id": ctx.guild.id},
                                                         {"$set": {"msg": message}},
                                                         upsert=True)
        # And notify about it
        await ctx.send(f"The welcome message was set to:\n```\n{message}\n```")

    @welcome.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Sets the channel for the custom join messages.
        """
        # If the channel is not part of the current guild
        if channel.guild != ctx.guild:
            # Notify about it and return
            await ctx.send("The channel is not part of the current guild.")
            return

        # Save the ID of the Channel
        await self.bot.db["welcome"].find_one_and_update({"_id": ctx.guild.id},
                                                         {"$set": {"channel": channel.id}},
                                                         upsert=True)
        # And notify about it
        await ctx.send(f"The channel for welcome messages was set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Shows the welcome message to the member that just joined.
        :param member: The member that just joined.
        """
        # Get the settings for the current guild
        settings = await self.bot.db["welcome"].find_one({"_id": member.guild.id})

        # If there are no settings, return
        if not settings:
            return

        # If the settings are disabled, return
        if not settings.get("enabled", False):
            return

        # Try to get the message
        message = settings.get("msg", None)
        # If there is no message, log it and return
        if not message:
            LOGGER.error(f"Guild {member.guild.id} has welcome messages enabled but no Message set!")
            return

        # Try to get the the channel to use
        channel_id = settings.get("channel", 0)
        # If there is no channel, log it and return
        if not channel_id:
            LOGGER.error(f"Guild {member.guild.id} has welcome messages enabled but no Channel set!")
            return

        # Request the channel on the guild
        channel = self.bot.get_channel(channel_id)
        # If the channel is not available (not present or no access), log it and return
        if not channel:
            LOGGER.error(f"The Channel {channel_id} for Guild {member.guild.id} was not found!")
            return

        # If the channel is not part of the guild, log it and return
        if channel.guild != member.guild:
            LOGGER.error(f"The Channel {channel_id} is not part of the Guild {member.guild.id}!")
            return

        # If we got here, send a message to the channel
        await channel.send(f"{member.mention} {message}")
        # And log about it
        LOGGER.info(f"Welcome message sent to {member.id} on channel {channel_id} for guild {member.guild.id}")
