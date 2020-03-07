import importlib
import inspect
import logging

from discord import Guild
from discord.ext.commands import AutoShardedBot
from motor.motor_asyncio import AsyncIOMotorClient

from chomusuke.exceptions import DatabaseRequired

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

        # Create a dictionary of settings
        self.settings = {}

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

    async def on_ready(self):
        """
        Event executed when Chomusuke is ready to work.
        """
        # Log a message about it
        LOGGER.info("Bot is ready to work!")

    async def save_setting(self, guild: Guild, setting: str, value):
        """
        Saves the specified setting.
        :param guild: The guild to set the settings from.
        :param setting: The name of the setting to store.
        :param value: The value to store.
        """
        # If the setting is not registered, throw an exception
        if setting not in self.settings:
            raise ValueError("The setting does not exists.")

        # Get the type of the setting
        _type = self.settings[setting]

        # if the passed object is not the correct type, raise an exception
        if not isinstance(value, _type):
            raise TypeError("The object does not matches the type of the setting.")

        # Create the filter and update
        _filter = {"_id": str(guild.id)}
        update = {"$set": {setting: value}}
        # If we got here, add or update the item
        self.db["settings"].update_one(_filter, update, upsert=True)

    async def get_setting(self, guild: Guild, setting: str, default: object = None):
        """
        Gets a setting based on the Guild on the context.
        :param guild: The guild to get the settings from.
        :param setting: The name of the setting that we need.
        :param default: The default value for this setting if it was not found or it was not requested.
        :return: The value of the setting, or None if nothing was found.
        """
        # If there is no database, throw an exception
        if not self.db:
            raise DatabaseRequired("Loading settings requires a MongoDB Database")

        # If the setting is not registered, throw an exception
        if setting not in self.settings:
            raise ValueError("The setting does not exists.")

        # Create an empty value of the setting
        empty = default if default else self.settings[setting]()

        # Try to find an item with the same item
        found = await self.db["settings"].find_one({"_id": str(guild.id)})
        # If is not there, return the default value
        if not found:
            return empty

        # Check if the setting has the specified setting
        if setting in found:
            # If so, return it
            return found[setting]
        # Otherwise, return the default value
        return empty

    def register_setting(self, setting: str, otype: type):
        """
        Registers a setting for the get_setting function.
        :param setting: The name of the setting that we need.
        :param otype: The type of the setting.
        """
        # Convert the text to lowercase
        lowercase = setting.lower()

        # If is already there, ignore it silently
        if lowercase in self.settings:
            return

        # Otherwise, add it
        self.settings[lowercase] = otype
