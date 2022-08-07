from coc import Player
from packages.clash_stats.clash_stats_levels import get_levels
from packages.private.settings import LEVEL_MAX, LEVEL_MIN

HERO_PETS_ORDER = ["L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn"]


class ClashStats:
    TOWN_HALLS = {
        "14": "<:14:828991721181806623>",
        "13": "<:th13:651099879686406145>",
        "12": "<:townhall12:546080710406963203>",
        "11": "<:townhall11:546080741545738260>",
        "10": "<:townhall10:546080756628324353>",
        "9": "<:townhall9:546080772118020097>",
        "8": "<:townhall8:546080798097539082>"
    }

    def __init__(self, player: Player, active_player: dict = None, set_lvl=None):
        """Display an embedded panel containing user stats"""
        self.player = player
        self.member = active_player
        if set_lvl:
            self.town_hall = self._get_lvl(set_lvl)
        else:
            self.town_hall = str(player.town_hall)
        self.troops = get_levels(int(self.town_hall))
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

    def _get_heroes_panel(self):
        frame = '**Heroes**\n'
        count = 0
        for hero in self.player.heroes:
            try:
                emoji = self.troops[hero.name].emoji
                current_lvl = hero.level
                max_lvl = self.troops[hero.name].max_level
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += "\n"
                    count = 0
            except KeyError:
                continue

        if frame[-1] != "\n":
            frame += "\n"
        return frame

    def _get_hero_pets_panel(self):
        frame = ""
        count = 0
        for troop in self.player.troops:
            if troop.name in HERO_PETS_ORDER:
                try:
                    emoji = self.troops[troop.name].emoji
                    current_lvl = troop.level
                    max_lvl = self.troops[troop.name].max_level
                    frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                    count += 1
                    if count == 4:
                        frame += "\n"
                        count = 0
                except KeyError:
                    continue

        if frame:
            _frame = "**Hero Pets**\n"
            _frame += frame
            if _frame[-1] != "\n":
                _frame += "\n"
            return _frame

        return frame
        pass

    def _get_sieges_panel(self):
        frame = ''
        count = 0
        for siege in self.player.siege_machines:
            try:
                emoji = self.troops[siege.name].emoji
                current_lvl = siege.level
                max_lvl = self.troops[siege.name].max_level
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                continue
        if frame:
            _frame = '**Sieges**\n'
            _frame += frame
            if _frame[-1] != "\n":
                _frame += "\n"
            return _frame

        return frame

    def _get_troops_panels(self):
        frame = '**Troops**\n'
        count = 0
        for troop in self.player.home_troops:
            # Skip the sieges from this panel
            if troop in self.player.siege_machines or troop in HERO_PETS_ORDER:
                continue
            try:
                emoji = self.troops[troop.name].emoji
                current_lvl = troop.level
                max_lvl = self.troops[troop.name].max_level
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                continue

        if frame[-1] != "\n":
            frame += "\n"
        return frame

    def _get_spells_panels(self):
        frame = '**Spells**\n'
        count = 0
        for spell in self.player.spells:
            try:
                emoji = self.troops[spell.name].emoji
                current_lvl = spell.level
                max_lvl = self.troops[spell.name].max_level
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                continue

        if frame[-1] != "\n":
            frame += "\n"

        return frame

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
                  f'{self.siege_panel}{self.troop_panel}{self.spell_panel}'
        return panel_a, panel_b

    def display_troops(self):
        panel_a = f'{self.title}\n{self.administration_panel}\n'
        panel_b = f'{self.hero_panel}{self.hero_pets_panel}{self.siege_panel}{self.troop_panel}{self.spell_panel}'
        return panel_a, panel_b
