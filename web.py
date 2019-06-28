import sanic
from bot import Chomusuke


class WebServer(sanic.Sanic):
    """
    Custom instance of Sanic for handling callback stuff
    """
    def __init__(self, bot, *args, **kwargs):
        # Store the bot for later use
        self.bot: Chomusuke = bot
        # Initialize everything as usual
        super().__init__(*args, **kwargs)
