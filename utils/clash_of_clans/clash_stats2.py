import json

SIEGES = (
    "Wall Wrecker",
    "Battle Blimp",
    "Stone Slammer"
)
class Clash_Stats:
    def __init__(self, player, set_lvl=None):
        """
        set_lvl is going to be an int
        """
        self.em = self.load_emojis()
        self.tr = self.load_troop()
        self.player = player
        if set_lvl:
            self.lvl = str(self.get_lvl(set_lvl))
        else:
            self.lvl = str(player.town_hall)

    def load_troop(self):
        with open("utils/clash_of_clans/clash_troop_levels.json", "r") as trooplevels:
            return json.load(trooplevels)
    def load_emojis(self):
        with open("/home/doob/Documents/Bots/beta_folder/Pantherlily_v2/PantherLily/utils/clash_of_clans/clash_emoji.json", "r") as emojis:
            return json.load(emojis)
    
    def get_lvl(self, set_lvl):
        if isinstance(set_lvl, int):
            if set_lvl in range(8, 14):
                return set_lvl
            else:
                return self.player.town_hall
        else:
            return self.player.town_hall

    def payload(self):
        title = (f"""
{self.em['townhalls'][str(self.player.town_hall)]} {self.player.name}
        """)
        frame = (f"""
`{'Player Tag:':<15}` `{self.player.tag:<15}`
`{'Current Clan:':<15}` `{self.player.clan.name:<15.15}`
`{'Role:':<15}` `{self.player.role:<15}`
`{'League:':<15}` `{self.player.league.name:<15.15}`
`{'Current Trophy:':<15}` `{self.player.trophies:<15}`
`{'Best Trophoes:':<15}` `{self.player.best_trophies:<15}`
`{'War Stars:':<15}` `{self.player.war_stars:<15}`
`{'Attack Wins:':<15}` `{self.player.attack_wins:<15}`
`{'Defense Wins:':<15}` `{self.player.defense_wins:<15}`
{self.get_heroes()}
{self.get_sieges()}
{self.get_troops()}
""")

        return frame, title

    def get_heroes(self):
        frame = '**Heroes**\n'
        for hero in self.player.ordered_heroes:
            if hero == 'Battle Machine':
                continue
            emoji = self.em['heroes'][hero]
            current_lvl = self.player.heroes_dict[hero].level
            max_lvl = self.tr[self.lvl][hero]
            frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
        return frame

    def get_sieges(self):
        frame = ''
        for siege in self.player.ordered_home_troops:
            if siege in SIEGES:
                emoji = self.em['siege'][siege]
                current_lvl = self.player.home_troops_dict[siege].level
                max_lvl = self.tr[self.lvl][siege]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
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
                emoji = self.em['troops'][troop]
                current_lvl = self.player.home_troops_dict[troop].level
                max_lvl = self.tr[self.lvl][troop]
                frame += f"{emoji}`{current_lvl:>2}|{max_lvl:<2}`"
                count += 1
                if count == 4:
                    frame += '\n'
                    count = 0
        return frame