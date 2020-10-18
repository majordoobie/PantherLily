from discord.ext import commands
import logging

from bot import BotClient
from packages.cogs.utils.discord_arg_parser import DiscordArgParse, DiscoArgParseException
from packages.cogs.utils.utils import *


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Leaders')

    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, args=None):
        switches = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
            },
            'test_flag' : {
                'flags': ['--test'],
                'switch': True
            }
        }
        parsed_args = await parse_args(ctx, self.bot.settings, switches, args)
        print(parsed_args)

        return




def setup(bot):
    bot.add_cog(Leaders(bot))


