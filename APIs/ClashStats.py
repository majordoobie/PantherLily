from configparser import ConfigParser
emoticons = ConfigParser(allow_no_value=True)

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
            "Baby Dragon2" :{},
            "Night Witch" :{},
            "Wall Wrecker" :{},
            "Battle Blimp" :{},
            "Ice Golem" :{},
            "Electro Dragon" :{},
            "Stone Slammer" :{}
        }
        for i in jjson['troops']:
            if i['name'] == "Baby Dragon":
                if i['village'] == "home":
                    self.troops['Baby Dragon'] = {
                        "name" : i['name'],
                        "level": i['level'],
                        "maxLevel" : i['maxLevel'],
                        "village" : i['village']
                    }
                else:
                    self.troops['Baby Dragon2'] = {
                        "name" : i['name'],
                        "level": i['level'],
                        "maxLevel" : i['maxLevel'],
                        "village" : i['village']
                    }
            else:
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

def statStitcher(memStat, emotLoc):
    emoticons.read(emotLoc)
    desc = (f"{memStat.tag}\n{emoticons['townhalls'][str(memStat.townHallLevel)]}")

    troopLevels = (f"{emoticons['troops']['barbarian']} {str(memStat.troops['Barbarian']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['archer']} {str(memStat.troops['Archer']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['goblin']} {str(memStat.troops['Goblin']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['giant']} {str(memStat.troops['Giant']['level']):<2}|{str(9):<2}\n")
    troopLevels += (f"{emoticons['troops']['wallbreaker']} {str(memStat.troops['Wall Breaker']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['loon']} {str(memStat.troops['Balloon']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['Wizard']} {str(memStat.troops['Wizard']['level']):<2}|{str(9):<2}")
    troopLevels += (f"{emoticons['troops']['Healer']} {str(memStat.troops['Healer']['level']):<2}|{str(5):<2}\n")
    troopLevels += (f"{emoticons['troops']['drag']} {str(memStat.troops['Dragon']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['pekka']} {str(memStat.troops['P.E.K.K.A']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['minion']} {str(memStat.troops['Minion']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['hogrider']} {str(memStat.troops['Hog Rider']['level']):<2}|{str(8):<2}\n")
    troopLevels += (f"{emoticons['troops']['valkyrie']} {str(memStat.troops['Valkyrie']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['golem']} {str(memStat.troops['Golem']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['witch']} {str(memStat.troops['Witch']['level']):<2}|{str(4):<2}")
    troopLevels += (f"{emoticons['troops']['lavahound']} {str(memStat.troops['Lava Hound']['level']):<2}|{str(5):<2}\n")
    troopLevels += (f"{emoticons['troops']['bowler']} {str(memStat.troops['Bowler']['level']):<2}|{str(4):<2}")
    troopLevels += (f"{emoticons['troops']['miner']} {str(memStat.troops['Miner']['level']):<2}|{str(6):<2}")
    troopLevels += (f"{emoticons['troops']['babydragon']} {str(memStat.troops['Baby Dragon']['level']):<2}|{str(6):<2}")
    troopLevels += (f"{emoticons['troops']['icegolem']} {str(memStat.troops['Ice Golem']['level']):<2}|{str(4):<2}")
    troopLevels += (f"{emoticons['troops']['edrag']} {str(memStat.troops['Electro Dragon']['level']):<2}|{str(3):<2}")
    
    spellLevels = (f"{emoticons['spells']['lightning']} {str(memStat.spells['Lightning Spell']['level']):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['heal']} {str(memStat.spells['Healing Spell']['level']):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['rage']} {str(memStat.spells['Rage Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['jump']} {str(memStat.spells['Jump Spell']['level']):<2}|{str(3):<2}\n")
    spellLevels += (f"{emoticons['spells']['freeze']} {str(memStat.spells['Freeze Spell']['level']):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['poison']} {str(memStat.spells['Poison Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['earthquake']} {str(memStat.spells['Earthquake Spell']['level']):<2}|{str(4):<2}")
    spellLevels += (f"{emoticons['spells']['haste']} {str(memStat.spells['Haste Spell']['level']):<2}|{str(4):<2}\n")
    spellLevels += (f"{emoticons['spells']['clone']} {str(memStat.spells['Clone Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['skeleton']} {str(memStat.spells['Skeleton Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['batspell']} {str(memStat.spells['Bat Spell']['level']):<2}|{str(5)}")

    heroLevels = (f"{emoticons['heroes']['barbking']} {str(memStat.heroes['Barbarian King']['level']):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['archerqueen']} {str(memStat.heroes['Archer Queen']['level']):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['grandwarden']} {str(memStat.heroes['Grand Warden']['level']):<2}|{str(30):<2}")
    return desc, troopLevels, spellLevels, heroLevels