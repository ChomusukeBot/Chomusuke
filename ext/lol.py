# Import the commands extension
import asyncio
import datetime
import discord
import logging
import os
from cog import Cog
from discord.ext import commands
import typing

# The color of the embeds
COLOR = 0xEDB24C
# Base URL for all API calls
BASE_URL = "https://{}.api.riotgames.com"
# League of Legends Static Data for profile pictures
PROFILE_IMAGE_URL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png"
# League of Legends Static Data for champions
CHAMPIONS_URL = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json"
# API Operation used to access summoner data
SUMMONER_API = "/lol/summoner/v4/summoners/by-name/{}?api_key={}"
# API Operation used to access summoner ranked data
RANKED_API = "/lol/league/v4/entries/by-summoner/{}?api_key={}"
# API Operation used to access summoner match history
MATCHES_API = "/lol/match/v4/matchlists/by-account/{}?api_key={}"
# API Operation used to access a specific match
MATCH_API = "/lol/match/v4/matches/{}?api_key={}"
# A .json file storing the current and all previous versions of league of legends
LEAGUE_VERSION = "https://ddragon.leagueoflegends.com/api/versions.json"
# A dictionary of RIOT's regional endpoints and their corresponding server shortcuts
REGIONS = {
    "br": "br1",
    "eune": "eun1",
    "euw": "euw1",
    "jp": "jp1",
    "kr": "kr",
    "lan": "la1",
    "las": "la2",
    "na": "na1",
    "oce": "oc1",
    "tr": "tr1",
    "ru": "ru",
    "pbe": "pbe1"
}
# A dictionary of riots matchmaking queues (deprecates ones included)
MATCHMAKING_QUEUES = {
    0: "Custom game",
    2: "Summoner's Rift - 5v5 Blind Pick game",
    4: "Summoner's Rift - 5v5 Ranked Solo game",
    6: "Summoner's Rift - 5v5 Ranked Premade game",
    7: "Summoner's Rift - Co-op vs AI game",
    8: "Twisted Treeline - 3v3 Normal game",
    9: "Twisted Treeline - 3v3 Ranked Flex game",
    14: "Summoner's Rift - 5v5 Draft Pick game",
    16: "Crystal Scar - 5v5 Dominion Blind Pick game",
    17: "Crystal Scar - 5v5 Dominion Draft Pick game",
    25: "Crystal Scar - Dominion Co-op vs AI game",
    31: "Summoner's Rift - Co-op vs AI Intro Bot game",
    32: "Summoner's Rift - Co-op vs AI Beginner Bot game",
    33: "Summoner's Rift - Co-op vs AI Intermediate Bot game",
    41: "Twisted Treeline - 3v3 Ranked Team game",
    42: "Summoner's Rift - 5v5 Ranked Team game",
    52: "Twisted Treeline - Co-op vs AI game",
    61: "Summoner's Rift - 5v5 Team Builder game",
    65: "Howling Abyss - 5v5 ARAM game",
    67: "Howling Abyss - ARAM Co-op vs AI game",
    70: "Summoner's Rift - One for All game",
    72: "Howling Abyss - 1v1 Snowdown Showdown game",
    73: "Howling Abyss - 2v2 Snowdown Showdown game",
    75: "Summoner's Rift - 6v6 Hexakill game",
    76: "Summoner's Rift - Ultra Rapid Fire game",
    78: "Howling Abyss - One For All: Mirror Mode game",
    83: "Summoner's Rift - Co-op vs AI Ultra Rapid Fire game",
    91: "Summoner's Rift - Doom Bots Rank 1 game",
    92: "Summoner's Rift - Doom Bots Rank 2 game",
    93: "Summoner's Rift - Doom Bots Rank 5 game",
    96: "Crystal Scar - Ascension game",
    98: "Twisted Treeline - 6v6 Hexakill game",
    100: "Butcher's Bridge - 5v5 ARAM game",
    300: "Howling Abyss - Legend of the Poro King game",
    310: "Summoner's Rift - Nemesis game",
    313: "Summoner's Rift - Black Market Brawlers game",
    315: "Summoner's Rift - Nexus Siege game",
    317: "Crystal Scar - Definitely Not Dominion game",
    318: "Summoner's Rift - ARURF game",
    325: "Summoner's Rift - All Random game",
    400: "Summoner's Rift - 5v5 Draft Pick game",
    410: "Summoner's Rift - 5v5 Ranked Dynamic game",
    420: "Summoner's Rift - 5v5 Ranked Solo game",
    430: "Summoner's Rift - 5v5 Blind Pick game",
    440: "Summoner's Rift - 5v5 Ranked Flex game",
    450: "Howling Abyss - 5v5 ARAM game",
    460: "Twisted Treeline - 3v3 Blind Pick game",
    470: "Twisted Treeline - 3v3 Ranked Flex game",
    600: "Summoner's Rift - Blood Hunt Assassin game",
    610: "Cosmic Ruins - Dark Star: Singularity game",
    700: "Summoner's Rift - Clash game",
    800: "Twisted Treeline - Co-op vs. AI Intermediate Bot game",
    810: "Twisted Treeline - Co-op vs. AI Intro Bot game",
    820: "Twisted Treeline - Co-op vs. AI Beginner Bot game",
    830: "Summoner's Rift - Co-op vs. AI Intro Bot game",
    840: "Summoner's Rift - Co-op vs. AI Beginner Bot game",
    850: "Summoner's Rift - Co-op vs. AI Intermediate Bot game",
    900: "Summoner's Rift - ARURF game",
    910: "Crystal Scar - Ascension game",
    920: "Howling Abyss - Legend of the Poro King game",
    940: "Summoner's Rift - Nexus Siege game",
    950: "Summoner's Rift - Doom Bots Voting game",
    960: "Summoner's Rift - Doom Bots Standard game",
    980: "Valoran City Park - Star Guardian Invasion: Normal game",
    990: "Valoran City Park - Star Guardian Invasion: Onslaught game",
    1000: "Overcharge PROJECT: Hunters game",
    1010: "Summoner's Rift - Snow ARURF game",
    1020: "Summoner's Rift - One for All game",
    1030: "Crash Site Odyssey Extraction: Intro game",
    1040: "Crash Site Odyssey Extraction: Cadet game",
    1050: "Crash Site Odyssey Extraction: Crewmember game",
    1060: "Crash Site Odyssey Extraction: Captain game",
    1070: "Crash Site Odyssey Extraction: Onslaught game",
    1200: "Nexus Blitz - Nexus Blitz game"
}
# The information logger
LOGGER: logging.Logger = logging.getLogger("chomusuke")


class LeagueOfLegends(Cog):
    """
    A cog for accessing the League of Legends API.
    """
    def __init__(self, bot):
        # Save our bot for later use
        self.bot = bot
        # Start the task to make sure that we have the values
        self.bot.loop.create_task(self.update_values())
        # Save the league api key and the current league version
        self.league_key = os.environ["LEAGUE_TOKEN"]

    async def update_values(self):
        """
        Task that updates the version and list of champions every hour.
        """
        # While the bot is not closed
        while not self.bot.is_closed():
            # Request the list of versions
            async with self.bot.session.get(LEAGUE_VERSION) as resp:
                # Parse the response as JSON and save the version
                self.version = (await resp.json(content_type=None))[0]

            # Create an empty dict with the character data
            new_champs = {}

            # Request the list of champions on the current version
            async with self.bot.session.get(CHAMPIONS_URL.format(self.version)) as resp:
                # Iterate over the characters on the response (but parse it first)
                for key, value in (await resp.json())["data"].items():
                    # Save the champion name
                    new_champs[value["key"]] = value["name"]

            # Replace the existing list of champions
            self.champions = new_champs

            # Finally log what we have done
            LOGGER.info("League of Legends Version and Champion list has been update")

            # And wait an hour (60 seconds * 60 minutes = 1 hour)
            await asyncio.sleep(60 * 60)

    @commands.group()
    async def lol(self, ctx):
        """
        Commands to interact with League of Legends profiles and matches.
        """

    @lol.command(aliases=["p"])
    async def profile(self, ctx, region, *, summoner):
        """
        Displays a summoner's profile.
        """
        # If the specific region is not on our dictionary, notify and return
        if not region.lower() in REGIONS:
            await ctx.send("That region was not found. Please use one of the following:\n" + ", ".join(REGIONS.keys()))
            return

        # Request the summoner data
        data = await self.get_summoner_data(region, summoner)
        # If there is no data available, notify the user and return
        if not data:
            await ctx.send("Summoner not found. Please double check that the you are using the summoner name and not the username.")
            return

        # Patch the region
        region = REGIONS[region.lower()]

        # Get the ranked data
        async with self.bot.session.get(BASE_URL.format(region) + RANKED_API.format(data["id"], self.league_key)) as resp:
            rank = await resp.json()

        # Create an embed to display summoner data
        embed = discord.Embed(title="Profile of " + data["name"], color=COLOR)
        # Set the picture as the user profile image
        embed.set_thumbnail(url=PROFILE_IMAGE_URL.format(self.version, data.get("profileIconId")))
        # Add our fields (if the summoner is unranked, show the unranked status)
        embed.add_field(name="Summoner Level", value="Level " + str(data["summonerLevel"]))
        embed.add_field(name="Rank", value=rank[0]["tier"] + " " + rank[0]["rank"] if rank else "Unranked")
        embed.add_field(name="Wins/Loses", value=str(rank[0]["wins"]) + "/" + str(rank[0]["losses"]) if rank else "Unranked")
        embed.add_field(name="League Points", value=rank[0]["leaguePoints"] if rank else "Unranked")
        # Finally, send the embed
        await ctx.send(embed=embed)

    @lol.command(aliases=["m"])
    async def match(self, ctx, region, prevMatch: typing.Optional[int] = 0, *, summoner):
        """
        Shows the match history of the specified summoner up to a maximum of 5.
        """
        # If the specific region is not on our dictionary, notify and return
        if not region.lower() in REGIONS:
            await ctx.send("That region was not found. Please use one of the following:\n" + ", ".join(REGIONS.keys()))
            return

        # Request the summoner data
        data = await self.get_summoner_data(region, summoner)
        # If there is no data available, notify the user and return
        if not data:
            await ctx.send("Summoner not found. Please double check that the you are using the summoner name and not the username.")
            return

        # Patch the current region
        region = REGIONS[region.lower()]

        # Get the match history
        params = {"endIndex": prevMatch+1, "beginIndex": prevMatch}
        async with self.bot.session.get(BASE_URL.format(region) + MATCHES_API.format(data["accountId"], self.league_key), params=params) as resp:
            history = await resp.json()
        # Iterate over the matches on the response
        for match_meta in history["matches"]:
            # Request the match information
            async with self.bot.session.get(BASE_URL.format(region) + MATCH_API.format(match_meta["gameId"], self.league_key)) as resp:
                match_data = await resp.json()

            # Grab the important match data
            mode = MATCHMAKING_QUEUES[match_data["queueId"]]
            duration = match_data["gameDuration"]
            timestamp = datetime.datetime.fromtimestamp(match_data["gameCreation"] / 1000)
            duration = datetime.datetime.min + datetime.timedelta(seconds=duration)

            # Split the two teams to process their data
            blue = (match_data["participants"][:5], match_data["participantIdentities"][:5])
            red = (match_data["participants"][5:], match_data["participantIdentities"][5:])
            # Generate the strings
            blue_data = await self.format_match_data(*blue)
            red_data = await self.format_match_data(*red)

            # Calculate the days ago that the game was played
            elapsed = datetime.datetime.now() - timestamp
            # If the elapsed days equals zero, the match was played today
            if elapsed.days == 0:
                stamp = "today"
            # Otherwise
            else:
                stamp = f"{elapsed.days} day(s) ago"

            # Create the embed to add the data
            embed = discord.Embed(title=f"{mode} ({stamp})", description="Game duration: " + duration.strftime("%H:%M:%S"), color=COLOR)
            # Add the fields with the information
            embed.add_field(name="🔵 BLUE TEAM 🔵", value=blue_data, inline=False)
            embed.add_field(name="🔴 RED TEAM 🔴", value=red_data, inline=False)
            # Add the information about the team that won
            embed.set_footer(text=("Blue" if match_data["teams"][0]["win"] == "Win" else "Red") + " team won!")
            # Finally, return the embed
            await ctx.send(embed=embed)

    async def format_match_data(self, players, identities):
        # Create a place to store our data
        base = ""
        # For every player and identity
        for player, identity in zip(players, identities):
            # Add the formatted information
            base += "{0} - {1} ({2}/{3}/{4})\n".format(identity["player"]["summonerName"],
                                                       self.champions.get(str(player["championId"]), "Unknown"),
                                                       player["stats"]["kills"], player["stats"]["deaths"], player["stats"]["assists"])
        # Finally, return the generated string
        return base

    async def get_summoner_data(self, region, summoner):
        # Run the response as usual
        async with self.bot.session.get(BASE_URL.format(REGIONS[region.lower()]) + SUMMONER_API.format(summoner, self.league_key)) as resp:
            if resp.status == 200:
                return await resp.json()
            return


def setup(bot):
    """
    Our function called to add the cog to our bot.
    """
    # Initial check to see if a League of Legends API Token exists in our enviroment
    if "LEAGUE_TOKEN" in os.environ:
        bot.add_cog(LeagueOfLegends(bot))
    else:
        LOGGER.error("No League of Legends token has been specified, the Cog has not been loaded")
