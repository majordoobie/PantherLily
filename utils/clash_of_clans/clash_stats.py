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

def stat_stitcher(player, emot_loc, _max):
    """Sitcher is used for MAX troops"""

    # Load troop levels
    with open("ClashOfClans/clash_troop_levels.json", "r") as trooplevels:
        troop = json.load(trooplevels)

    # Players townhall level
    if _max == True:
        plvl = str(12)
    else:
        plvl = str(player.town_hall)

    emoticons.read(emot_loc)
    desc = (f"**{player.role}**\n{player.tag}\n{emoticons['townhalls'][str(player.town_hall)]}")
    
    # gain stitcher
    gains = (f"**Current Clan:**\n{str(player.clan)}\n")
    gains += (f"**Current Trophy:**\n{str(player.trophies)}\n")
    gains += (f"**Best Trophy:**\n{str(player.best_trophies)}\n")
    gains += (f"**War Stars:**\n{str(player.war_stars)}\n")
    gains += (f"**Attack Wins:**\n{str(player.attack_wins)}\n")
    gains += (f"**Defense Wins:**\n{str(player.defense_wins)}\n")

    # Troop stitcher
    if player.home_troops_dict['Barbarian'].level == int(troop[plvl]['Barbarian']):
        troop_levels = (f"{emoticons['troops']['barbarian']} **{str(player.home_troops_dict['Barbarian'].level):<2}| {str(troop[plvl]['Barbarian']):<2}**")
    else:
        troop_levels = (f"{emoticons['troops']['barbarian']} {str(player.home_troops_dict['Barbarian'].level):<2}| {str(troop[plvl]['Barbarian']):<2}")

    if player.home_troops_dict['Archer'].level == int(troop[plvl]['Archer']):
        troop_levels += (f"{emoticons['troops']['archer']} **{str(player.home_troops_dict['Archer'].level):<2}| {str(troop[plvl]['Archer']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['archer']} {str(player.home_troops_dict['Archer'].level):<2}| {str(troop[plvl]['Archer']):<2}")
    
    if player.home_troops_dict['Goblin'].level == int(troop[plvl]['Goblin']):
        troop_levels += (f"{emoticons['troops']['goblin']} **{str(player.home_troops_dict['Goblin'].level):<2}| {str(troop[plvl]['Goblin']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['goblin']} {str(player.home_troops_dict['Goblin'].level):<2}| {str(troop[plvl]['Goblin']):<2}\n")

    if player.home_troops_dict['Giant'].level == int(troop[plvl]['Giant']):
        troop_levels += (f"{emoticons['troops']['giant']} **{str(player.home_troops_dict['Giant'].level):<2}| {str(troop[plvl]['Giant']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['giant']} {str(player.home_troops_dict['Giant'].level):<2}| {str(troop[plvl]['Giant']):<2}")

    if player.home_troops_dict['Wall Breaker'].level == int(troop[plvl]['Wall Breaker']):
        troop_levels += (f"{emoticons['troops']['wallbreaker']} **{str(player.home_troops_dict['Wall Breaker'].level):<2}| {str(troop[plvl]['Wall Breaker']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['wallbreaker']} {str(player.home_troops_dict['Wall Breaker'].level):<2}| {str(troop[plvl]['Wall Breaker']):<2}")

    if player.home_troops_dict['Balloon'].level == int(troop[plvl]['Balloon']):
        troop_levels += (f"{emoticons['troops']['loon']} **{str(player.home_troops_dict['Balloon'].level):<2}| {str(troop[plvl]['Balloon']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['loon']} {str(player.home_troops_dict['Balloon'].level):<2}| {str(troop[plvl]['Balloon']):<2}\n")

    if player.home_troops_dict['Wizard'].level == int(troop[plvl]['Wizard']):
        troop_levels += (f"{emoticons['troops']['Wizard']} **{str(player.home_troops_dict['Wizard'].level):<2}| {str(troop[plvl]['Wizard']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['Wizard']} {str(player.home_troops_dict['Wizard'].level):<2}| {str(troop[plvl]['Wizard']):<2}")

    if player.home_troops_dict['Healer'].level == int(troop[plvl]['Healer']):
        troop_levels += (f"{emoticons['troops']['Healer']} **{str(player.home_troops_dict['Healer'].level):<2}| {str(troop[plvl]['Healer']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['Healer']} {str(player.home_troops_dict['Healer'].level):<2}| {str(troop[plvl]['Healer']):<2}")

    if player.home_troops_dict['Dragon'].level == int(troop[plvl]['Dragon']):
        troop_levels += (f"{emoticons['troops']['drag']} **{str(player.home_troops_dict['Dragon'].level):<2}| {str(troop[plvl]['Dragon']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['drag']} {str(player.home_troops_dict['Dragon'].level):<2}| {str(troop[plvl]['Dragon']):<2}\n")

    if player.home_troops_dict['P.E.K.K.A'].level == int(troop[plvl]['P.E.K.K.A']):
        troop_levels += (f"{emoticons['troops']['pekka']} **{str(player.home_troops_dict['P.E.K.K.A'].level):<2}| {str(troop[plvl]['P.E.K.K.A']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['pekka']} {str(player.home_troops_dict['P.E.K.K.A'].level):<2}| {str(troop[plvl]['P.E.K.K.A']):<2}")

    if player.home_troops_dict['Minion'].level == int(troop[plvl]['Minion']):
        troop_levels += (f"{emoticons['troops']['minion']} **{str(player.home_troops_dict['Minion'].level):<2}| {str(troop[plvl]['Minion']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['minion']} {str(player.home_troops_dict['Minion'].level):<2}| {str(troop[plvl]['Minion']):<2}")

    if player.home_troops_dict['Hog Rider'].level == int(troop[plvl]['Hog Rider']):
        troop_levels += (f"{emoticons['troops']['hogrider']} **{str(player.home_troops_dict['Hog Rider'].level):<2}| {str(troop[plvl]['Hog Rider']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['hogrider']} {str(player.home_troops_dict['Hog Rider'].level):<2}| {str(troop[plvl]['Hog Rider']):<2}\n")

    if player.home_troops_dict['Valkyrie'].level == int(troop[plvl]['Valkyrie']):
        troop_levels += (f"{emoticons['troops']['valkyrie']} **{str(player.home_troops_dict['Valkyrie'].level):<2}| {str(troop[plvl]['Valkyrie']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['valkyrie']} {str(player.home_troops_dict['Valkyrie'].level):<2}| {str(troop[plvl]['Valkyrie']):<2}")

    if player.home_troops_dict['Golem'].level == int(troop[plvl]['Golem']):
        troop_levels += (f"{emoticons['troops']['golem']} **{str(player.home_troops_dict['Golem'].level):<2}| {str(troop[plvl]['Golem']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['golem']} {str(player.home_troops_dict['Golem'].level):<2}| {str(troop[plvl]['Golem']):<2}")

    if player.home_troops_dict['Witch'].level == int(troop[plvl]['Witch']):
        troop_levels += (f"{emoticons['troops']['witch']} **{str(player.home_troops_dict['Witch'].level):<2}| {str(troop[plvl]['Witch']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['witch']} {str(player.home_troops_dict['Witch'].level):<2}| {str(troop[plvl]['Witch']):<2}\n")

    if player.home_troops_dict['Lava Hound'].level == int(troop[plvl]['Lava Hound']):
        troop_levels += (f"{emoticons['troops']['lavahound']} **{str(player.home_troops_dict['Lava Hound'].level):<2}| {str(troop[plvl]['Lava Hound']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['lavahound']} {str(player.home_troops_dict['Lava Hound'].level):<2}| {str(troop[plvl]['Lava Hound']):<2}")

    if player.home_troops_dict['Bowler'].level == int(troop[plvl]['Bowler']):
        troop_levels += (f"{emoticons['troops']['bowler']} **{str(player.home_troops_dict['Bowler'].level):<2}| {str(troop[plvl]['Bowler']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['bowler']} {str(player.home_troops_dict['Bowler'].level):<2}| {str(troop[plvl]['Bowler']):<2}")

    if player.home_troops_dict['Miner'].level == int(troop[plvl]['Miner']):
        troop_levels += (f"{emoticons['troops']['miner']} **{str(player.home_troops_dict['Miner'].level):<2}| {str(troop[plvl]['Miner']):<2}\n**")
    else:
        troop_levels += (f"{emoticons['troops']['miner']} {str(player.home_troops_dict['Miner'].level):<2}| {str(troop[plvl]['Miner']):<2}\n")

    if player.home_troops_dict['Baby Dragon'].level == int(troop[plvl]['Baby Dragon']):
        troop_levels += (f"{emoticons['troops']['babydragon']} **{str(player.home_troops_dict['Baby Dragon'].level):<2}| {str(troop[plvl]['Baby Dragon']):<2}**")
    else:
        troop_levels += (f"{emoticons['troops']['babydragon']} {str(player.home_troops_dict['Baby Dragon'].level):<2}| {str(troop[plvl]['Baby Dragon']):<2}")

    try:
        if player.home_troops_dict['Ice Golem'].level == int(troop[plvl]['Ice Golem']):
            troop_levels += (f"{emoticons['troops']['icegolem']} **{str(player.home_troops_dict['Ice Golem'].level):<2}| {str(troop[plvl]['Ice Golem']):<2}**")
        else:
            troop_levels += (f"{emoticons['troops']['icegolem']} {str(player.home_troops_dict['Ice Golem'].level):<2}| {str(troop[plvl]['Ice Golem']):<2}")
    except:
        troop_levels += (f"{emoticons['troops']['icegolem']} 0 | 0")

    try:
        if player.home_troops_dict['Electro Dragon'].level == int(troop[plvl]['Electro Dragon']):
            troop_levels += (f"{emoticons['troops']['edrag']} **{str(player.home_troops_dict['Electro Dragon'].level):<2}| {str(troop[plvl]['Electro Dragon']):<2}\n**")
        else:
            troop_levels += (f"{emoticons['troops']['edrag']} {str(player.home_troops_dict['Electro Dragon'].level):<2}| {str(troop[plvl]['Electro Dragon']):<2}\n")
    except:
        troop_levels += (f"{emoticons['troops']['edrag']} 0 | 0\n")

    # Spell stitcher
    if player.spells_dict['Lightning Spell'].level == int(troop[plvl]['Lightning Spell']):
        spell_levels = (f"{emoticons['spells']['lightning']} **{str(player.spells_dict['Lightning Spell'].level):<2}| {str(troop[plvl]['Lightning Spell']):<2}**")
    else:
        spell_levels = (f"{emoticons['spells']['lightning']} {str(player.spells_dict['Lightning Spell'].level):<2}| {str(troop[plvl]['Lightning Spell']):<2}")

    if player.spells_dict['Healing Spell'].level == int(troop[plvl]['Healing Spell']):
        spell_levels += (f"{emoticons['spells']['heal']} **{str(player.spells_dict['Healing Spell'].level):<2}| {str(troop[plvl]['Healing Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['heal']} {str(player.spells_dict['Healing Spell'].level):<2}| {str(troop[plvl]['Healing Spell']):<2}")

    if player.spells_dict['Rage Spell'].level == int(troop[plvl]['Rage Spell']):
        spell_levels += (f"{emoticons['spells']['rage']} **{str(player.spells_dict['Rage Spell'].level):<2}| {str(troop[plvl]['Rage Spell']):<2}\n**")
    else:
        spell_levels += (f"{emoticons['spells']['rage']} {str(player.spells_dict['Rage Spell'].level):<2}| {str(troop[plvl]['Rage Spell']):<2}\n")

    if player.spells_dict['Jump Spell'].level == int(troop[plvl]['Jump Spell']):
        spell_levels += (f"{emoticons['spells']['jump']} **{str(player.spells_dict['Jump Spell'].level):<2}| {str(troop[plvl]['Jump Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['jump']} {str(player.spells_dict['Jump Spell'].level):<2}| {str(troop[plvl]['Jump Spell']):<2}")

    if player.spells_dict['Freeze Spell'].level == int(troop[plvl]['Freeze Spell']):
        spell_levels += (f"{emoticons['spells']['freeze']} **{str(player.spells_dict['Freeze Spell'].level):<2}| {str(troop[plvl]['Freeze Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['freeze']} {str(player.spells_dict['Freeze Spell'].level):<2}| {str(troop[plvl]['Freeze Spell']):<2}")

    if player.spells_dict['Poison Spell'].level == int(troop[plvl]['Poison Spell']):
        spell_levels += (f"{emoticons['spells']['poison']} **{str(player.spells_dict['Poison Spell'].level):<2}| {str(troop[plvl]['Poison Spell']):<2}\n**")
    else:
        spell_levels += (f"{emoticons['spells']['poison']} {str(player.spells_dict['Poison Spell'].level):<2}| {str(troop[plvl]['Poison Spell']):<2}\n")

    if player.spells_dict['Earthquake Spell'].level == int(troop[plvl]['Earthquake Spell']):
        spell_levels += (f"{emoticons['spells']['earthquake']} **{str(player.spells_dict['Earthquake Spell'].level):<2}| {str(troop[plvl]['Earthquake Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['earthquake']} {str(player.spells_dict['Earthquake Spell'].level):<2}| {str(troop[plvl]['Earthquake Spell']):<2}")

    if player.spells_dict['Haste Spell'].level == int(troop[plvl]['Haste Spell']):
        spell_levels += (f"{emoticons['spells']['haste']} **{str(player.spells_dict['Haste Spell'].level):<2}| {str(troop[plvl]['Haste Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['haste']} {str(player.spells_dict['Haste Spell'].level):<2}| {str(troop[plvl]['Haste Spell']):<2}")

    if player.spells_dict['Clone Spell'].level == int(troop[plvl]['Clone Spell']):
        spell_levels += (f"{emoticons['spells']['clone']} **{str(player.spells_dict['Clone Spell'].level):<2}| {str(troop[plvl]['Clone Spell']):<2}\n**")
    else:
        spell_levels += (f"{emoticons['spells']['clone']} {str(player.spells_dict['Clone Spell'].level):<2}| {str(troop[plvl]['Clone Spell']):<2}\n")

    if player.spells_dict['Skeleton Spell'].level == int(troop[plvl]['Skeleton Spell']):
        spell_levels += (f"{emoticons['spells']['skeleton']} **{str(player.spells_dict['Skeleton Spell'].level):<2}| {str(troop[plvl]['Skeleton Spell']):<2}**")
    else:
        spell_levels += (f"{emoticons['spells']['skeleton']} {str(player.spells_dict['Skeleton Spell'].level):<2}| {str(troop[plvl]['Skeleton Spell']):<2}")

    if player.spells_dict['Bat Spell'].level == int(troop[plvl]['Bat Spell']):
        spell_levels += (f"{emoticons['spells']['batspell']} **{str(player.spells_dict['Bat Spell'].level):<2}| {str(troop[plvl]['Bat Spell']):<2}\n**")
    else:
        spell_levels += (f"{emoticons['spells']['batspell']} {str(player.spells_dict['Bat Spell'].level):<2}| {str(troop[plvl]['Bat Spell'])}\n")

    # Hero stitcher
    if player.heroes_dict['Barbarian King'].level == int(troop[plvl]['Barbarian King']):
        heroLevels = (f"{emoticons['heroes']['barbking']} **{str(player.heroes_dict['Barbarian King'].level):<2} | {str(troop[plvl]['Barbarian King']):<2}**")
    else:
        heroLevels = (f"{emoticons['heroes']['barbking']} {str(player.heroes_dict['Barbarian King'].level):<2} | {str(troop[plvl]['Barbarian King']):<2}")

    if player.heroes_dict['Archer Queen'].level == int(troop[plvl]['Archer Queen']):
        heroLevels += (f"{emoticons['heroes']['archerqueen']} **{str(player.heroes_dict['Archer Queen'].level):<2} | {str(troop[plvl]['Archer Queen']):<2}**")
    else:
        heroLevels += (f"{emoticons['heroes']['archerqueen']} {str(player.heroes_dict['Archer Queen'].level):<2} | {str(troop[plvl]['Archer Queen']):<2}")

    try:
        if player.heroes_dict['Grand Warden'].level == int(troop[plvl]['Grand Warden']):
            heroLevels += (f"{emoticons['heroes']['grandwarden']} **{str(player.heroes_dict['Grand Warden'].level):<2} | {str(troop[plvl]['Grand Warden']):<2}**")
        else:
            heroLevels += (f"{emoticons['heroes']['grandwarden']} {str(player.heroes_dict['Grand Warden'].level):<2} | {str(troop[plvl]['Grand Warden']):<2}")
    except:
        heroLevels += (f"{emoticons['heroes']['grandwarden']} 0 | 0")

    siege_flag = False
    try:
        if player.home_troops_dict['Wall Wrecker'].level == int(troop[plvl]["Wall Wrecker"]):
            siege_levels = (f"{emoticons['siege']['smground']} **{str(player.home_troops_dict['Wall Wrecker'].level):<2} | {str(troop[plvl]['Wall Wrecker']):<2}**")
        else:
            siege_levels = (f"{emoticons['siege']['smground']} {str(player.home_troops_dict['Wall Wrecker'].level):<2} | {str(troop[plvl]['Wall Wrecker']):<2}")
        siege_flag = True
    except:
        siege_levels = None

    if siege_flag:
        try:
            if player.home_troops_dict['Battle Blimp'].level == int(troop[plvl]["Battle Blimp"]):
                siege_levels += (f"{emoticons['siege']['smair1']} **{str(player.home_troops_dict['Battle Blimp'].level):<2} | {str(troop[plvl]['Battle Blimp']):<2}**")
            else:
                siege_levels += (f"{emoticons['siege']['smair1']} {str(player.home_troops_dict['Battle Blimp'].level):<2} | {str(troop[plvl]['Battle Blimp']):<2}")
        except:
            siege_levels += (f"{emoticons['siege']['smair1']} 0 | 0")

        try:
            if player.home_troops_dict['Stone Slammer'].level == int(troop[plvl]["Stone Slammer"]):
                siege_levels += (f"{emoticons['siege']['smair2']} **{str(player.home_troops_dict['Stone Slammer'].level):<2} | {str(troop[plvl]['Stone Slammer']):<2}**")
            else:
                siege_levels += (f"{emoticons['siege']['smair2']} {str(player.home_troops_dict['Stone Slammer'].level):<2} | {str(troop[plvl]['Stone Slammer']):<2}")
        except:
            siege_levels += (f"{emoticons['siege']['smair2']} 0 | 0")


    return desc, troop_levels, spell_levels, heroLevels, gains, siege_levels