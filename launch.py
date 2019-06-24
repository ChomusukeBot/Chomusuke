# Import our little set of tools
import os
import sys
# Import the bot class
from bot import Chomusuke


def main():
    """
    Our main function.
    """
    # If the discord token is not on the environment variables
    if "DISCORD_TOKEN" not in os.environ:
        # Exit with a code 2
        sys.exit(2)

    # If the bot prefix is not on the environment variables
    if "DISCORD_PREFIX" not in os.environ:
        # Exit with a code 3
        sys.exit(3)

    # Create our bot instance
    bot = Chomusuke(command_prefix=os.environ["DISCORD_PREFIX"])

    # Iterate over the python files from the ext folder
    for file in [x for x in os.listdir("ext") if x.endswith(".py")]:
        # And add the extension without the extension
        bot.load_extension("ext." + os.path.splitext(file)[0])


if __name__ == "__main__":
    main()
