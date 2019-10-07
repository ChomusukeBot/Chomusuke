from discord.ext.commands import AutoShardedBot
import logging


LOGGER = logging.getLogger("chomusuke")


class Chomusuke(AutoShardedBot):
    """
    Base class for everything bot related.
    """
