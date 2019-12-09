import json

class Clash_Stats:
    def __init__(self, player, _max, emoticons):
        self.em = emoticons
        self.tr = self.load_troop()
        self.player = player

    def load_troop(self):
        with open("utils/clash_of_clans/clash_troop_levels.json", "r") as trooplevels:
            return json.load(trooplevels)

    def payload(self, level):
        if level.isdigit() or level != None:
            if int(level) in (8,9,10,11,12,13):
                self.l = level
        else:
            self.l = self.player.town_hall

        frame = (f"""      
`{'Role:'} ` `{self.player.role}`
`{'Player Tag:'} ` `{self.player.tag}`
`{'Town Hall:'} ` `{self.em['townhalls'][str(self.player.town_hall)]}`
""")
        return frame