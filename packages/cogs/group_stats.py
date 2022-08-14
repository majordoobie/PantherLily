import asyncio
from datetime import timedelta

import disnake
from disnake.ext import commands
import logging

from bot import BotClient
import packages.utils.bot_sql as sql
from packages.utils.paginator import Paginator
from packages.utils.utils import parse_args, get_utc_monday


class RosterSearch(disnake.ui.View):
    def __init__(self, bot: BotClient,
                 inter: disnake.ApplicationCommandInteraction,
                 clan_locations: dict):
        super().__init__()
        self.bot = bot
        self.inter = inter
        self.clan = clan_locations

    @disnake.ui.button(label="Show Locations",
                       style=disnake.ButtonStyle.blurple)
    async def confirm(self,
                      button: disnake.Button,
                      inter: disnake.MessageInteraction):
        location_panels = ''
        for clan, players in self.clan.items():
            panel = f'__**{clan}**__\n'
            for player in players:
                panel += f"`{player['name']:<15.15}{player['clash_tag']:<13.13}`\n"

            location_panels += panel

        await self.bot.inter_send(inter, location_panels)
        self.stop()


class GroupStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(
            f'{self.bot.settings.log_name}.GroupStats')

    @commands.slash_command(
        name="roster",
        auto_sync=True,
        dm_permission=False
    )
    async def roster(self,
                     inter: disnake.ApplicationCommandInteraction) -> None:
        """
        Display the currently registered users and users in the clan.

        Parameters
        ----------
        inter: Interaction object
        """

        panels = []

        # Create legend to display
        clan = self.bot.settings.emojis["reddit_zulu"]
        db = self.bot.settings.emojis["database"]
        waze = self.bot.settings.emojis["waze"]
        true = self.bot.settings.emojis["true"]
        false = self.bot.settings.emojis["false"]

        legend = f'{clan} Member is in Reddit Zulu in-game.\n'
        legend += f'{db} Member is registered with Pantherlily.\n'
        legend += f'{waze} Get realtime location of members.\n'

        panels.append(legend)

        # Get users and sort them by name
        async with self.bot.pool.acquire() as con:
            members_db = await con.fetch(
                sql.select_all_active_users().format(get_utc_monday()))
            unregistered_users = await con.fetch(
                sql.select_clash_members_not_registered())
        members_db.sort(key=lambda x: x['clash_name'].lower())

        roster = {}
        clan_locations = {}
        strength_count = 0
        strength = {}
        for member in members_db:
            strength_count += 1
            town_hall = strength.get(member['town_hall'])
            if town_hall:
                strength[member['town_hall']] += 1
            else:
                strength[member['town_hall']] = 1

            roster[member['clash_name']] = {
                "in_mother_clan": _in_clan(member['current_clan_tag']),
                "in_discord": member['in_zulu_server'],
                "in_database": True,
                "clash_tag": member['clash_tag']
            }

            clan_location = clan_locations.get(member['current_clan_name'])
            if clan_location:
                clan_locations[member['current_clan_name']].append({
                    'name': member['clash_name'],
                    'town_hall': member['town_hall'],
                    "clash_tag": member['clash_tag']
                })
            else:
                clan_locations[member['current_clan_name']] = [{
                    'name': member['clash_name'],
                    'town_hall': member['town_hall'],
                    "clash_tag": member['clash_tag']
                }]

        for player in unregistered_users:
            roster[player['player_name']] = {
                'in_mother_clan': True,
                'in_discord': False,
                'in_database': False,
                "clash_tag": player['clash_tag']
            }
        # Display the roster panel
        panel = f'{clan}{db}\n'
        count = 0
        for player, stats in roster.items():
            panel += true if stats['in_mother_clan'] else false
            panel += true if stats['in_database'] else false
            count += 1
            panel += f"  **{count:>2}**  {player}\n"

        panels.append(panel)
        # await self.bot.send(inter, panel, footnote=False)

        # Create the strength panel the tiny one that shows how many there are
        strength_panel = f'__**Registered Members**__\n`{"Total members:":{self.bot.space}<15}{strength_count:>2}`\n'
        levels = [level for level in strength.keys()]
        levels.sort(reverse=True)
        for level in levels:
            town_hall = f'Total TH{level}:'
            strength_panel += f"`{town_hall:<15}{strength[level]:>2}`\n"

        panels.append(strength_panel)
        await self.bot.inter_send(inter, panels=panels,
                                  view=RosterSearch(self.bot,
                                                    inter,
                                                    clan_locations))

    @commands.slash_command(
        name="top",
        auto_sync=True,
        dm_permission=False
    )
    async def top(self,
                  inter: disnake.ApplicationCommandInteraction,
                  weeks: int = 1) -> None:
        """
        Display top trophies and donations in the clan

        Parameters
        ----------
        inter:
        weeks: Number of weeks to display
        """

        # Get the amount of weeks to pull back
        dates = []
        for i in range(0, weeks):
            dates.append(get_utc_monday() - timedelta(days=(i * 7)))

        # Get report blocks based on dates
        data_blocks = []
        async with self.bot.pool.acquire() as con:
            for date in dates:
                players = await con.fetch(
                    sql.select_classic_view().format(date))
                data_blocks.append(players)

        trophies = []
        donations = []
        for date, players in enumerate(data_blocks):
            players.sort(key=lambda x: x['current_trophy'], reverse=True)
            t_frame = f'__**Trophy Ranking**__\n'
            t_frame += f"`{'rk':<3}{'th':<3}{'trop':<5}{'diff':>3}`\n"
            for count, player in enumerate(players):
                count += 1
                name = player['clash_name'][:14]
                t_frame += f"`{count:<3}{player['town_hall']:<3}{player['current_trophy']:<5}" \
                           f"{player['trophy_diff']:<5}{name:<11.11}`\n"
            t_frame += f'`Week of: {dates[date].strftime("%Y-%m-%d")}`'
            trophies.append(t_frame)

        for date, players in enumerate(data_blocks):
            players.sort(key=lambda x: x['donation_gains'], reverse=True)
            d_frame = f'__**Donation Ranking**__\n'
            d_frame += f"`{'rk':<3}{'th':<3}{'Donation':<9}`\n"
            for count, player in enumerate(players[:20]):
                count += 1
                d_frame += f"`{str(count):<3}{player['town_hall']:<3}{player['donation_gains']:<5}" \
                           f"{player['clash_name']:<14.14}`\n"

            d_frame += f'`Week of: {dates[date].strftime("%Y-%m-%d")}`'
            donations.append(d_frame)

        embeds = await self.bot.inter_send(inter, panels=donations + trophies,
                                           return_embed=True,
                                           flatten_list=True)

        view = Paginator(embeds)
        await inter.send(embeds=view.embed, view=view)


def _in_clan(clan_tag: str) -> bool:
    if clan_tag == '#2Y28CGP8':
        return True
    return False


def setup(bot):
    bot.add_cog(GroupStats(bot))
