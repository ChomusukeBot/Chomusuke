# Import our little set of tools
import argparse
import asyncio
import logging
import os
import sys
from bot import Chomusuke
from discord.ext import commands
from dotenv import load_dotenv

# The information logger
LOGGER: logging.Logger = logging.getLogger("chomusuke")


def main():
    """
    Our main function.
    """
    # Start by creating our parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-env", dest="manual_env", action="store_true", help="if the .env file should be loaded manually by the bot")
    parser.add_argument("--log", dest="log", action="store_false", help="if we should log the bot actions to stdout")
    # Parse our arguments
    args = parser.parse_args()

    # If the user requested the manual adition of .env, use python-dotenv
    if args.manual_env:
        load_dotenv()
        LOGGER.info(".env file have been manually loaded")

    # If the user wants logging to stdout, configure the logger
    if args.log:
        # Set the logger level to info
        LOGGER.setLevel(logging.INFO)
        # Create a stream handler and also set it to info
        stream = logging.StreamHandler()
        stream.setLevel(logging.INFO)
        # Create the formatter and add it into our handler
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s")
        stream.setFormatter(formatter)
        # Finally, add the formatter to our logger
        LOGGER.addHandler(stream)

    # If the discord token is not on the environment variables, log and exit with a code 2
    if "DISCORD_TOKEN" not in os.environ:
        LOGGER.critical("There is no Discord Token on the environment variables!")
        sys.exit(2)

    # If the bot prefix is not on the environment variables, log and exit with a code 2
    if "DISCORD_PREFIX" not in os.environ:
        LOGGER.critical("There is no Bot Prefix on the environment variables!")
        sys.exit(3)

    # Create a dictionary of keyword arguments
    kwargs = {
        "command_prefix": os.environ["DISCORD_PREFIX"]
    }

    # If there is a MongoDB database added
    if "MONGODB_URL" in os.environ:
        # Add the database to our keyword arguments and notify the user
        kwargs["database"] = os.environ["MONGODB_URL"]
        LOGGER.info("Found MongoDB URL on the environment variables")

    # Create our bot instance
    bot = Chomusuke(**kwargs)

    # Iterate over the python files from the ext folder
    for file in [x for x in os.listdir("ext") if x.endswith(".py")]:
        # Try to load the extension
        try:
            LOGGER.info(f"Attempting to load {file}...")
            bot.load_extension("ext." + os.path.splitext(file)[0])
        # If there was a problem, intercept the exception and log what happened
        except commands.ExtensionNotFound:
            LOGGER.warning(f"The extension {file} was already loaded")
        except commands.NoEntryPointError:
            LOGGER.error(f"The extension {file} does not has a setup(bot) function")
        except commands.ExtensionFailed as e:
            LOGGER.exception(e.original)

    # We have everything, start loading the bot
    try:
        # Get the event loop
        loop = asyncio.get_event_loop()
        # Log and connect the user
        loop.run_until_complete(bot.login(os.environ["DISCORD_TOKEN"]))
        loop.run_until_complete(bot.connect())
    except KeyboardInterrupt:
        # After a CTRL+C or CTRL+Z, log out the bot and disconnect everything
        loop.run_until_complete(bot.logout())
    finally:
        # Afer finishing, grab all tasks
        tasks = asyncio.all_tasks(loop)
        # Run all of the tasks until they have completed
        loop.run_until_complete(asyncio.gather(*tasks))
        # Only after the tasks have been completed, close the loop
        loop.close()
        # Finally, exit with a code zero
        sys.exit(0)


if __name__ == "__main__":
    main()
