import asyncio
import logging
from datetime import datetime, timedelta

from coc import utils
from disnake.ext import commands
from disnake.member import Member

from bot import BotClient
from packages.clash_stats.clash_stats_panel import ClashStats
from packages.utils.bot_sql import sql_select_active_account, \
    sql_select_user_donation
from packages.utils.utils import get_discord_member, get_utc_monday, parse_args


class UserStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(f"{self.bot.settings.log_name}.UserStats")

    @commands.command(
        aliases=["d"],
        brief="",
        description="View current donation gains",
        usage="(user name)",
        help="Display the current donation gains for the weeks cycle. "
             "You also have the option of providing another users name as an "
             "argument to display their donation gains."
    )
    async def donation(self, ctx, *, arg_string=None):
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="donation",
                                   args=None,
                                   arg_string=arg_string)
        member: Member
        if arg_string:
            member = await get_discord_member(ctx, arg_string)
        else:
            member = await get_discord_member(ctx, ctx.author.id)

        if not member:
            user = arg_string if arg_string else ctx.author
            await self.bot.send(ctx, f"User `{user}` not found.",
                                color=self.bot.ERROR)
            return

        else:
            async with self.bot.pool.acquire() as conn:
                player = await conn.fetchrow(
                    sql_select_active_account().format(member.id))

            if not player:
                await self.bot.send(ctx,
                                    f"User `{member.display_name}` is no "
                                    f"longer an active member",
                                    color=self.bot.WARNING)
                return

        week_start = get_utc_monday()
        async with self.bot.pool.acquire() as conn:
            donation_sql = sql_select_user_donation().format(week_start,
                                                             player[
                                                                 "clash_tag"])
            player_record = await conn.fetchrow(donation_sql)

        if not player_record:
            await self.bot.send(ctx, title="Donation",
                                description="No results return. Please allow 10 minutes "
                                            "to pass to calculate donations")
            return

        week_end = week_start + timedelta(days=7)
        time_remaining = week_end - datetime.utcnow()
        day = time_remaining.days
        time = str(timedelta(seconds=time_remaining.seconds)).split(":")
        msg = f"**Donation Stat:**\n{player_record['donation_gains']} | 300\n**Time Remaining:**\n" \
              f"{day} days {time[0]} hours {time[1]} minutes"
        author = [
            member.display_name,
            member.avatar.url
        ]
        await self.bot.send(ctx, description=msg, author=author)

    @commands.command(
        aliases=["s"],
        brief="",
        description="Display Clash of Clans stats",
        usage="[-c (str)] [-l (int)]",
        help="Display Clash of Clan stats of the caller. You also have the "
             "option of providing someone else\'s name to get their Clash of "
             "Clan stats.\nUsers are also able to provide a level they "
             "would like to display with the -l switch.\nUsers are able "
             "to get Clash of Clan stats by provide ANYONE\'s Clash tag.\n\n"
             "-c || --clash-tag\n-l || --level"
    )
    async def stats(self, ctx, *, arg_string=None):
        arg_dict = {
            "clash_tag": {
                "flags": ["-c", "--clash_tag"],
            },
            "display_level": {
                "flags": ["-l", "--level"],
                "type": "int",
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="stats",
                                   args=args,
                                   arg_string=arg_string)
        if not args:
            return
        member: Member

        # If --clash-tag was supplied the search by
        # clash tag directly instead of by user
        if args["clash_tag"]:
            tag = args["clash_tag"]
            if utils.is_valid_tag(tag):
                player = await self.bot.coc_client.get_player(tag)
                if player:
                    panel_a, panel_b = ClashStats(player).display_troops()
                    await self._display_panels(ctx, player, panel_a, panel_b)
                    return
                else:
                    await self.bot.send(ctx,
                                        description=f"User with the tag of {tag} was not found",
                                        color=self.bot.WARNING)
                    return

        # If clash tag was not used then attempt
        # to get the user by discord accounts
        elif args["positional"]:
            member = await get_discord_member(ctx, args["positional"])
        else:
            member = await get_discord_member(ctx, ctx.author.id)

        if not member:
            user = arg_string if arg_string else ctx.author
            await self.bot.send(ctx, f"User `{user}` not found.",
                                color=self.bot.ERROR)
            return

        async with self.bot.pool.acquire() as conn:
            active_player = await conn.fetchrow(
                sql_select_active_account().format(member.id))

        if not active_player:
            await self.bot.send(ctx,
                                f"User `{member.display_name}` is no longer "
                                f"an active member. You could query their "
                                f"stats using their clash tag instead if you "
                                f"like.",
                                color=self.bot.ERROR)
            return

        player = await self.bot.coc_client.get_player(
            active_player["clash_tag"])
        panel_a, panel_b = ClashStats(player, active_player, set_lvl=args[
            "display_level"]).display_all()
        await self._display_panels(ctx, player, panel_a, panel_b)

        # from discord import Embed
        # clash_stat = ClashStats(player, active_player, set_lvl=['display_level'])
        # embed = Embed.from_dict(clash_stat.to_dict)
        # async with self.bot.pool.acquire() as con:
        #     sql = f"""SELECT discord_user.discord_id from discord_user, clash_account WHERE clash_tag='{player.tag}'
        #     AND discord_user.discord_id=clash_account.discord_id"""
        #     member = await con.fetchval(sql)
        #     member = ctx.guild.get_member(member)
        #
        # embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        # await ctx.send(embed=embed)

    async def _display_panels(self, ctx, player, panel_a, panel_b):
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
