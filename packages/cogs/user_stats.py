from datetime import datetime, timedelta
from discord.ext import commands
from discord.member import Member
import logging

from bot import BotClient
from .utils.utils import get_utc_monday, get_discord_member
from .utils.bot_sql import sql_select_user_donation, sql_select_user_active_clash_account, sql_select_active_account

class UserStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('PantherBot.UserStats')

    @commands.command()
    async def donation(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `donation`')
        member: Member
        if arg_string:
            member = await get_discord_member(ctx, arg_string)
        else:
            member = await get_discord_member(ctx, ctx.author.id)

        if not member:
            user = arg_string if arg_string else ctx.author
            await self.bot.embed_print(ctx, f"User `{user}` not found.", color=self.bot.ERROR)
            return

        else:
            async with self.bot.pool.acquire() as conn:
                player = await conn.fetchrow(sql_select_active_account().format(member.id))

            if not player:
                await self.bot.embed_print(ctx, f'User `{member.display_name}` is no longer an active member')
                return

        async with self.bot.pool.acquire() as conn:
            start_date = get_utc_monday()
            sql_query = sql_select_user_donation().format(player['clash_tag'], start_date)
            donation_records = await conn.fetch(sql_query)

        if len(donation_records) < 2:
            await self.bot.embed_print(ctx, title='Donation', description='No results return. Please allow 10 minutes '
                                                                          'minutes to pass to calculate donations')
            return

        else:
            next_monday = start_date + timedelta(days=7)
            time_remaining = next_monday - datetime.utcnow()
            day = time_remaining.days
            time = str(timedelta(seconds=time_remaining.seconds)).split(":")

            donation_value = donation_records[-1]['current_donations'] - donation_records[0]['current_donations']
            msg = f'**Donation Stat:**\n{donation_value} | 300\n**Time Remaining:**\n' \
                  f'{day} days {time[0]} hours {time[1]} minutes'
            await self.bot.embed_print(ctx, title='Donation', description=msg)







def setup(bot):
    bot.add_cog(UserStats(bot))