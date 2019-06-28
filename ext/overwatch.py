from discord.ext import commands
from cog import Cog
import json
import aiohttp
import async_timeout

class OWApi:
    def __init__(self):
        self.base_url = "https://overwatchy.com"

    async def __get_json(self, session, url):
        """
            A helper function for fetching JSON data from the OWApi
            :param session: aiohttp.ClientSession object
            :param url: str -- URL to be requested
            :return: response body and status code.
        """
        with async_timeout.timeout(15):
            async with session.get(url) as response:
                resp = await response.json()
                resp_code = response.status
            return resp, resp_code

    async def status(self):
        """
            Requests the status of the OWApi.
            :return: int -- The status code of the request. 
        """
        url = self.base_url+ '/'
        async with aiohttp.ClientSession() as session:
            resp, resp_code = await self.__get_json(session, url)
        return resp_code

    async def get_player_profile(self, platform, region, player, comp=False):
        """
            Requests the player's profile from OWApi.
            :param platform: str -- The platform that the player is on
            :param region: str -- The overwatch region that the player is from.
            :param player: str -- The player name to query.
            :param comp: optional: bool -- Set to true if you want to actually return the response.
            :return: None -- If an error is encountered with the API.
            :return: False -- If the player profile is not found.
            :return: True -- If the player profile is successfully retrieved.
        """
        url = self.base_url + f'/profile/{platform}/{region}/{player}'
        async with aiohttp.ClientSession() as session:
            resp, resp_code = await self.__get_json(session, url)
        # In case something goes wrong when querying the OWApi.
        if resp_code is not 200:
            return None
        if comp:
            return resp
        # If there is an error message in the response, 
        # then the profile was not found, or is private.
        if 'message' in resp:
            return False
        else:
            return True

    async def get_player_stats(self, platform, region, player):
        """
            Requests the players stats from OWApi.
            :param platform: str -- The platform that the player is on
            :param region: str -- The overwatch region that the player is from.
            :param player: str -- The player name to query.
            :return: None -- If an error is encountered with the API.
            :return: resp -- The response from the OWApi.
        """
        url = self.base_url + f'/stats/{platform}/{region}/{player}'
        async with aiohttp.ClientSession() as session:
            resp, resp_code = await self.__get_json(session, url)
        if resp_code is not 200:
            return None
        else:
            return resp

class Overwatch(Cog):
    """
        A cog for getting stats about an Overwatch player.
    """
    def __init__(self, bot):
        self.bot = bot
        self.api = OWApi()

    async def __handle_avgs(self, avg):
        """
            Takes a bunch of averages from OWApi, and handles them sanely.
            :param avg: list -- The list of avgs from OWApi.
            :return: dict -- An easily workable dict of the averages.
        """
        avg_dict = {
            'Damage Done': None,
            'Eliminations': None,
            'Deaths': None,
        }
        for item in avg:
            if item['title'] == 'All Damage Done - Avg per 10 Min':
                avg_dict['Damage Done'] = item['value']
            elif item['title'] == 'Deaths - Avg per 10 Min':
                avg_dict['Deaths'] = item['value']
            elif item['title'] == 'Eliminations - Avg per 10 Min':
                avg_dict['Eliminations'] = item['value']
        return avg_dict

    async def __calculate_kdr(self, combat):
        """
            Handles the the combat object from the OWApi in a sane way to calculate KDR.
            :param combat: list -- The combat list from the OWApi.
            :returns: dict -- Relevant KDR info.
        """
        kdr_dict = {
            'Eliminations': 0,
            'Deaths': 0,
            'kdr': 0,
        }
        for item in combat:
            if item['title'] == 'Deaths':
                kdr_dict['Deaths'] = int(item['value'])
            elif item['title'] == 'Eliminations':
                kdr_dict['Eliminations'] = int(item['value'])
        kdr_dict['kdr'] = round(kdr_dict['Eliminations'] / kdr_dict['Deaths'], 2)
        return kdr_dict

    async def __build_stats_embed(self, platform, region, player):
        """
            Function calls the get_player_stats function from the OWApi, and uses the returned response to build 
            the embed that will be sent.
        """
        stats = await self.api.get_player_stats(platform, region, player)
        profile = await self.api.get_player_profile(platform, region, player, True)
        comp = False # Used to determine if we need to pull competitive stats or not.
        if '-' in player:
            player = player.replace('-', '#')
        # Start building the embed.
        embed = discord.Embed(title=f'{player} Overwatch Statistics')
        embed.set_thumbnail(url=stats['portrait'])
        embed.add_field(name='Level', value=stats['level'])
        if profile['competitive']['rank']:
            embed.add_field(name='Competitive Rank', value=profile['competitive']['rank'])
            comp = True
        embed.add_field(name='Quick Play Time', value=stats['stats']['game']['quickplay'][-1]['value'])
        if comp:
            embed.add_field(name='Competitive Play Time', value=stats['stats']['game']['competitive'][-1]['value'])
        top_heroes = '\n• '.join([f'*{x["hero"]}*:  {x["played"]}' for x in stats['stats']['top_heroes']['quickplay']['played'][:3]])
        embed.add_field(name='Quick Play Heroes', value=f"• {top_heroes}")
        if comp:
            top_heroes = '\n• '.join([f'*{x["hero"]}*:  {x["played"]}' for x in stats['stats']['top_heroes']['competitive']['played'][:3]])
            embed.add_field(name='Competitive Heroes', value=f'• {top_heroes}')
        avgs = await self.__handle_avgs(stats['stats']['average']['quickplay'])
        avgs = '\n• '.join([f'**{key}**: {value}' for key, value in avgs.items()])
        embed.add_field(name='Quick Play Averages (10 mins)', value=f"• {avgs}")
        if comp:
            avgs = await self.__handle_avgs(stats['stats']['average']['competitive'])
            avgs = '\n• '.join([f'**{key}**: {value}' for key, value in avgs.items()])
            embed.add_field(name='Competitive Averages (10 mins)', value=f"• {avgs}")
        kdr = await self.__calculate_kdr(stats['stats']['combat']['quickplay'])
        embed.add_field(name='Quick Play KDR', value=f'{kdr["kdr"]} ({kdr["Eliminations"]}/{kdr["Deaths"]})')
        if comp:
            kdr = await self.__calculate_kdr(stats['stats']['combat']['competitive'])
            embed.add_field(name='Competitive KDR', value=f'{kdr["kdr"]} ({kdr["Eliminations"]}/{kdr["Deaths"]})')
        # return the embed!
        return embed

    @commands.command(aliases=['ow_stats', 'ow'])
    async def get_overwatch_stats(self, ctx, player=None, platform='pc', region='global'):
        """
            Command to get the stats for a given player on a given platform.
        """
        if player is None or platform is None:
            return await ctx.send("You must provide both a player and a platform to retrieve player stats.")
        # Format player name.
        if platform == 'pc':
            if '#' not in player:
                return await ctx.send('PC player names must include a discriminator. Example: `Lemon#13526`')
            else:
                player = player.replace('#', '-') 
        # Check that the user has provided a valid overwatch platform.
        platforms = ('pc', 'psn', 'xbl')
        if platform not in platforms:
            return await ctx.send(f"`{platform}` is not a valid platform. "
                                  f"\nValid platform choices are: `pc`, `psn`, or `xbl`.")
        # Check that the region is valid
        regions = ('us','eu','kr','cn','global')
        if region not in regions:
            return ctx.send(f"`{region} is not a valid region. \nValid choices for region are `{'`, `'.join(regions)}")
        # Check if the player provided was found.
        found = await self.api.get_player_profile(platform, region, player)
        if found is None:
            return await ctx.send("Something went wrong when attempting to contact the Overwatch API.")
        elif found is False:
            return await ctx.send('The profile for the player specified either does not exist or is set private.')
        # Actually get and parse stats!
        embed = await self.__build_stats_embed(platform, region, player)
        if embed is None:
            return await ctx.send("Something went wrong when attempting to contact the Overwatch API.")
        return await ctx.send(embed=embed)

    @commands.command(aliases=['ow_status', 'ows'])
    async def overwatch_status(self, ctx):
        status = await self.api.status()
        if status is 200:
            return await ctx.send("Overwatch API functioning normally! 👍")
        else:
            return await ctx.send(f"Something is wrong with the overwatch API! Got status `{status}`")


def setup(bot):
    bot.add_cog(Overwatch(bot))