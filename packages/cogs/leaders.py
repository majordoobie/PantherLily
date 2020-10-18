from discord.ext import commands
import logging

from bot import BotClient
from packages.cogs.utils.discord_arg_parser import arg_parser
from packages.cogs.utils.discord_aarg_parser2 import DiscoArgParse, DiscoArgParseException
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
                'switch': False,
                'required': True
            },
            'discord_id': {
                'default': None,
                'flags': ['--discord', '-d'],
                'switch': False,
                'required': True
            }
        }
        #parsed_args = await arg_parser(switches, args)


        try:
            parsed_args = DiscoArgParse(switches, args)
            print(parsed_args)
            print(parsed_args.arg_dict)
        except DiscoArgParseException as error:
            await self.bot.embed_print(ctx, error.msg,  color='error')

        return




def setup(bot):
    bot.add_cog(Leaders(bot))


