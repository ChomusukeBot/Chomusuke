# Start by loading the important stuff
import aiohttp
from cog import Cog
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient


class Chomusuke(commands.AutoShardedBot):
    """
    Custom base class for the Chomusuke bot.
    """
    def __init__(self, *args, **kwargs):
        # If there is a MongoDB URL in the keyword arguments
        if "database" in kwargs:
            # Create the MongoDB/Motor instance
            self.mongo = AsyncIOMotorClient(kwargs["database"])
            # Save the bot database
            self.database = self.mongo.chomusuke
            # And pop the argument
            kwargs.pop("database")
        # Otherwise
        else:
            # Set the database to null
            self.mongo = None
            self.database = None

        # Initialize the usual bot
        super().__init__(*args, **kwargs)

        # Create a Client Session for using REST APIs
        self.session = aiohttp.ClientSession(loop=self.loop)

    def add_cog(self, cog):
        """
        Adds a custom cog into the bot.
        """
        # If the cog is not our custom cog, raise an exception
        if isinstance(cog, Cog):
            raise TypeError("Chomusuke only accepts cogs that inherit from the custom class.")

        # Continue the workflow
        super().add_cog(cog)
