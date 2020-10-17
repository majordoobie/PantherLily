from discord.ext import commands
import logging

from .utils import *
from bot import BotClient
from .discord_arg_parser import arg_parser

class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Leaders')

    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, args=None):
        switches = {
            'coc_tag': {
                'default': None,
                'flags': ['-c', '--clash'],
                'switch': False,
                'required': True
            },
            'discord_id': {
                'default': None,
                'flags': ['-d', '--discord'],
                'switch': False,
                'required': True
            }
        }
        parsed_args = await arg_parser(switches, args)

        print(parsed_args)


def setup(bot):
    bot.add_cog(Leaders(bot))


