import argparse
import os
import sys

from .bot import Chomusuke


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


def parse_args():
    """
    Parses the command line arguments.
    """
    # Create an instance of the Argument Parser
    parser = argparse.ArgumentParser()
    # Then, add the required arguments for this
    parser.add_argument("--env", dest="env", action="store_true",
                        help="if the bot should be configured with environment variables")
    # Finally, return the arguments
    return parser.parse_args()


def main():
    """
    Executes the bot from the command line.
    """
    # Get the parsed command line arguments
    args = parse_args()

    # If the user wants the config from environment variables
    if args.env:
        # If there is no token on the environment variables, exit
        if "DISCORD_TOKEN" not in os.environ:
            pass

        # Otherwise, load the configuration
        config = config_from_env()
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
