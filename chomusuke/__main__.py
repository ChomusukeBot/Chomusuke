import argparse
import asyncio
import json
import logging
import os
import platform
import sys

from .__init__ import __version__ as version
from .bot import Chomusuke

LOGGER = logging.getLogger("chomusuke")


def configure_logging():
    """
    Configures the logging system of the bot.
    """
    # Set the logger level to INFO
    LOGGER.setLevel(logging.INFO)
    # Create a stream logger for sending messages to STDOUT
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    # Then, we need a formatter to make the messages pretty
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] %(message)s")
    stream.setFormatter(formatter)
    # Finally, add the formatter so is processed
    LOGGER.addHandler(stream)


def config_from_env():
    """
    Generates a dict with configuration values from the environment variables.
    """
    # Notify the user
    LOGGER.info("Loading configuration values from environment variables...")
    # Create a dictionary with the info that we need
    output = {
        "token": os.environ["DISCORD_TOKEN"],
        "prefix": os.environ.get("DISCORD_PREFIX", "&"),
        "cogs": os.environ.get("DISCORD_COGS", "").split(","),
        "database": os.environ.get("MONGODB_URL", "")
    }
    # And return it
    return output


def config_from_json(file):
    """
    Generates a dict with configuration values from a JSON file.
    """
    # Notify the user about the loading
    LOGGER.info(f"Loading JSON configuration from {file}")
    # Open the file for reading
    with open(file):
        # Get the contents as JSON
        output = json.load(file)
    # If there is no token saved, notify the user and return
    if "token" not in output:
        LOGGER.critical("No token was found in the JSON configuration file.")
        sys.exit(4)
    # If everything succeeds, return the output
    return output


def parse_args():
    """
    Parses the command line arguments.
    """
    # Create an instance of the Argument Parser
    parser = argparse.ArgumentParser()
    # Then, add the required arguments for this
    parser.add_argument("--env", dest="env", action="store_true",
                        help="if the bot should be configured with environment variables")
    parser.add_argument("--json", dest="json", action="store",
                        help="the JSON configuration file that should be used")
    # Finally, return the arguments
    return parser.parse_args()


def main():
    """
    Executes the bot from the command line.
    """
    # Configure the logging system
    configure_logging()
    # And notify the user that we are starting the bot
    LOGGER.info(f"Starting up Chomusuke v{version} on {platform.platform()}")

    # Get the parsed command line arguments
    args = parse_args()

    # If the user wants the config from environment variables
    if args.env:
        # If there is no token on the environment variables
        if "DISCORD_TOKEN" not in os.environ:
            # Notify the user and exit
            LOGGER.critical(f"No token was found on the environment variables (DISCORD_TOKEN).")
            sys.exit(1)

        # Otherwise, load the configuration
        config = config_from_env()
    # If the user wants the configuration from a JSON file
    elif args.json:
        # If the JSON file does not exists
        if not os.path.isfile(args.json):
            # Notify the user and return
            LOGGER.critical(f"The JSON Configuration file was not found ({args.json}).")
            sys.exit(3)
        # Otherwise, get the configuration
        config = config_from_json(args.json)
    # If there is no configuration type specified
    else:
        LOGGER.critical("No configuration system was specified.")
        sys.exit(2)

    # Get the event loop
    loop = asyncio.get_event_loop()
    # Then, create a instance for the bot
    bot = Chomusuke(config["prefix"], loop=loop, database=config["database"])

    # If there are cogs in the configuration
    if "cogs" in config:
        # Iterate over the cogs
        for cog in config["cogs"]:
            # If the cog is an empty string
            if cog == "":
                # Skip this iteration and continue
                continue

            # And try to import them
            try:
                bot.import_cog(cog)
            # If we failed
            except Exception as e:
                LOGGER.error(f"Error while loading {cog}: {type(e).__name__} - {str(e)}")

    # Notify the user that we got everything and we are starting the bot
    LOGGER.info("Everything ready! Booting up...")

    # Start processing everything
    try:
        # Log and connect the user
        loop.run_until_complete(bot.login(config["token"]))
        # And connect the bot to Discord
        loop.run_until_complete(bot.connect())
    except KeyboardInterrupt:
        # After a CTRL+C or CTRL+Z, log out the bot and disconnect everything
        loop.run_until_complete(bot.logout())
    finally:
        # After the bot finishes (or crashing), grab all tasks
        tasks = asyncio.all_tasks(loop)
        # Run all of the tasks until they have been completed
        loop.run_until_complete(asyncio.gather(*tasks))
        # After the tasks have been completed, close the loop
        loop.close()


if __name__ == "__main__":
    main()
