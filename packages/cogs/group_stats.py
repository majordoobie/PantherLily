import asyncio
from discord.ext import commands
import logging

from bot import BotClient
from .utils.bot_sql import sql_select_all_active_users, sql_select_clash_members_not_registered

class GroupStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('PantherBot.GroupStats')

    @commands.command()
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
        members_db.sort(key=lambda x: x['discord_nickname'].lower())

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

            roster[member['discord_nickname']] = {
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
            for clan, players in clan_locations.items():
                panel = f'__**{clan}**__\n'
                for player in players:
                    panel += f'`⠀{player["town_hall"]:<2}⠀` `⠀{player["name"]:<23}⠀`\n'
                await self.bot.embed_print(ctx, panel)
        except asyncio.TimeoutError:
            pass





def _in_clan(clan_tag: str) -> bool:
    if clan_tag == '#2Y28CGP8':
        return True
    return False
        #TODO: Stop for now we need to populate clash_account for this to work









def setup(bot):
    bot.add_cog(GroupStats(bot))