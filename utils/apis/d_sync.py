from datetime import datetime
import logging
import random
import traceback
import discord
import asyncio
import coc.errors as coc_error
from pathlib import Path

# Log path
LOG_PATH = Path(__file__).joinpath(*Path(__file__).resolve().parts[:-3])

# set up global logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
HDNL = logging.FileHandler(filename=LOG_PATH/'weekly.log', encoding='utf-8', mode='w')
HDNL.setFormatter(logging.Formatter('[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Fun'
                                    'c:%(funcName)s]\n[Path:%(pathname)s]\n MSG: %(message)s\n',
                                    "%d %b %H:%M:%S"))
log.addHandler(HDNL)

class UpdateLoop():
    """Looping function to update users information and tables"""
    def __init__(self, d_client, dbconn, bot_mode, coc_client2, config):
        self.d_client = d_client
        self.dbconn = dbconn
        self.bot_mode = bot_mode
        self.coc_client2 = coc_client2
        self.config = config
        self.set_guild()

    def set_guild(self):
        """ Method used to get the guild object"""
        _id = int(self.config["discord"]["zuludisc_id"])
        self.guild = self.d_client.get_guild(_id)     
        

    async def run(self):
        """Looping function to update users information and tables"""
        guild = 503660106110730256
        channel = 606278536457748481
        g = self.d_client.get_guild(guild)
        c = g.get_channel(channel)
        if self.bot_mode == "devBot":
            print("Running in dev mode, disabling database update.")
            return

        await self.d_client.wait_until_ready()
        while not self.d_client.is_closed():
            succ = False
            while succ == False:
                try:
                    await self.coc_client2.get_player("#9P9PRYQJ", cache=False)
                    succ = True
                except Exception as e:
                    log.info(e)
                    await c.send(f"{e}\nWaiting five minutes before trying again.")
                    await asyncio.sleep(300)

            # Sleep for the amount needed
            sleep = self.sleep_time()
            log.info(f"Looping starts in {sleep} minutes")
            await c.send(f'`{f"Looping starts in {sleep} minutes"}`')
            await asyncio.sleep(sleep * 60)
            log.info("Starting d_sync")
            await c.send(f'`{f"Starting d_sync"}`')
            # Change presense
            log.info("Change presense to busy")
            await self.change_presence("busy")

            # Get all users in the database
            all_active = self.dbconn.get_all_active()

            # Update all donations
            ret, err = await update_donationstable(self.dbconn, self.coc_client2)
            if ret == "Failed":
                log.error(err)

            # Get zbp guild member list 
            plan_mem = self.d_client.get_guild(int(self.config['discord']['plandisc_id'])).members
            if plan_mem is None:
                log.error("Could not get plan_memners")
                await c.send(f'`{"Could not get plan_memners"}`')
            else:
                # Iterate over all active users 
                for user in all_active:
                    # get users coc object
                    try:
                        player = await self.coc_client2.get_player(user[0], cache=False)
                    except coc_error.NotFound as exception:
                        log.error(f"{exception} from {user[0]} {user[1]}")
                        await c.send(f'`{exception} from {user[0]} {user[1]}`')
                        continue

                    # get discord user object
                    try:
                        d_user = self.guild.get_member(int(user[4])) # Returns none if not there
                    except:
                        log.error(f"Could not retrieve the users discord member object for {player.name}")
                        await c.send(f'`{f"Could not retrieve the users discord member object for {player.name}"}`')
                        continue

                    if d_user == None:
                        continue

                    # Check if user is in zbp and update their table accordingly
                    in_zbp = "False"
                    if int(user[4]) in (mem.id for mem in plan_mem):
                        in_zbp = "True"

                    # Get roles and apply them
                    role_list, apply = self.get_updated_roles(player, d_user)
                    if apply:
                        try:
                            await d_user.edit(roles=role_list)
                            roles = [i.name for i in role_list]
                            log.info(f"Applying roles to {user[1]}\n{roles}")
                            await c.send(f'`{f"Applying roles to {user[1]} [{roles}]"}`')
                        except:
                            log.error(f"Could not apply roles to {user[1]}")
                            await c.send(f'`{f"Could not apply roles to {user[1]}"}`')
                            pass

                    # Update users discord name
                    if d_user.display_name != player.name:
                        try:
                            await self.change_name(d_user, player.name)
                            log.info(f"Changing {player.name} discord name from {d_user.display_name} to {player.name}")
                            await c.send(f'`{f"Changing {player.name} discord name from {d_user.display_name} to {player.name}"}`')
                        except:
                            log.error(f"Could not change {player.name} discord name")
                            await c.send(f'`{f"Could not change {player.name} discord name"}`')
                            pass

                    # Update the datehttps://github.com/majordoobie/dragontoolkitbase 
                    league = None
                    if player.league:
                        league = player.league.name
                    try:
                        self.dbconn.update_members_table((player.town_hall,
                                                        league,
                                                        in_zbp,
                                                        player.tag
                                                        ))
                    except:
                        log.error(f"Could not write to database for {player.name}")
                        await c.send(f'`{f"Could not write to database for {player.name}"}`')

            # Change precsne when done
            try:
                await self.change_presence(None)
            except:
                log.error(traceback.print_exc())
                await c.send(f'`{traceback.print_exc()}`')

    def get_updated_roles(self, player, d_user):
        """Method used to check if a members TH role needs to be updated"""
        player_th_role = self.get_th(player.town_hall)
        players_roles = d_user.roles

        # Set th role counter
        count = 0
        for role in players_roles:
            if role.name.startswith("th"):
                count += 1

        if count == 0:
            players_roles.append(player_th_role)
            return players_roles, True

        elif count == 1:
            if player_th_role in players_roles:
                return None, False
            else:
                new_roles = []
                for role in players_roles:
                    if role.name.startswith("th"):
                        continue
                    elif role.name.startswith("@"):
                        continue
                    else:
                        new_roles.append(role)
                new_roles.append(player_th_role)
                return new_roles, True
        else:
            new_roles = []
            for role in players_roles:
                if role.name.startswith("th"):
                    continue
                elif role.name.startswith("@"):
                    continue
                else:
                    new_roles.append(role)
            new_roles.append(player_th_role)
            return new_roles, True

    def sleep_time(self):
        """Simple fuction to get the time needed to hit the 15th minute hour"""
        wait_time = 60 - datetime.utcnow().minute
        if wait_time <= 15:
            pass
        elif wait_time <= 30:
            wait_time = wait_time - 15
        elif wait_time <= 45:
            wait_time = wait_time - 30
        else:
            wait_time = wait_time - 45
        return wait_time

    async def change_presence(self, mode):
        """Function to change the mode of presense"""
        if mode == "busy":
            log.info("Changing presense to busy")
            game = discord.Game("Updating Donations")
            try:
                await self.d_client.change_presence(status=discord.Status.dnd, activity=game)
            except:
                log.error(log.error(traceback.print_exc()))
                log.error("Could not change precense")

        else:
            messages = [
                (discord.ActivityType.playing ,   "Spotify"),
                (discord.ActivityType.playing   ,   "Overwatch"),
                (discord.ActivityType.playing   ,   "Clash of Clans"),
                (discord.ActivityType.playing   ,   "with cat nip~"),
                (discord.ActivityType.watching ,   "Fairy Tail"),
                (discord.ActivityType.playing   ,   "I'm not a cat!"),
                (discord.ActivityType.watching  ,   "panther.help"),
                (discord.ActivityType.watching , "Dragon Ball Z"),
                (discord.ActivityType.playing , "Reddit Zulu is #1")
            ]
            log.info("Chaning presense to random")
            activ = random.choice(messages)
            activity = discord.Activity(type=activ[0], name=activ[1])
            try:
                log.info("Trying to change presence back to normal")
                await self.d_client.change_presence(status=discord.Status.online, activity=activity)
            except:
                log.error(traceback.print_exc())

    def get_role(self, role_str):
        """Simple method to get rule objects"""
        for role in self.guild.roles:
            if role.name == role_str:
                return role
        return None

    def get_th(self, thlvl):
        """Retrieves the proper role for the given TH value"""
        levels = [9, 10, 11, 12, 13]
        str_roles = ['th9s', 'th10s', 'th11s', 'th12s', 'th13s']
        for level, str_role in zip(levels, str_roles):
            if thlvl == level:
                return self.get_role(str_role)
        return None

    async def change_name(self, disc_user, name):
        """Changes the users name"""
        await disc_user.edit(nick=name)
        return

async def update_donationstable(dbcon, coc_api):
    """Function used to retrive all active players to feed to commit_database

     Keyword arguments:
     ctx -- Discord context
     db -- Database handle
     coc_api -- coc.py client

     Return:
     No returns"""
    active_members = [tag[0] for tag in dbcon.get_all_active()]
    try:
        async for player in coc_api.get_players(active_members):
            commit_database(player, dbcon)
        return "Success", "Success"
    except Exception as e:
        return "Failed", e

async def update_user(dbcon, coc_api, user_tag):
    """Function used to retrive a single player to feed to commit_database

     Keyword arguments:
     ctx -- Discord context
     db -- Database handle
     coc_api -- coc.py client
     user_tag -- Tag of member you want to update

     Return:
     No returns"""
    player = await coc_api.get_player(user_tag)
    commit_database(player, dbcon)

def commit_database(player, dbcon):
    """Function used to update donations table with upto date data using coc.py

     Keyword arguments:
     player -- coc.py SearchPlayer object
     dbcon -- Database handle

     Return:
     No returns"""
    in_zulu = "False"
    try:
        if player.clan.name == "Reddit Zulu":
            in_zulu = "True"
    except:
        in_zulu = "False"

    try:
        dbcon.update_donations((
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            player.tag,
            player.achievements_dict["Friend in Need"].value,
            in_zulu,
            player.trophies
        ))
    except:
        log.error(f"Could not update for {player.name}")