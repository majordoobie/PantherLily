from datetime import datetime

from discord.ext import commands
import logging

from bot import BotClient

from packages.cogs.utils.bot_sql import *
from packages.cogs.utils.utils import *


def get_inser_clash_account():
    pass


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Leaders')

    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, arg_string=None):
        # Set up arguments 9P9PRYQJ 265368254761926667
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
                'required': True,
                'type': 'int'
            },
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return
        args.coc_tag = args.coc_tag.upper()

        # Get user objects
        player = await get_coc_player(ctx, args.coc_tag, self.bot.coc_client, self.bot.embed_print)
        member = await get_discord_member(ctx, args.discord_id, self.bot.embed_print)
        if not player or not member:
            return

        discord_record = (
            member.id,
            member.name,
            member.display_name,
            member.discriminator,
            member.joined_at,
            member.created_at,
            datetime.utcnow(),
        )
        coc_record = (
            player.tag,
            member.id,
        )


        async with self.bot.pool.acquire() as con:
            discord_member = con.execute(sql_select_discord_user_id(), args.discord_id)
            clash_member = con.execute(sql_select_clash_account_tag(), args.coc_tag)
            if discord_member is None and clash_member is None:
                await con.execute(sql_insert_discord_user(), *discord_record)
                await con.execute(sql_insert_clash_account(), *coc_record)







def setup(bot):
    bot.add_cog(Leaders(bot))


