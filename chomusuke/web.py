from discord.ext.commands import AutoShardedBot
from sanic import Sanic


class WebServer(Sanic):
    """
    A custom version of sanic.Sanic for supporting the Discord bot.
    """
    def __init__(self, *args, **kwargs):
        # Save the Discord Bot information
        # TODO: Use chomusuke.bot.Chomusuke instead of discord.ext.commands.AutoShardedBot
        self.bot: AutoShardedBot = kwargs.pop("bot", None)
        # Call the default Sanic init
        super().__init__(*args, **kwargs)
