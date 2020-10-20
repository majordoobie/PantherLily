from datetime import datetime

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
        discord_record_sql = '''INSERT INTO discord_user(
                        discord_id, discord_name, discord_nickname, discord_discriminator, 
                        guild_join_date, global_join_date, db_join_date, in_zulu_base_planning, 
                        in_zulu_server, is_active) 
                        VALUES (
                        $1, $2, $3, $4, $5, $6, $7, false, true, true)'''
        coc_record_sql = '''INSERT INTO clash_account(
                        clash_tag, discord_id, is_primary_account) VALUES (
                        $1, $2, true)'''
        async with self.bot.pool.acquire() as con:
            await con.execute(discord_record_sql, *discord_record)
            await con.execute(coc_record_sql, *coc_record)







def setup(bot):
    bot.add_cog(Leaders(bot))


