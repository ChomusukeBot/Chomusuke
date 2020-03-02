import importlib
import inspect
import logging

from discord.ext.commands import AutoShardedBot
from motor.motor_asyncio import AsyncIOMotorClient

LOGGER = logging.getLogger("chomusuke")


class Chomusuke(AutoShardedBot):
    """
    Base class for everything bot related.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the Chomusuke bot.
        """
        # Try to get the settings for the web server
        db = kwargs.pop("database", "")

        # Call the default Bot init
        super().__init__(*args, **kwargs)

        # If the user wants a MongoDB instance
        if db:
            # Notify the user that the database is being initialized
            LOGGER.info("Initializing MongoDB instance")
            # Create the Motor/MongoDB instance
            self.mongo = AsyncIOMotorClient(db)
            # Make sure that the the database is valid by calling a simple command
            self.mongo.admin.command("ismaster")
            # And save the bot database
            self.db = self.mongo.chomusuke
        # Otherwise
        else:
            # Tell the user that there is no database available
            LOGGER.warning("The MongoDB instance is disabled")
            LOGGER.warning("Cogs that require storing any type of data might not work")
            # And set the database to nothing
            self.mongo = None
            self.db = None

    def import_cog(self, name: str):
        """
        Imports a cog with importlib and adds it to a.
        """
        # Notify that we are attempting to import the cog
        LOGGER.info(f"Loading the cog '{name}'")
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
