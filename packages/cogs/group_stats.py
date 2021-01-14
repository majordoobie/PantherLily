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

        legend = f'{clan} Member is in Reddit Zulu in-game.\n'
        legend += f'{db} Member is registered with Pantherlily.\n'
        legend += f'{discord} Member is Reddit Zulu Discord server.\n'
        legend += f'{waze} Get realtime location of members.\n'

        await self.bot.embed_print(ctx, legend)

        # Populate the roster dictionary
        roster = {"total": 0}
        sister_clans = {
            "#P0Q8VRC8": [],
            "#2Y28CGP8": [],
            "#8YG0CQRY": [],
            "Unknown": []
        }


        # Get users and sort them by name
        async with self.bot.pool.acquire() as con:
            members_db = await con.fetch(sql_select_all_active_users())
            unregistered_users = await con.fetch(sql_select_clash_members_not_registered())
        members_db.sort(key=lambda x: x['discord_nickname'].lower())

        roster = {}
        clan_locations = {}
        for member in members_db:
            roster[member['discord_nickname']] = {
                'in_mother_clan': _in_clan(member['current_clan_tag']),
                'in_discord': member['in_zulu_server'],
                'in_database': True
            }
            clan_location = clan_locations.get(member['current_clan_tag'])
            if clan_location:
                clan_locations[member['current_clan_name']].append({
                    member['discord_name'],
                    member['town_hall']
                })
            else:
                clan_locations[member['current_clan_name']] = [{
                    member['discord_name'],
                    member['town_hall']
                }]

        for player in unregistered_users:
            roster[player['player_name']] = {
                'in_mother_clan': True,
                'in_discord': False,
                'in_database': False
            }

def _in_clan(clan_tag: str) -> bool:
    if clan_tag == '#2Y28CGP8':
        return True
    return False








        #TODO: Stop for now we need to populate clash_account for this to work









def setup(bot):
    bot.add_cog(GroupStats(bot))