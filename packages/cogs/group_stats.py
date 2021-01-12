from discord.ext import commands
import logging

from bot import BotClient
from .utils.bot_sql import sql_select_all_active_users

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
        members_db.sort(key=lambda x: x['discord_nickname'].lower())










        #TODO: Stop for now we need to populate clash_account for this to work









def setup(bot):
    bot.add_cog(GroupStats(bot))