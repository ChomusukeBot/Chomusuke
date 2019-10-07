import importlib
import inspect
import logging

from discord.ext.commands import AutoShardedBot, Cog

LOGGER = logging.getLogger("chomusuke")


class Chomusuke(AutoShardedBot):
    """
    Base class for everything bot related.
    """
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
