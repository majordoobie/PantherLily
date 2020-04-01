import json
from pathlib import Path
WORK_DIR = Path(__file__).resolve().parent

SIEGES = (
    "Wall Wrecker",
    "Battle Blimp",
    "Stone Slammer",
    "Siege Barracks"
)
class ClashStats:
    """Build stats output"""
    def __init__(self, player, set_lvl=None):
        """
        set_lvl is going to be an int
        """
        self.em = self.load_emojis()
        self.tr = self.load_troop()
        self.player = player
        if set_lvl:
            self.lvl = self.get_lvl(set_lvl)
        else:
            self.lvl = str(player.town_hall)

    def load_troop(self):
        with open(WORK_DIR/'clash_troop_levels.json', "r") as trooplevels:
            f = json.load(trooplevels)
            return f

    def load_emojis(self):
        with open(WORK_DIR/"clash_emoji.json", "r") as emojis:
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

    def payload(self, joined_at, active):
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
`{'Member Status:':<15}` `{active:<15}`
`{'Joined Date:':<15}` `{joined_at:<15}`
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
        for hero in self.player.ordered_heroes:
            if hero == 'Battle Machine':
                continue
            try:
                emoji = self.em['heroes'][hero]
                current_lvl = self.player.heroes_dict[hero].level
                max_lvl = self.tr[self.lvl][hero]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
            except KeyError:
                pass
        return frame

    def get_sieges(self):
        frame = ''
        for siege in self.player.ordered_home_troops:
            if siege in SIEGES:
                try:
                    emoji = self.em['siege'][siege]
                    current_lvl = self.player.home_troops_dict[siege].level
                    max_lvl = self.tr[self.lvl][siege]
                    frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                except KeyError:
                    pass
        if frame:
            _frame = '**Sieges**\n'
            _frame += frame
            return _frame
        return frame

    def get_troops(self):
        frame = '**Troops**\n'
        count = 0
        for troop in self.player.ordered_home_troops:
            if troop not in SIEGES:
                try:
                    emoji = self.em['troops'][troop]
                    current_lvl = self.player.home_troops_dict[troop].level
                    max_lvl = self.tr[self.lvl][troop]
                    frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                    count += 1
                    if count == 4:
                        frame += '\n'
                        count = 0
                except KeyError:
                    pass
        return frame

    def get_spells(self):
        frame = '**Spells**\n'
        count = 0
        for spell in self.player.ordered_spells:
            try:
                emoji = self.em['spells'][spell]
                current_lvl = self.player.spells_dict[spell].level
                max_lvl = self.tr[self.lvl][spell]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
            except KeyError:
                pass
        return frame