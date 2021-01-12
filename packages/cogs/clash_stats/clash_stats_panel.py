import json

from coc import Player

HOME = '/opt/project/packages/cogs/clash_stats/'

class ClashStats:
    """Build stats output"""
    def __init__(self, player: Player, active_player: dict, set_lvl=None):
        """
        set_lvl is going to be an int
        """
        import os
        print(os.getcwd())
        self.em = self.load_emojis()
        self.tr = self.load_troop()
        self.player = player
        self.member = active_player
        if set_lvl:
            self.lvl = self.get_lvl(set_lvl)
        else:
            self.lvl = str(player.town_hall)

    def load_troop(self):
        with open(HOME+'clash_stats_levels.json', 'rt') as trooplevels:
            f = json.load(trooplevels)
            return f

    def load_emojis(self):
        with open(HOME+'clash_stats_emoji.json', 'rt') as emojis:
            f = json.load(emojis)
            return f

    def get_lvl(self, set_lvl):
        if isinstance(set_lvl, int):
            if set_lvl in range(8, 14):
                return str(set_lvl)
            else:
                return str(self.player.town_hall)
        elif isinstance(set_lvl, str):
            if set_lvl.isdigit():
                set_lvl = int(set_lvl)
                if set_lvl in range(8, 14):
                    return str(set_lvl)
            else:
                return str(self.player.town_hall)
        else:
            return str(self.player.town_hall)

    def payload(self):
        title = (f"""
{self.em['townhalls'][str(self.player.town_hall)]} {self.player.name}
        """)
        frame = (f"""
`{'Role:':<15}` `{self.player.role:<15}`
`{'Player Tag:':<15}` `{self.player.tag:<15}`
""")
        if self.player.town_hall > 11:
            frame += (f"""\
`{'TH Weapon LvL:':<15}` `{self.player.town_hall_weapon:<15}`
            """)
        frame += (f"""
`{'Member Status:':<15}` `{'True' if self.member['is_active'] else 'False':<15}`
`{'Joined Date:':<15}` `{self.member['guild_join_date'].strftime('%Y-%b-%d'):<15}`
`{'Current Clan:':<15}` `{self.player.clan.name:<15.15}`
`{'League:':<15}` `{self.player.league.name:<15.15}`
`{'Trophies:':<15}` `{self.player.trophies:<15}`
`{'Best Trophies:':<15}` `{self.player.best_trophies:<15}`
`{'War Stars:':<15}` `{self.player.war_stars:<15}`
`{'Attack Wins:':<15}` `{self.player.attack_wins:<15}`
`{'Defense Wins:':<15}` `{self.player.defense_wins:<15}`
**__Displaying Level:__** `{self.lvl}`
{self.get_heroes()}
{self.get_sieges()}
{self.get_troops()}
{self.get_spells()}
""")
        #TODO: add ashare link!

        return frame, title

    def get_heroes(self):
        frame = '**Heroes**\n'
        for hero in self.player.heroes:
            try:
                emoji = self.em['heroes'][hero.name]
                current_lvl = hero.level
                max_lvl = self.tr[self.lvl][hero.name]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
            except KeyError:
                continue
        return frame

    def get_sieges(self):
        frame = ''
        for siege in self.player.siege_machines:
            try:
                emoji = self.em['siege'][siege.name]
                current_lvl = siege.level
                max_lvl = self.tr[self.lvl][siege.name]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
            except KeyError:
                continue
        if frame:
            _frame = '**Sieges**\n'
            _frame += frame
            return _frame
        return frame

    def get_troops(self):
        frame = '**Troops**\n'
        count = 0
        for troop in self.player.troops:
            try:
                emoji = self.em['troops'][troop.name]
                current_lvl = troop.level
                max_lvl = self.tr[self.lvl][troop.name]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                continue
        return frame

    def get_spells(self):
        frame = '**Spells**\n'
        count = 0
        for spell in self.player.spells:
            try:
                emoji = self.em['spells'][spell.name]
                current_lvl = spell.level
                max_lvl = self.tr[self.lvl][spell.name]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                continue
        return frame
