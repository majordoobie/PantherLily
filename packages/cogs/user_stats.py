import logging
from datetime import datetime, timedelta
from typing import Optional

import coc
import disnake
from disnake.ext import commands

from bot import BotClient
from packages.clash_stats.clash_stats_panel import ClashStats
from packages.private.settings import LEVEL_MAX, LEVEL_MIN
from packages.utils.bot_sql import select_active_account, \
    select_user_donation
from packages.utils.utils import EmbedColor, get_utc_monday


class CoCAccountLink(disnake.ui.View):
    def __init__(self, player: coc.Player):
        super().__init__()
        self.player = player
        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary,
                                        label="Game Account Link",
                                        url=self.player.share_link))

        self.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary,
                                        label="Clash of Stats",
                                        url=self.clash_of_stats))

    @property
    def clash_of_stats(self):
        user = f"{'-'.join(self.player.name.split(' '))}-{self.player.tag.lstrip('#')}"
        return f"https://www.clashofstats.com/players/{user}/summary"


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
    async def donation(
            self,
            inter: disnake.ApplicationCommandInteraction,
            member: disnake.Member = commands.Param(lambda inter: inter.author)
                       ) -> None:
        """
        Display the current donation gains for the weeks cycle

        Parameters
        ----------
        ctx: disnake.ApplicationCommandInteraction
        member: Optional discord member to specify
        """

        async with self.bot.pool.acquire() as conn:
            player = await conn.fetchrow(
                select_active_account().format(member.id))

        if not player:
            await self.bot.inter_send(
                inter,
                panel=f"User `{member.display_name}` is not an active member",
                color=EmbedColor.WARNING)
            return

        week_start = get_utc_monday()
        async with self.bot.pool.acquire() as conn:
            donation_sql = select_user_donation().format(
                week_start,
                player["clash_tag"])
            player_record = await conn.fetchrow(donation_sql)

        if not player_record:
            await self.bot.inter_send(
                inter,
                title="Donation",
                panel="No results return. Please allow 10 minutes to "
                      "pass to calculate donations")
            return

        week_end = week_start + timedelta(days=7)
        time_remaining = week_end - datetime.utcnow()
        day = time_remaining.days
        time = str(timedelta(seconds=time_remaining.seconds)).split(":")
        msg = (f"**Donation Stat:**\n{player_record['donation_gains']} "
               f"| 300\n**Time Remaining:**\n{day} days {time[0]} "
               f"hours {time[1]} minutes")

        await self.bot.inter_send(inter, panel=msg, author=member)

    @commands.slash_command(
        auto_sync=True,
        name="stats",
        dm_permission=False,
    )
    async def stats(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(lambda inter: inter.author),
        clash_tag: str = None,
        display_level: commands.Range[LEVEL_MIN, LEVEL_MAX] = 0
    ) -> None:
        """
        Display the stats of the Clash of Clans caller or specified user

        Parameters
        ----------
        inter: disnake.ApplicationCommandInteraction
        member: Optional discord member to specify
        clash_tag: Optional clash of clans tag to retrieve
        display_level: Optional level to display useful for viewing a level up
        """

        # Goal of parameters it to fetch a valid player
        # object to display data from
        player: Optional[coc.Player] = None
        active_player = None

        # Normalize the parameters if defaults are set
        if clash_tag is not None:
            clash_tag = coc.utils.correct_tag(clash_tag)
            if coc.utils.is_valid_tag(clash_tag):

                try:
                    player = await self.bot.coc_client.get_player(clash_tag)
                except coc.errors.NotFound:
                    pass

                if not player:
                    await self.bot.inter_send(
                        inter,
                        panel=f"User with the tag of {clash_tag} "
                              f"was not found",
                        color=EmbedColor.WARNING)
                    return
            else:
                await self.bot.inter_send(
                    inter,
                    panel=f"{clash_tag} is an invalid tag",
                    color=EmbedColor.WARNING)
                return

        else:
            async with self.bot.pool.acquire() as conn:
                active_player = await conn.fetchrow(
                    select_active_account().format(member.id))
                if not active_player:
                    await self.bot.inter_send(
                        inter,
                        f"User `{member.display_name}` is not "
                        f"an active member. You could query their "
                        f"stats using their clash tag instead if you "
                        f"like.",
                        color=EmbedColor.WARNING)
                    return
                else:
                    player = await self.bot.coc_client.get_player(
                        active_player["clash_tag"])

        if display_level == 0:
            display_level = player.town_hall

        panel_a, panel_b = ClashStats(player,
                                      active_player,
                                      set_lvl=display_level
                                      ).display_all()

        await self.bot.inter_send(inter,
                                  panels=[panel_a, panel_b],
                                  view=CoCAccountLink(player))


def setup(bot):
    bot.add_cog(UserStats(bot))
