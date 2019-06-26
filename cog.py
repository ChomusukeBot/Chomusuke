# Import the commands extension
from discord.ext import commands


class Cog(commands.Cog):
    """
    A custom Cog Class to comply with the GDPR.
    """
    async def dump_data(self, ctx) -> dict:
        """
        Dumps all of the Cog data into a dictionary.
        """
        return {}

    async def forget_data(self, ctx) -> bool:
        """
        Removes all of the data from the cog.
        """
        return False
