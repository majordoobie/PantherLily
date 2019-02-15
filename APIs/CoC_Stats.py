class ClashStats():
    def __init__(self, jjson):
        """
        Class used to identify the stats of the user

        Parameters:
            jjson   (json):     json of the data returned form CoC_API
        """
        # First Level
        self.tag = jjson['tag']
        self.name = jjson['name']
        self.townHallLevel = jjson['townHallLevel']
        self.expLevel = jjson['expLevel']
        self.trophies = jjson['trophies']
        self.bestTrophies = jjson['bestTrophies']
        self.warStars = jjson['warStars']
        self.attackWins = jjson['attackWins']
        self.defenseWins = jjson['defenseWins']
        self.builderHallLevel = jjson ['builderHallLevel']
        self.versusTrophies = jjson['versusTrophies']
        self.bestVersusTrophies = jjson['bestVersusTrophies']
        self.versusBattleWins = jjson['versusBattleWins']
        self.role = jjson['role']
        self.donations = jjson['donations']
        self.donationsReceived = jjson['donationsReceived']
        self.versusBattleWinCount = jjson['versusBattleWinCount']

        #Clan Level
        self.clan_tag = jjson['clan']['tag']
        self.clan_name = jjson['clan']['tag']
        self.clan_Level = jjson['clan']['clanLevel']
        self.clan_badgeSmall = jjson['clan']['badgeUrls']['small']
        self.clan_badgeMed = jjson['clan']['badgeUrls']['medium']
        self.clan_badgeLarge = jjson['clan']['badgeUrls']['large']

        #League Level
        self.league_id = jjson['league']['id']
        self.league_name = jjson['league']['name']
        self.league_badgeTiny = jjson['league']['iconUrls']['tiny']
        self.league_badgeSmall = jjson['league']['iconUrls']['small']
        self.league_badgeMed = jjson['league']['iconUrls']['medium']

        #Achievements Level
        self.achieve = {
            "Bigger Coffers" :{},
            "Get those Goblins!" :{},
            "Bigger & Better" :{},
            "Nice and Tidy" :{},
            "Release the Beasts" :{},
            "Gold Grab" :{},
            "Elixir Escapade" :{},
            "Sweet Victory!" :{},
            "Empire Builder" :{},
            "Wall Buster" :{},
            "Humiliator" :{},
            "Union Buster" :{},
            "Conqueror" :{},
            "Unbreakable" :{},
            "Friend in Need" :{},
            "Mortar Mauler" :{},
            "Heroic Heist" :{},
            "League All-Star" :{},
            "X-Bow Exterminator" :{},
            "Firefighter" :{},
            "War Hero" :{},
            "Treasurer" :{},
            "Anti-Artillery" :{},
            "Sharing is caring" :{},
            "Keep your village safe" :{},
            "Master Engineering" :{},
            "Next Generation Model" :{},
            "Un-Build It" :{},
            "Champion Builder" :{},
            "High Gear" :{},
            "Hidden Treasures" :{},
            "Games Champion" :{},
            "Dragon Slayer" :{},
            "War League Legend" :{},
            "Keep your village safe" :{},
        }
        for i in jjson['achievements']:
            self.achieve[i['name']] = {
                "name"  :   i['name'],
                "stars" :   i['stars'],
                "value" :   i['value'],
                "target":   i['target'],
                "info"  :   i['info'],
                #"completionInfo": i['completionInfo'],
                "village": i['village']
            }
        # Troops level
        self.troops = {
            "Barbarian" :{},
            "Archer" :{},
            "Goblin" :{},
            "Giant" :{},
            "Wall Breaker" :{},
            "Balloon" :{},
            "Wizard" :{},
            "Healer" :{},
            "Dragon" :{},
            "P.E.K.K.A" :{},
            "Minion" :{},
            "Hog Rider" :{},
            "Valkyrie" :{},
            "Golem" :{},
            "Witch" :{},
            "Lava Hound" :{},
            "Bowler" :{},
            "Miner" :{},
            "Raged Barbarian" :{},
            "Sneaky Archer" :{},
            "Beta Minion" :{},
            "Boxer Giant" :{},
            "Bomber" :{},
            "Super P.E.K.K.A" :{},
            "Cannon Cart" :{},
            "Drop Ship" :{},
            "Baby Dragon" :{},
            "Night Witch" :{},
            "Wall Wrecker" :{},
            "Battle Blimp" :{},
            "Ice Golem" :{},
            "Electro Dragon" :{},
            "Stone Slammer" :{}
        }
        for i in jjson['troops']:
            self.troops[i['name']] = {
                "name" : i['name'],
                "level": i['level'],
                "maxLevel" : i['maxLevel'],
                "village" : i['village']
            }

        for troop in self.troops.keys():
            if not self.troops[troop]:
                self.troops[troop] = {
                    "name" : troop,
                    "level" : 0,
                    "maxLevel": 0
                }

        # Heroes Level
        self.heroes = {
            "Barbarian King" :{},
            "Archer Queen" :{},
            "Grand Warden" :{},
            "Battle Machine" :{}
        }
        for i in jjson['heroes']:
            self.heroes[i['name']] = {
                "name" : i['name'],
                "level" : i['level'],
                "maxLevel" : i['maxLevel'],
                "village" : i['village']
            }

        for hero in self.heroes.keys():
            if not self.heroes[hero]:
                self.heroes[hero] = {
                    "name" : hero,
                    "level" : 0,
                    "maxLevel": 0
                }

        # Spells level
        self.spells = {
            "Lightning Spell" :{},
            "Healing Spell" :{},
            "Rage Spell" :{},
            "Jump Spell" :{},
            "Freeze Spell" :{},
            "Poison Spell" :{},
            "Earthquake Spell" :{},
            "Haste Spell" :{},
            "Clone Spell" :{},
            "Skeleton Spell" :{},
            "Bat Spell" :{}
        }
        for i in jjson['spells']:
            self.spells[i['name']] = {
                "name" : i['name'],
                "level" : i['level'],
                "maxLevel" : i['maxLevel'],
                "village" : i['village']          
            }

        for spell in self.spells.keys():
            if not self.spells[spell]:
                self.spells[spell] = {
                    "name" : spell,
                    "level" : 0,
                    "maxLevel": 0
                }