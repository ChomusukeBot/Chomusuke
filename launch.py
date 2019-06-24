# Import our little set of tools
import asyncio
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

    # Create a dictionary of keyword arguments
    kwargs = {
        "command_prefix": os.environ["DISCORD_PREFIX"]
    }

    # If there is a MongoDB database added
    if "MONGODB_URL" in os.environ:
        # Add the database to our keyword arguments
        kwargs["database"] = os.environ["MONGODB_URL"]

    # Create our bot instance
    bot = Chomusuke(**kwargs)

    # Iterate over the python files from the ext folder
    for file in [x for x in os.listdir("ext") if x.endswith(".py")]:
        # And add the extension without the extension
        bot.load_extension("ext." + os.path.splitext(file)[0])

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
