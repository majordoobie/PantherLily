from datetime import datetime, timedelta

import asyncio
from coc import utils
from discord.ext import commands
from discord.member import Member
import logging

from bot import BotClient
from .clash_stats.clash_stats_panel import ClashStats
from .utils.utils import get_utc_monday, get_discord_member, parse_args
from .utils.bot_sql import sql_select_user_donation, sql_select_active_account, sql_select_discord_user_id, \
    sql_select_clash_account_discord_id
from .leaders import account_panel

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
                await self.bot.embed_print(ctx, f'User `{member.display_name}` is no longer an active member',
                                           color=self.bot.WARNING)
                return

        week_start = get_utc_monday()
        async with self.bot.pool.acquire() as conn:
            donation_sql = sql_select_user_donation().format(week_start, player['clash_tag'])
            player_record = await conn.fetchrow(donation_sql)

        if not player_record:
            await self.bot.embed_print(ctx, title='Donation', description='No results return. Please allow 10 minutes '
                                                                          'minutes to pass to calculate donations')
            return

        week_end = week_start + timedelta(days=7)
        time_remaining = week_end - datetime.utcnow()
        day = time_remaining.days
        time = str(timedelta(seconds=time_remaining.seconds)).split(":")
        msg = f'**Donation Stat:**\n{player_record["donation_gains"]} | 300\n**Time Remaining:**\n' \
              f'{day} days {time[0]} hours {time[1]} minutes'
        await self.bot.embed_print(ctx, title=f'__**{player_record["clash_name"]}**__', description=msg)


    @commands.command()
    async def stats(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `stats` with `{arg_string}`')
        #TODO add a way to just give a tag to get that information
        arg_dict = {
            'clash_tag': {
                'flags': ['-c', '--clash_tag'],
            },
            'display_level': {
                'flags': ['-l', '--level'],
                'type': 'int',
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return
        member: Member

        # If --clash-tag was supplied the search by clash tag directly instead of by user
        if args['clash_tag']:
            tag = args['clash_tag']
            if utils.is_valid_tag(tag):
                player = await self.bot.coc_client.get_player(tag)
                if player:
                    panel_a, panel_b = ClashStats(player).display_troops()
                    await self._display_panels(ctx, player, panel_a, panel_b)
                    return
                else:
                    await self.bot.embed_print(ctx, description=f'User with the tag of {tag} was not found',
                                               color=self.bot.WARNING)
                    return

        # If clash tag was not used then attempt to get the user by discord accounts
        elif args['positional']:
            member = await get_discord_member(ctx, args['positional'])
        else:
            member = await get_discord_member(ctx, ctx.author.id)

        if not member:
            user = arg_string if arg_string else ctx.author
            await self.bot.embed_print(ctx, f"User `{user}` not found.", color=self.bot.ERROR)
            return

        async with self.bot.pool.acquire() as conn:
            active_player = await conn.fetchrow(sql_select_active_account().format(member.id))

        # If player is no longer active
        if not active_player:
            async with self.bot.pool.acquire() as conn:
                db_discord_member = await conn.fetchrow(sql_select_discord_user_id(), member.id)
                db_clash_accounts = await conn.fetch(sql_select_clash_account_discord_id(), member.id)

            await self.bot.embed_print(ctx, f'User `{member.display_name}` is no longer an active member. You could '
                                            f'query their stats using their clash tag instead if you like.',
                                       color=self.bot.ERROR)
            msg = account_panel(db_discord_member, db_clash_accounts)
            await self.bot.embed_print(ctx, msg)
            return

        player = await self.bot.coc_client.get_player(active_player['clash_tag'])
        panel_a, panel_b = ClashStats(player, active_player, set_lvl=args['display_level']).display_all()
        await self._display_panels(ctx, player, panel_a, panel_b)

    async def _display_panels(self, ctx, player, panel_a, panel_b):
        await self.bot.embed_print(ctx, panel_a, footnote=False)
        panel = await self.bot.embed_print(ctx, panel_b, _return=True)
        panel = await ctx.send(embed=panel)
        await panel.add_reaction(self.bot.settings.emojis['link'])

        def check(reaction, user):
            return not user.bot and str(reaction.emoji) == self.bot.settings.emojis['link']

        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            await ctx.send(player.share_link)
        except asyncio.TimeoutError:
            pass

def setup(bot):
    bot.add_cog(UserStats(bot))