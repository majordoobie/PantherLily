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
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return

        # Get user objects
        player = await get_coc_player(ctx, args.coc_tag, self.bot.coc_client, self.bot.embed_print)
        member = await get_discord_member(ctx, args.discord_id, self.bot.embed_print)
        if not player or not member:
            return

        print(member)








def setup(bot):
    bot.add_cog(Leaders(bot))


