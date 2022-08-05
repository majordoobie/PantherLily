import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import coc
import disnake
from disnake.ext import commands

from bot import BotClient
from packages.clash_stats.clash_stats_panel import ClashStats
from packages.utils.bot_sql import sql_select_active_account, \
    sql_select_user_donation
from packages.utils.utils import get_discord_member, get_utc_monday, parse_args

from packages.private.settings import LEVEL_MIN, LEVEL_MAX


class UserStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(f"{self.bot.settings.log_name}.UserStats")

    @commands.slash_command(
        auto_sync=True,
        name="donation",
        dm_permission=False,
        sync_commands_debug=True
    )
    async def donation(self, ctx, member: disnake.Member = None):
        """
        Display the current donation gains for the weeks cycle

        Parameters
        ----------
        ctx: disnake.ApplicationCommandInteraction
        member: Optional discord member to specify
        """
        if member is None:
            member = ctx.author

        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="donation",
                                   args=None,
                                   arg_string=member)

        async with self.bot.pool.acquire() as conn:
            player = await conn.fetchrow(
                sql_select_active_account().format(member.id))

        if not player:
            await self.bot.send(
                ctx,
                f"User `{member.display_name}` is no longer an active member",
                color=self.bot.WARNING)
            return

        week_start = get_utc_monday()
        async with self.bot.pool.acquire() as conn:
            donation_sql = sql_select_user_donation().format(
                week_start,
                player["clash_tag"])
            player_record = await conn.fetchrow(donation_sql)

        if not player_record:
            await self.bot.send(
                ctx,
                title="Donation",
                description="No results return. Please allow 10 minutes to "
                            "pass to calculate donations")
            return

        week_end = week_start + timedelta(days=7)
        time_remaining = week_end - datetime.utcnow()
        day = time_remaining.days
        time = str(timedelta(seconds=time_remaining.seconds)).split(":")
        msg = (f"**Donation Stat:**\n{player_record['donation_gains']} "
               f"| 300\n**Time Remaining:**\n{day} days {time[0]} "
               f"hours {time[1]} minutes")
        author = [
            member.display_name,
            member.avatar.url
        ]
        await self.bot.send(ctx, description=msg, author=author)

    @commands.slash_command(
        auto_sync=True,
        name="stats",
        dm_permission=False,
    )
    async def stats(
        self,
        ctx,
        member: disnake.Member = None,
        clash_tag: str = None,
        display_level: commands.Range[LEVEL_MIN, LEVEL_MAX] = 0
    ) -> None:
        """
        Display the stats of the Clash of Clans caller or specified user

        Parameters
        ----------
        ctx: disnake.ApplicationCommandInteraction
        member: Optional discord member to specify
        clash_tag: Optional clash of clans tag to retrieve
        display_level: Optional level to display useful for viewing a level up
        """

        # Goal of parameters it to fetch a valid player
        # object to display data from
        player: Optional[coc.Player] = None

        # Normalize the parameters if defaults are set
        if member is None and clash_tag is not None:
            clash_tag = coc.utils.correct_tag(clash_tag)
            if coc.utils.is_valid_tag(clash_tag):

                try:
                    player = await self.bot.coc_client.get_player(clash_tag)
                except coc.errors.NotFound:
                    pass

                if not player:
                    await self.bot.send(
                        ctx,
                        description=f"User with the tag of {clash_tag} "
                                    f"was not found",
                        color=self.bot.WARNING)
            else:
                await self.bot.send(
                    ctx,
                    description=f"{clash_tag} is an invalid tag",
                    color=self.bot.WARNING)

        else:
            if member is None:
                member = ctx.author
            async with self.bot.pool.acquire() as conn:
                active_player = await conn.fetchrow(
                    sql_select_active_account().format(member.id))
                if not active_player:
                    await self.bot.send(
                        ctx,
                        f"User `{member.display_name}` is no longer "
                        f"an active member. You could query their "
                        f"stats using their clash tag instead if you "
                        f"like.",
                        color=self.bot.ERROR)
                else:
                    player = await self.bot.coc_client.get_player(
                        active_player["clash_tag"])

        if display_level == 0:
            display_level = player.town_hall

        # Log the user command
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="stats",
                                   member=member,
                                   clash_tag=clash_tag,
                                   display_level=display_level
                                   )
        panel_a, panel_b = ClashStats(player,
                                      active_player,
                                      set_lvl=display_level
                                      ).display_all()

        await self._display_panels(ctx, player, panel_a, panel_b)

    async def _display_panels(self, ctx, player, panel_a, panel_b):
        # TODO: Fix the reaction
        await self.bot.send(ctx, panel_a, footnote=False)
        panel = await self.bot.send(ctx, panel_b, _return=True)
        panel = await ctx.send(embed=panel[0])
        await panel.add_reaction(self.bot.settings.emojis["link"])

        def check(reaction, user):
            return not user.bot and str(reaction.emoji) == \
                   self.bot.settings.emojis["link"]

        try:
            await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            await ctx.send(player.share_link)
        except asyncio.TimeoutError:
            pass


def setup(bot):
    bot.add_cog(UserStats(bot))
