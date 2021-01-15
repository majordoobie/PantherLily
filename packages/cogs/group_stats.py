import asyncio
from datetime import timedelta

from discord.ext import commands
import logging

from bot import BotClient
from .utils.bot_sql import sql_select_all_active_users, sql_select_clash_members_not_registered, sql_select_classic_view
from .utils.utils import parse_args, get_utc_monday


class GroupStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('PantherBot.GroupStats')

    @commands.command(
        aliases=['ro'],
        brief='',
        description='Display clan roster',
        usage='',
        help='Display users currently registered and all users in the clan. Additionally, display the current location '
             'of players. This is useful for CWL when the clanmates are scattered.'
    )
    async def roster(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `roster`')

        # Create legend to display
        clan = self.bot.settings.emojis["reddit_zulu"]
        db = self.bot.settings.emojis["database"]
        discord = self.bot.settings.emojis["zulu_server"]
        waze = self.bot.settings.emojis["waze"]
        true = self.bot.settings.emojis["true"]
        false = self.bot.settings.emojis["false"]

        legend = f'{clan} Member is in Reddit Zulu in-game.\n'
        legend += f'{db} Member is registered with Pantherlily.\n'
        legend += f'{discord} Member is Reddit Zulu Discord server.\n'
        legend += f'{waze} Get realtime location of members.\n'

        await self.bot.embed_print(ctx, legend)

        # Get users and sort them by name
        async with self.bot.pool.acquire() as con:
            members_db = await con.fetch(sql_select_all_active_users())
            unregistered_users = await con.fetch(sql_select_clash_members_not_registered())
        members_db.sort(key=lambda x: x['clash_name'].lower())

        roster = {}
        clan_locations = {}
        strength_count = 0
        strength = {}
        for member in members_db:
            strength_count += 1
            town_hall = strength.get(member['town_hall'])
            if town_hall:
                strength[member['town_hall']] += 1
            else:
                strength[member['town_hall']] = 1

            roster[member['clash_name']] = {
                'in_mother_clan': _in_clan(member['current_clan_tag']),
                'in_discord': member['in_zulu_server'],
                'in_database': True
            }
            clan_location = clan_locations.get(member['current_clan_name'])
            if clan_location:
                clan_locations[member['current_clan_name']].append({
                    'name': member['discord_name'],
                    'town_hall': member['town_hall']
                })
            else:
                clan_locations[member['current_clan_name']] = [{
                    'name': member['discord_name'],
                    'town_hall': member['town_hall']
                }]

        for player in unregistered_users:
            roster[player['player_name']] = {
                'in_mother_clan': True,
                'in_discord': False,
                'in_database': False
            }


        # Display the roster panel
        panel = f'{clan}{db}{discord}\u0080\n'
        count = 0
        for player, stats in roster.items():
            panel += true if stats['in_mother_clan'] else false
            panel += true if stats['in_database'] else false
            panel += true if stats['in_discord'] else false
            count += 1
            panel += f"  **{count:>2}**  {player}\n"

        await self.bot.embed_print(ctx, panel, footnote=False)

        strength_panel = f'__**Registered Members**__\n`⠀{"Total members":\u00A0<13}⠀` `⠀{strength_count:>2}⠀`\n'
        levels = [level for level in strength.keys()]
        levels.sort(reverse=True)
        for level in levels:
            town_hall = f'Total TH{level}'
            strength_panel += f"`⠀{town_hall:\u00A0<13}⠀` `⠀{strength[level]:>2}⠀`\n"

        strength_embed = await self.bot.embed_print(ctx, strength_panel, _return=True)
        strength_panel = await ctx.send(embed=strength_embed)
        await strength_panel.add_reaction(waze)

        # Display the location panels
        def check(reaction, user):
            return not user.bot and str(reaction.emoji) == waze

        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            location_panels = ''
            for clan, players in clan_locations.items():
                panel = f'__**{clan}**__\n'
                for player in players:
                    panel += f'`⠀{player["town_hall"]:<2}⠀` `⠀{player["name"]:<23.23}⠀`\n'
                location_panels += panel
            await self.bot.embed_print(ctx, location_panels)

        except asyncio.TimeoutError:
            pass

    @commands.command(
        aliases=['t'],
        brief='-t for trophies',
        description='Display clan rankings for trophies or donations',
        usage='[-w int][-d(Default)][-t]',
        help='Display donation or trophy rankings of the clan. By default, top 20 donations will be shown and only '
             'the current week is shown. If you would like to display trophy rankings instead, use the -t switch.\n\n'
             'Additionally, you are able to show previous weeks with the -w switch followed by the number of weeks you '
             'you would like to display.\n\n'
             '-w || --weeks [integer]\n-d || --donations\n-t || --trophies'
    )
    async def top(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `top`')
        arg_dict = {
            'weeks': {
                'flags': ['-w', '--weeks'],
                'type': 'int',
                'default': 1
            },
            'donations': {
                'flags': ['-d', '--donations'],
                'switch_action': True,
                'switch': True,
                'default': True
            },
            'trophies': {
                'flags': ['-t', '--trophies'],
                'switch_action': True,
                'switch': True,
                'default': False
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        donation = True if not args['trophies'] else False

        # Get the amount of weeks to pull back
        dates = []
        for i in range(0, args['weeks']):
            dates.append(get_utc_monday() - timedelta(days=(i * 7)))

        # Get report blocks based on dates
        data_blocks = []
        async with self.bot.pool.acquire() as con:
            for date in dates:
                players = await con.fetch(sql_select_classic_view().format(date))
                data_blocks.append(players)

        if not donation:
            for date, players in enumerate(data_blocks):
                players.sort(key=lambda x: x['current_trophy'], reverse=True)
                frame = f'__**Trophy Ranking**__\n'
                frame += f"`⠀{'rk':<2}⠀{'th':<2}⠀{'trop':<4}⠀{'diff':>5}⠀`\n"
                for count, player in enumerate(players):
                    count += 1
                    name = player['clash_name'][:14]
                    frame += f"`⠀{count:<2}⠀{player['town_hall']:<2}⠀{player['current_trophy']:<4}⠀" \
                             f"{player['trophy_diff']:<5}⠀{name:<14}`\n"
                frame += f'`Week of: {dates[date].strftime("%Y-%m-%d")}`'
                await ctx.send(frame)
        else:
            for date, players in enumerate(data_blocks):
                players.sort(key=lambda x: x['donation_gains'], reverse=True)
                frame = f'__**Donation Ranking**__\n'
                frame += f"`⠀{'rk':<2}⠀{'th':<2}⠀{'Donation':<8}⠀`\n"
                for count, player in enumerate(players[:20]):
                    count += 1
                    frame += f"`⠀{str(count):<2}⠀{player['town_hall']:<2}⠀{player['donation_gains']:<4}⠀" \
                             f"{player['clash_name']:<14.14}`\n"

                frame += f'`Week of: {dates[date].strftime("%Y-%m-%d")}`'
                await ctx.send(frame)

def _in_clan(clan_tag: str) -> bool:
    if clan_tag == '#2Y28CGP8':
        return True
    return False

def setup(bot):
    bot.add_cog(GroupStats(bot))