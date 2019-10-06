import argparse

from .bot import Chomusuke


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


if __name__ == "__main__":
    main()
