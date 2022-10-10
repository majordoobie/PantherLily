from typing import List, Optional

import coc
import pandas as pd
from packages.clash_stats.clash_stats_levels import get_df_and_level, get_df_level
from packages.private.settings import LEVEL_MAX, LEVEL_MIN

HERO_PETS_ORDER = ["L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn"]


class ClashStats:
    TOWN_HALLS = {
        "15": "<:15:1028478312928002118>",
        "14": "<:14:828991721181806623>",
        "13": "<:th13:651099879686406145>",
        "12": "<:townhall12:546080710406963203>",
        "11": "<:townhall11:546080741545738260>",
        "10": "<:townhall10:546080756628324353>",
        "9": "<:townhall9:546080772118020097>",
        "8": "<:townhall8:546080798097539082>",
        "warning": "<:warning:807778609825447968>",
    }

    def __init__(self,
                 player: coc.Player,
                 active_player: Optional[dict] = None,
                 set_lvl=None,
                 troop_df: Optional[pd.DataFrame]=None):
        """
        Create the panel used to display the users stats

        :param player: The CoC Player object
        :param active_player: Optional database object of the registered player
        :param set_lvl: Level to set the user display
        """
        self.player = player
        self.member = active_player
        if set_lvl:
            self.town_hall = self._get_lvl(set_lvl)
        else:
            self.town_hall = str(player.town_hall)

        if troop_df is not None:
            self.troops = get_df_level(troop_df, int(self.town_hall))
        else:
            self.troops = get_df_and_level(int(self.town_hall))
        self._set_panels()

    def _get_lvl(self, set_lvl):
        """Private function to get the troop level of a specific level"""
        if isinstance(set_lvl, int):
            if set_lvl in range(LEVEL_MIN, LEVEL_MAX + 1):
                return str(set_lvl)
            else:
                return str(self.player.town_hall)
        elif isinstance(set_lvl, str):
            if set_lvl.isdigit():
                set_lvl = int(set_lvl)
                if set_lvl in range(LEVEL_MIN, LEVEL_MAX + 1):
                    return str(set_lvl)
            else:
                return str(self.player.town_hall)
        else:
            return str(self.player.town_hall)

    def _set_panels(self):
        self.title = f'{self.TOWN_HALLS[str(self.player.town_hall)]} **{self.player.name}**'
        if self.member:
            self.administration_panel = self._get_administration_panel()
        else:
            self.administration_panel = self._get_light_admin_panel()
        self.hero_panel = self._get_heroes_panel()
        self.hero_pets_panel = self._get_hero_pets_panel()
        self.troop_panel = self._get_troops_panels()
        self.siege_panel = self._get_sieges_panel()
        self.spell_panel = self._get_spells_panels()
        self.super_troops = self._get_super_panels()

    def _get_administration_panel(self) -> str:
        """Creates the administration information. This should only be available to registered users"""
        frame = ''
        if self.player.town_hall > 11:
            frame += f"`{'TH Weapon LvL:':<15}` `{self.player.town_hall_weapon:<15}`\n"
        role = self.player.role if self.player.role else 'None'
        clan = self.player.clan.name if self.player.clan else 'None'
        frame += (
            f"`{'Role:':<15}` `{role:<15}`\n"
            f"`{'Player Tag:':<15}` `{self.player.tag:<15}`\n"
            f"`{'Member Status:':<15}` `{'True' if self.member['is_active'] else 'False':<15}`\n"
            f"`{'Joined Date:':<15}` `{self.member['guild_join_date'].strftime('%Y-%b-%d'):<15}`\n"
            f"`{'Current Clan:':<15}` `{clan:<15.15}`\n"
            f"`{'League:':<15}` `{self.player.league.name:<15.15}`\n"
            f"`{'Trophies:':<15}` `{self.player.trophies:<15}`\n"
            f"`{'Best Trophies:':<15}` `{self.player.best_trophies:<15}`\n"
            f"`{'War Stars:':<15}` `{self.player.war_stars:<15}`\n"
            f"`{'Attack Wins:':<15}` `{self.player.attack_wins:<15}`\n"
            f"`{'Defense Wins:':<15}` `{self.player.defense_wins:<15}`\n"
        )
        return frame

    def _get_light_admin_panel(self):
        frame = ''
        role = self.player.role if self.player.role else 'None'
        clan = self.player.clan.name if self.player.clan else 'None'
        if self.player.town_hall > 11:
            frame += f"`{'TH Weapon LvL:':<15}` `{self.player.town_hall_weapon:<15}`\n"
        frame += (
            f"`{'Role:':<15}` `{role:<15}`\n"
            f"`{'Player Tag:':<15}` `{self.player.tag:<15}`\n"
            f"`{'Current Clan:':<15}` `{clan:<15.15}`\n"
            f"`{'League:':<15}` `{self.player.league.name:<15.15}`\n"
            f"`{'Trophies:':<15}` `{self.player.trophies:<15}`\n"
            f"`{'Best Trophies:':<15}` `{self.player.best_trophies:<15}`\n"
            f"`{'War Stars:':<15}` `{self.player.war_stars:<15}`\n"
            f"`{'Attack Wins:':<15}` `{self.player.attack_wins:<15}`\n"
            f"`{'Defense Wins:':<15}` `{self.player.defense_wins:<15}`\n"
        )
        return frame

    def _build_frame(self, coc_objs: List, frame: str) -> str:
        """Iterates over the list of objects and builds the frame string"""
        count = 0
        if not coc_objs or coc_objs is None:
            return ""
        for obj in coc_objs:
            obj_df = self.troops.get(obj.name)
            if obj_df is not None:
                emoji = obj_df.emoji
                if pd.isna(emoji):
                    emoji = ClashStats.TOWN_HALLS.get("warning")
                current_lvl = obj.level
                max_lvl = obj_df.max_level
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
        if frame[-1] != "\n":
            frame += "\n"
        return frame

    def _get_super_panels(self):
        troops = [i for i in self.player.super_troops if i.is_active]
        frame = "**Active Super Troops**\n"
        if troops:
            count = 0
            for troop in troops:
                obj_df = self.troops.get(troop.name)
                if obj_df is not None:
                    emoji = obj_df.emoji
                    if pd.isna(emoji):
                        emoji = ClashStats.TOWN_HALLS.get("warning")
                    frame += f"{emoji} `{troop.name}`\n"
                    count += 1
                    if count == 4:
                        frame += '\n'
                        count = 0
            if frame[-1] != "\n":
                frame += "\n"
            return frame
        return ""

    def _get_heroes_panel(self):
        frame = '**Heroes**\n'
        return self._build_frame(self.player.heroes, frame)

    def _get_hero_pets_panel(self):
        frame = ""
        frame = self._build_frame(self.player.hero_pets, frame)
        if frame:
            _frame = "**Hero Pets**\n"
            _frame += frame
            frame = _frame
        return frame

    def _get_sieges_panel(self):
        frame = ""
        frame = self._build_frame(self.player.siege_machines, frame)
        if frame:
            _frame = "**Siege Machines**\n"
            _frame += frame
            frame = _frame
        return frame

    def _get_troops_panels(self):
        frame = '**Troops**\n'
        exclusions = self.player.siege_machines + self.player.hero_pets + self.player.super_troops
        troops = []
        for troop in self.player.home_troops:
            if troop not in exclusions:
                troops.append(troop)
        return self._build_frame(troops, frame)

    def _get_spells_panels(self):
        frame = '**Spells**\n'
        return self._build_frame(self.player.spells, frame)

    @property
    def to_dict(self) -> dict:
        return {
            'color': 0x000080,
            'fields': [
                {
                    'name': f'{self.TOWN_HALLS[str(self.player.town_hall)]}',
                    'value': self.administration_panel
                },
                {
                    'name': '**Heroes**',
                    'value': '\n'.join(self._get_heroes_panel().split('\n')[1:])
                },
                {
                    'name': '**Sieges**',
                    'value': '\n'.join(self._get_sieges_panel().split('\n')[1:])
                },
                {
                    'name': '**Troops**',
                    'value': '\n'.join(self._get_troops_panels().split('\n')[1:])
                },
                {
                    'name': '**Spells**',
                    'value': '\n'.join(self._get_spells_panels().split('\n')[1:])
                },
            ]
        }

    def display_all(self):
        panel_a = f'{self.title}\n{self.administration_panel}\n'
        panel_b = f'**__Displaying Level:__** `{self.town_hall}`\n{self.hero_panel}{self.hero_pets_panel}' \
                  f'{self.siege_panel}{self.troop_panel}{self.spell_panel}{self.super_troops}'
        return panel_a, panel_b

    def display_troops(self):
        panel_a = f'{self.title}\n{self.administration_panel}\n'
        panel_b = f'{self.hero_panel}{self.hero_pets_panel}{self.siege_panel}' \
                  f'{self.troop_panel}{self.spell_panel}{self.super_troops}'
        return panel_a, panel_b
