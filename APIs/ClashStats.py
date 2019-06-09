from configparser import ConfigParser
import json

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
        try:
            self.role = jjson['role']
        except:
            self.role = "None"

        self.donations = jjson['donations']
        self.donationsReceived = jjson['donationsReceived']
        self.versusBattleWinCount = jjson['versusBattleWinCount']

        #Clan Level
        clan = False
        try:
            jjson['clan']
            clan = True
        except:
            self.clan_name = "None"
            self.clan_tag = "None"

        if clan:
            self.clan_tag = jjson['clan']['tag']
            self.clan_name = jjson['clan']['name']
            self.clan_Level = jjson['clan']['clanLevel']
            self.clan_badgeSmall = jjson['clan']['badgeUrls']['small']
            self.clan_badgeMed = jjson['clan']['badgeUrls']['medium']
            self.clan_badgeLarge = jjson['clan']['badgeUrls']['large']

        #League Level
        if 'league' in jjson.keys():
            self.league_id = jjson['league']['id']
            self.league_name = jjson['league']['name']
            self.league_badgeTiny = jjson['league']['iconUrls']['tiny']
            self.league_badgeSmall = jjson['league']['iconUrls']['small']
            self.league_badgeMed = jjson['league']['iconUrls']['medium']
        else:
            self.league_id = None
            self.league_name = None
            self.league_badgeTiny = None
            self.league_badgeSmall= None
            self.league_badgeMed = None

        #Achievements Levl
        self.achieve ={
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
            # "Keep your village safe" :{},
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

def stat_stitcher(player, emot_loc):
    """Sitcher is used for MAX troops"""

    # Load troop levels
    with open("clash_troop_levels.json", "r") as trooplevels:
        print(trooplevels)
        troops = json.load(trooplevels)
        print(troops)
    print(troops)
    
    for troop in troops["12"]:
        print(troop)
    plvl = str(player.town_hall)
    emoticons.read(emot_loc)
    desc = (f"**{player.role}**\n{player.tag}\n{emoticons['townhalls'][str(player.town_hall)]}")
    # gain stitcher
    gains = (f"**Current Clan:** {str(player.clan):>20}\n")
    gains += (f"**Current Trophy:** {str(player.trophies):>20}\n")
    gains += (f"**Best Trophy:** {str(player.best_trophies):>26}\n")
    gains += (f"**War Stars:** {str(player.war_stars):>32}\n")
    gains += (f"**Attack Wins:** {str(player.attack_wins):>28}\n")
    gains += (f"**Defense Wins:** {str(player.defense_wins):>27}\n")

    # Troop stitcher        
    troopLevels  = (f"{emoticons['troops']['barbarian']} {str(player.home_troops_dict['Barbarian'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['archer']} {str(player.home_troops_dict['Archer'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['goblin']} {str(player.home_troops_dict['Goblin'].level):<2}|{str(7):<2}\n")
    troopLevels += (f"{emoticons['troops']['giant']} {str(player.home_troops_dict['Giant'].level):<2}|{str(9):<2}")
    troopLevels += (f"{emoticons['troops']['wallbreaker']} {str(player.home_troops_dict['Wall Breaker'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['loon']} {str(player.home_troops_dict['Balloon'].level):<2}|{str(8):<2}\n")
    troopLevels += (f"{emoticons['troops']['Wizard']} {str(player.home_troops_dict['Wizard'].level):<2}|{str(9):<2}")
    troopLevels += (f"{emoticons['troops']['Healer']} {str(player.home_troops_dict['Healer'].level):<2}|{str(5):<2}")
    troopLevels += (f"{emoticons['troops']['drag']} {str(player.home_troops_dict['Dragon'].level):<2}|{str(7):<2}\n")
    troopLevels += (f"{emoticons['troops']['pekka']} {str(player.home_troops_dict['P.E.K.K.A'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['minion']} {str(player.home_troops_dict['Minion'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['hogrider']} {str(player.home_troops_dict['Hog Rider'].level):<2}|{str(8):<2}\n")
    troopLevels += (f"{emoticons['troops']['valkyrie']} {str(player.home_troops_dict['Valkyrie'].level):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['golem']} {str(player.home_troops_dict['Golem'].level):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['witch']} {str(player.home_troops_dict['Witch'].level):<2}|{str(5):<2}\n")
    troopLevels += (f"{emoticons['troops']['lavahound']} {str(player.home_troops_dict['Lava Hound'].level):<2}|{str(5):<2}")
    troopLevels += (f"{emoticons['troops']['bowler']} {str(player.home_troops_dict['Bowler'].level):<2}|{str(4):<2}")
    troopLevels += (f"{emoticons['troops']['miner']} {str(player.home_troops_dict['Miner'].level):<2}|{str(6):<2}\n")
    troopLevels += (f"{emoticons['troops']['babydragon']} {str(player.home_troops_dict['Baby Dragon'].level):<2}|{str(6):<2}")
    troopLevels += (f"{emoticons['troops']['icegolem']} {str(player.home_troops_dict['Ice Golem'].level):<2}|{str(5):<2}")
    troopLevels += (f"{emoticons['troops']['edrag']} {str(player.home_troops_dict['Electro Dragon'].level):<2}|{str(3):<2}\n")
    # Spell stitcher
    spellLevels = (f"{emoticons['spells']['lightning']} {str(player.spells_dict['Lightning Spell'].level):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['heal']} {str(player.spells_dict['Healing Spell'].level):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['rage']} {str(player.spells_dict['Rage Spell'].level):<2}|{str(5):<2}\n")
    spellLevels += (f"{emoticons['spells']['jump']} {str(player.spells_dict['Jump Spell'].level):<2}|{str(3):<2}")
    spellLevels += (f"{emoticons['spells']['freeze']} {str(player.spells_dict['Freeze Spell'].level):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['poison']} {str(player.spells_dict['Poison Spell'].level):<2}|{str(5):<2}\n")
    spellLevels += (f"{emoticons['spells']['earthquake']} {str(player.spells_dict['Earthquake Spell'].level):<2}|{str(4):<2}")
    spellLevels += (f"{emoticons['spells']['haste']} {str(player.spells_dict['Haste Spell'].level):<2}|{str(4):<2}")
    spellLevels += (f"{emoticons['spells']['clone']} {str(player.spells_dict['Clone Spell'].level):<2}|{str(5):<2}\n")
    spellLevels += (f"{emoticons['spells']['skeleton']} {str(player.spells_dict['Skeleton Spell'].level):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['batspell']} {str(player.spells_dict['Bat Spell'].level):<2}|{str(5)}\n")
    # Hero stitcher
    heroLevels = (f"{emoticons['heroes']['barbking']} {str(player.heroes_dict['Barbarian King'].level):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['archerqueen']} {str(player.heroes_dict['Archer Queen'].level):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['grandwarden']} {str(player.heroes_dict['Grand Warden'].level):<2}|{str(30):<2}")
    return desc, troopLevels, spellLevels, heroLevels, gains