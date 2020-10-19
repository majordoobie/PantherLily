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
    async def add_user(self, ctx, *, arg_string=None):
        # Set up arguments
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
                'required': True
            },
        }

        parsed_args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not parsed_args:
            return



        print(ctx.guild.members)
        for m in ctx.guild.members:
            print(m)

        return

        player = await get_coc_player(ctx, parsed_args.coc_tag, self.bot.coc_client, self.bot.embed_print)
        k_member = await get_discord_member(ctx, parsed_args.discord_id, self.bot.embed_print)


        if k_member:
            print(k_member)



        return




def setup(bot):
    bot.add_cog(Leaders(bot))


