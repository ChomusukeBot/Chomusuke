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
        # Register the setting
        bot.register_setting("welcome_enabled", bool)
        bot.register_setting("welcome_message", str)
        bot.register_setting("welcome_channel", int)
        # And save the bot
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """
        Group of commands for modifying the custom welcome messages.
        """

    @welcome.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def activation(self, ctx: commands.Context, toggle: bool):
        """
        Changes the activation of the custom welcome messages.
        """
        # Save the activation
        await self.bot.save_setting(ctx.guild, "welcome_enabled", toggle)
        # And notify about it
        await ctx.send("The welcome messages have been " + ("enabled" if toggle else "disabled"))

    @welcome.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def message(self, ctx: commands.Context, *, message: str = None):
        """
        Gets or sets the welcome message for this server.
        """
        # If there is a help message
        if message:
            # Save the message
            await self.bot.save_setting(ctx.guild, "welcome_message", message)
            # And notify about it
            await ctx.send(f"The welcome message was set to:\n```\n{message}\n```")
        else:
            # Try to get the message
            message = await self.bot.get_setting(ctx.guild, "welcome_message")
            # If there is no message, notify the user and return
            if not message:
                await ctx.send("There is no welcome message set for this guild.")
            # Otherwise, just send it
            else:
                await ctx.send(f"The welcome message is set to:\n```\n{message}\n```")

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
        await self.bot.save_setting(ctx.guild, "welcome_channel", channel.id)
        # And notify about it
        await ctx.send(f"The channel for welcome messages was set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Shows the welcome message to the member that just joined.
        :param member: The member that just joined.
        """
        # Get the activation of the join messages for the current guild
        activation = await self.bot.get_setting(member.guild, "welcome_enabled")
        # If is disabled or it was never toggled, log it return
        if not activation:
            return

        # Try to get the message
        message = await self.bot.get_setting(member.guild, "welcome_message")
        # If there is no message, log it and return
        if not message:
            LOGGER.warning(f"Server {member.guild.id} has welcome messages enabled but no message set!")
            return

        # Try to get the the channel to use
        channel_id = await self.bot.get_setting(member.guild, "welcome_channel")
        # If there is no channel, log it and return
        if not channel_id:
            LOGGER.warning(f"Server {member.guild.id} has welcome messages enabled but no channel set!")
            return

        # Request the channel on the guild
        channel = self.bot.get_channel(channel_id)
        # If the channel is not available (not present or no access), log it and return
        if not channel:
            LOGGER.warning(f"The channel {channel_id} for guild {member.guild.id} was not found!")
            return

        # If the channel is not part of the guild, log it and return
        if channel.guild != member.guild:
            LOGGER.warning(f"The channel {channel_id} is not part of the guild {member.guild.id}!")
            return

        # If we got here, send a message to the channel
        await channel.send(f"{member.mention} {message}")
        # And log about it
        LOGGER.info(f"Welcome message sent to {member.id} on channel {channel_id} for guild {member.guild.id}")
