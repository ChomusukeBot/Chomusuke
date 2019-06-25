from discord.ext.commands import CheckFailure


class NoTokenSet(CheckFailure):
    """
    Raised when a commands needs a special token and is not present.
    """
