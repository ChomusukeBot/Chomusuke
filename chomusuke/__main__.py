import argparse
import json
import os
import sys

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
    # Create a dictionary with the info that we need
    output = {
        "token": os.environ["DISCORD_TOKEN"],
        "prefix": os.environ.get("DISCORD_PREFIX", "&")
    }
    # And return it
    return output


def config_from_json(file):
    """
    Generates a dict with configuration values from a JSON file.
    """
    # Open the file for reading
    with open(file):
        # Get the contents as JSON
        output = json.load(file)
    # If there is no token saved, notify the user and return
    if "token" not in output:
        print("Error: There is no token in the JSON configuration")
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
    # Get the parsed command line arguments
    args = parse_args()

    # If the user wants the config from environment variables
    if args.env:
        # If there is no token on the environment variables, exit
        if "DISCORD_TOKEN" not in os.environ:
            pass

        # Otherwise, load the configuration
        config = config_from_env()
    # If the user wants the configuration from a JSON file
    elif args.json:
        # If the JSON file does not exists
        if not os.path.isfile(args.json):
            # Notify the user and return
            print(f"Error: The JSON Configuration file was not found ({args.json})")
            sys.exit(3)
        # Otherwise, get the configuration
        config = config_from_json(args.json)
    # If there is no configuration type specified
    else:
        print("Error: You need to specify a configuration system")
        sys.exit(2)

    # Then, create a instance for the bot
    bot = Chomusuke(config["prefix"])
    # And start the bot
    bot.run(config["token"])


if __name__ == "__main__":
    main()
