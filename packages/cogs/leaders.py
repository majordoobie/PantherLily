from discord.ext import commands
import logging

from bot import BotClient
from coc.utils import is_valid_tag
from packages.cogs.utils.utils import *


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Leaders')

    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, args=None):
        # Set up arguments
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
            },
        }
        parsed_args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)

        # Get player coc_client
        if not is_valid_tag(parsed_args['coc_tag']):
            await self.bot.embed_print(ctx, title='Invalid Tag', description='Please provide a valid player tag',
                                       color='error')
            return
        1

        return




def setup(bot):
    bot.add_cog(Leaders(bot))


