import asyncio
import importlib
import inspect
import logging

from discord.ext.commands import AutoShardedBot

from .endpoint import DefaultEndpoint
from .web import WebServer

LOGGER = logging.getLogger("chomusuke")


class Chomusuke(AutoShardedBot):
    """
    Base class for everything bot related.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the Chomusuke bot.
        """
        # Call the default Bot init
        super().__init__(*args, **kwargs)

        # Try to get the settings for the web server
        host = kwargs.pop("web_host", "0.0.0.0")
        port = kwargs.pop("web_port", 4810)
        web = kwargs.pop("use_web", False)

        # If the user wants the web server
        if web:
            # Notify the user that the server is OK
            LOGGER.info(f"Starting Sanic Web Server at {host}:{port}")
            # And create the server instance
            self.server = WebServer(bot=self)
            coro = self.server.create_server(host=host, port=port, return_asyncio_server=True)
            self.loop.run_until_complete(asyncio.ensure_future(coro, loop=self.loop))
            self.server.add_route(DefaultEndpoint.as_view(), "/")
        # Otherwise
        else:
            # Tell the user that there is no web server
            LOGGER.warning("The Sanic Web Server is disabled")
            LOGGER.warning("Cogs that require callbacks and return endpoints might not work")
            # And set the server to nothing
            self.server = None

    def import_cog(self, name: str):
        """
        Imports a cog with importlib and adds it to a.
        """
        # Split the name sent
        split = name.split(":")

        # If the length of the splitted text is not two
        if len(split) != 2:
            raise ValueError("The name of the package is not set to 'package:class'")

        # At this point, we guess that the input is correct
        imported = importlib.import_module(split[0])

        # If the imported library does not has a library with the specified attribute
        if not hasattr(imported, split[1]):
            raise ImportError(f"'{split[0]}' does not contains an attribute called {split[1]}")
        # We know that there is something at imported.name, so save it
        cog = getattr(imported, split[1])
        # If there is an attribute but is not a class
        if not inspect.isclass(cog):
            raise TypeError(f"{name} is not a class")

        # If we got here, call add_cog
        self.add_cog(cog(self))
