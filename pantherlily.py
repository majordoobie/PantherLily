#Discord
from discord.ext import commands
import discord
from discord import Embed, Game, Guild

#APIs
from CoC_APIs.ClashConnectAPI import ClashConnectAPI
from CoC_APIs.CoC_Stats import ClashStats
from Database.ZuluBot_DB import ZuluDB
from discordBotAPI import BotAssist

#New Functions
import pandas as pd
import asyncio
from collections import OrderedDict
from configparser import ConfigParser
from requests import get
from datetime import datetime, timedelta
from sys import argv
from sys import exit as ex # Avoid exit built in
from os import path

import json # delete me

#####################################################################################################################
                                             # Set up the environment 
#####################################################################################################################
# Look for either the dev or live switch
if len(argv) == 2:
    if argv[-1] == "--live":
        botMode = "liveBot"
    elif argv[-1] == "--dev":
        botMode = "devBot"
    else:
        ex("\n[ERROR] Make sure to add the right switch to activate me.")
else:
    ex("\n[ERROR] Make sure to add the right switch to activate me.")


# Instanciate Config
config = ConfigParser(allow_no_value=True)
emoticons = ConfigParser(allow_no_value=True)

if botMode == "liveBot":
    configLoc = '/root/bots/waritsukeruBot/donatorConfig.ini'
    emoticonLoc = '/'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = f"{config['Bot']['bot_prefix']}")
    discord_client.remove_command("help")

elif botMode == "devBot":
    configLoc = 'zuluConfig.ini'
    emoticonLoc = 'CoC_APIs/emoticons.ini'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = "dev.")
    discord_client.remove_command("help")


# Instanciate botAssit and DB
botAPI = BotAssist(botMode, configLoc)

dbLoc = config[botMode]['db']
if dbLoc == "None":
    print(f"No dev file set in {botMode}")
    ex("Exiting")
else:
    dbconn = ZuluDB(dbLoc)

coc_client = ClashConnectAPI(config['Clash']['ZuluClash_Token'])


#####################################################################################################################
                                             # Discord Commands [info]
#####################################################################################################################
@discord_client.event
async def on_ready():
    """
    Simple funciton to display logged in data to terminal 
    """
    print(f'\n\nLogged in as: {discord_client.user.name} - {discord_client.user.id}\nDiscord Version: {discord.__version__}\n'
        f"\nRunning in [{botMode}] mode\n"
        "------------------------------------------\n"
        f"Prefix set to:          {config[botMode]['bot_Prefix']}\n"
        f"Config file set to:     {configLoc}\n"
        f"DB File set to:         {dbLoc}\n"
        "------------------------------------------")

    game = Game("if __main__ == __name__:")
    await discord_client.change_presence(status=discord.Status.online, activity=game)

@discord_client.command()
async def help(ctx):
    """
    Display help menu to user
    """
    arg = ctx.message.content.split(" ")[1:]
    if len(arg) == 0:
        embed = Embed(color=0x8A2BE2)
    elif arg[0] == '-v':
        embed = Embed(color=0x8A2BE2)
    elif arg[0] == '-vv':
        desc = ("Welcome to Zulu's donation tracker!")
        embed = Embed(title='NameComingSoon!', description= desc, color=0x8A2BE2)

    embed.add_field(name="Commands:", value="-----------", inline=True)
    
    helpp = ("Provides this help menu. \nOptional: -v provide CoC Leaders commands "
    "\nOptional: -vv provide a indepth description of the bot.")
    embed.add_field(name="/help <opt: -v>", value=helpp, inline=False)

    newinvite = ("Provides caller with a temporary link to the planning server with a default "
    "expiration of 10 minutes. You have the option of providing an integer which changes the "
    "expiration in minutes.")
    embed.add_field(name="/newinvite <opt: int>", value=newinvite, inline=False)

    lcm = ("Provides caller with a list of names and tags of all the users currently in Zulu.")
    embed.add_field(name="/lcm", value=lcm, inline=False)

    donation = ("Provides the caller with their donation progress for the week. The caller has the "
    "option of providing a clash tag to get the status of other users. A list of tags can be found in /lcm. "
    "\nNOTE: A full week must pass for the progression counts to be accurate.")
    embed.add_field(name="/donation <opt: clash tag>", value=donation, inline=False)

    if arg and (arg[0] == "-v" or arg[0] == "-vv"):
        embed.add_field(name="..", value="..", inline = False)
        embed.add_field(name="Commands: CoC Leaders", value="-----------", inline=True)

        useradd = ("Register the a new user into the SQL DataBase. This will also set default discord "
        "roles such as TH# role and CoC Members role. Finally, the users nickname will be changed "
        "to reflect their in game name.")
        embed.add_field(name="/useradd <#coc_tag> <@discord_mention>", value=useradd, inline=False)

        userkick = ('Places a "is_Active = False" flag on the user to stop the bot from tracking the user. '
        'The caller will be prompt with the option of adding an administrative note such as '
        '"User was kicked for misconduct" or "User is on temporary leave". These notes can be retrived with the '
        '"insert command here for it" command.')
        embed.add_field(name="/userkick <#coc_tag>", value=userkick, inline=False)

        activeUsers = ('Queries the database for all the users that are "active". This is helpful '
        'to verify users that are kicked.')
        embed.add_field(name="/active_users", value=activeUsers, inline=False)

        listroles = ("Simple command used for debugging.")
        embed.add_field(name="/listroles", value=listroles, inline=False)

        killit = ("Command to safely terminate the bot.")
        embed.add_field(name="/killswitch", value=killit, inline=False)

    
    await ctx.send(embed = embed)

@discord_client.command()
async def killbot(ctx):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return

    if botAPI.authorized(ctx, config):
        await ctx.send("Tearing down, please hold.")
        await ctx.send("Closing database..")
        dbconn.conn.close()
        with open(configLoc, 'w') as f:
                config.write(f)
        await ctx.send("Terminating bot..")
        await ctx.send("_Later._")
        await discord_client.logout()
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

@discord_client.command()
async def newinvite(ctx, *arg):
    """ Get the channel object to use the invite method of that channel """

    if botAPI.rightServer(ctx, config):
        targetServer = int(config['Discord']['PlanDisc_ID'])
        targetChannel = int(config['Discord']['PlanDisc_Channel'])

    else:
        print("User is using the wrong server")
        return

    # Try to create the invite object
    if len(arg) == 1 and arg[0].isdigit():
        channel = botAPI.invite(discord_client, targetServer, targetChannel)
        inv = await channel.create_invite(max_age = (int(arg[0]) *60), max_uses = 1 )
        await ctx.send(inv)
        return

    elif len(arg) == 0:
        channel = botAPI.invite(discord_client, targetServer, targetChannel)
        inv = await channel.create_invite(max_age = 600, max_uses = 1 )
        await ctx.send(inv)
        return
    
    else:
        await ctx.send("Wrong arguments used")
        return

@discord_client.command()
async def listroles(ctx):
    """ List the roles and ID in the current channel """

    if botAPI.rightServer(ctx, config):
        targetServer = int(config['Discord']['PlanDisc_ID'])
        targetChannel = int(config['Discord']['PlanDisc_Channel'])

    else:
        print("User is using the wrong server")
        return

    tupe = []
    guild_obj = discord_client.get_guild(int(config[botMode]['guild_lock']))
    for i in guild_obj.roles:
        tupe.append((i.name,i.id))

    max_length = 0
    for name in tupe:
        if len(name[0]) > max_length:
            max_length = len(name[0])
    tupe.sort()

    output = ''
    for name in tupe:
        output += "{:<{}} {}\n".format(name[0], max_length, name[1])

    await ctx.send("```{}```".format(output))

@discord_client.command()
async def lcm(ctx):
    """ List users in the current clan with their tag """

    if botAPI.rightServer(ctx, config):
        targetServer = int(config['Discord']['PlanDisc_ID'])
        targetChannel = int(config['Discord']['PlanDisc_Channel'])

    else:
        print("User is using the wrong server")
        return

    res = coc_client.get_clan(config['Clash']['ZuluClash_Tag'])

    # Quick check to  make sure that the https request was good
    if int(res.status_code) > 300:
        embed = Embed(color=0xff0000)
        msg = (f"Bad HTTPS request, please make sure that the bots IP is in the CoC whitelist. "
        f"Our current exit node is {get('https://api.ipify.org').text}")
        embed.add_field(name="Bad Request: {}".format(res.status_code),value=msg)
        await ctx.send(embed=embed)
        return

    # If we're able to talk to COC api
    else:
        mem_list = []
        for user in res.json()['memberList']:
            mem_list.append((user['name'],user['tag']))

        #sort the list and get the max length
        max_length = 0
        for user in mem_list:
            if len(user[0]) > max_length:
                max_length = len(user[0])
        mem_list.sort(key = lambda tupe_item: tupe_item[0].lower())

        output = ''
        for index, user in enumerate(mem_list):
            output += "[{:>2}] {:<{}} {}\n".format(index+1, user[0], max_length, user[1])

        await ctx.send("```{}```".format(output))
#####################################################################################################################
                                             # Discord Commands [Execution]
#####################################################################################################################
@discord_client.command()
async def useradd(ctx, clash_tag, disc_mention):
    """
    Function to add a user to the database and initiate tracking of that user
    """
    if botAPI.rightServer(ctx, config):
        targetServer = int(config['Discord']['PlanDisc_ID'])
        targetChannel = int(config['Discord']['PlanDisc_Channel'])

    else:
        print("User is using the wrong server")
        return

    # If user is authorized to use this command 
    if botAPI.authorized(ctx, config):
        clash_tag = clash_tag.lstrip("#") 
        if disc_mention.startswith("<") == False:
            msg = (f"Could not interpret the {disc_mention} argument. Make sure "
            "that you are mentioning the user such as @user")
            await ctx.send(embed=Embed(title=msg, color=0xff0000))
            return
        else:
            member_ID = ''.join(list(disc_mention)[2:-1])
            if member_ID.startswith("!"):
                disc_mention = member_ID[1:]
            else:
                disc_mention = member_ID
        # Evaluate if the discord user exists
        exists, disc_userObj = botAPI.is_DiscordUser(ctx, config, disc_mention)
 
        if exists == False:
            msg = (f"User id {disc_mention} does not exist on this server.")
            await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
            return
        else:
            pass

        # Evaluate if the user is part of reddit zulu
        res = coc_client.get_clan(config['Clash']['ZuluClash_Tag'])
        inClan = False
        for user in res.json()['memberList']:
            if user['tag'].lstrip("#").upper() == clash_tag.upper():
                inClan = True

        if inClan == False:
            msg = (f"{disc_userObj.display_name} must be part of Reddit Zulu before adding them.")
            await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
            return

        # Query CoC API to see if we have the right token and the right tag
        res = coc_client.get_member(clash_tag)

        if res.status_code != 200:
            msg = (f"Clash tag {clash_tag} was not found in Reddit Zulu. "
            "Or our exit node is not currently whitelisted. "
            f"Use {config[botMode]['bot_Prefix']}lcm to see the available Clash tags "
            "in Reddit Zulu and to verify if your IP is whitelisted.")
            await ctx.send(embed = Embed(title="HTTP ERROR", description=msg, color=0xFF0000))
            return
        else:
            memStat = ClashStats(res.json())

        # Retrieve the CoC Members Role Object
        CoCMem_Role = botAPI.get_RoleObj(ctx, "CoC Members")
        if isinstance(CoCMem_Role, discord.Role) == False:
            msg = (f"Clash role [CoC Members] was not found in Reddit Zulu discord")
            await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
            return
        
        # Retrieve the townHall Role Object
        thLvl_Role = botAPI.get_townhallRole(ctx, memStat.townHallLevel)
        if isinstance(thLvl_Role, discord.Role) == False:
            msg = (f"Town Hall Level {memStat.townHallLevel} is currently not supported")
            await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
            return

        # Change users default roles
        msg = (f"Applying default roles to {memStat.name}")
        await ctx.send(embed = Embed(title=msg, color=0x5c0189))
        if botAPI.contains_Role(disc_userObj, "CoC Members"):
            msg = (f"{memStat.name} already has CoC Members role.")
            await ctx.send(embed = Embed(description=msg, color=0xFFFF00))
        else:
            await disc_userObj.add_roles(CoCMem_Role)
            msg = (f"CoC Members role applied.")
            await ctx.send(embed = Embed(description=msg, color=0x00ff00))

        if botAPI.contains_Role(disc_userObj, thLvl_Role.name):
            msg = (f"{memStat.name} already has {thLvl_Role.name} role.")
            await ctx.send(embed = Embed(description=msg, color=0xFFFF00))
        else:
            contains, role = botAPI.contains_thRole(disc_userObj)
            if contains:
                await disc_userObj.remove_roles(botAPI.get_RoleObj(ctx, role))
            await disc_userObj.add_roles(thLvl_Role)
            msg = (f"{thLvl_Role.name} role applied.")
            await ctx.send(embed = Embed(description=msg, color=0x00ff00))

        msg = (f"Changing {memStat.name}'s nickname to reflect their in-game name.")
        await ctx.send(embed = Embed(title=msg, color=0x5c0189))

        # Change users nickname
        if disc_userObj.display_name == memStat.name:
            msg = (f"{memStat.name}'s discord nickname already reflects their in-game name.")
            await ctx.send(embed = Embed(description=msg, color=0xFFFF00))
        else:
            oldName = disc_userObj.display_name
            try:
                await disc_userObj.edit(nick=memStat.name)
                msg = (f"Changed {memStat.name} discord nickname from {oldName} to {disc_userObj.name}")
                await ctx.send(embed = Embed(description=msg, color=0x00ff00))
            except:
                msg = (f"It is impossible for a mere bot to change the nickname of a boss like you. "
                "Seriously though, bots are prohibited from doing this action to a discord leader.")
                await ctx.send(embed = Embed(description=msg, color=0xff0000))


        # Add user to database
        msg = (f"Adding {memStat.name} to Reddit Zulu's database.")
        await ctx.send(embed = Embed(title=msg, color=0x5c0189))
        error = dbconn.insert_userdata((
            memStat.tag,
            memStat.name,
            memStat.townHallLevel,
            memStat.league_name,
            disc_userObj.id,
            disc_userObj.joined_at.strftime('%Y-%m-%d %H:%M:%S'),
            "False",
            "True",
            "",
        ))
        if error != None:
            if error.args[0] == "UNIQUE constraint failed: MembersTable.Tag":
                msg = (f"UNIQUE constraint failed: MembersTable.Tag: {memStat.tag}\n\nUser already exists. Attempting to re-activate {memStat.name}")
                await ctx.send(embed = Embed(title="SQL ERROR", description=msg, color=0xFFFF00)) 
                result = dbconn.is_Active((memStat.tag))
                if isinstance(result, str):
                    print(result)
                    await ctx.send(embed = Embed(title="SQL ERROR", description=result, color=0xFF0000)) 
                    return
                else:
                    result = dbconn.set_Active(("True", memStat.tag))

                    if isinstance(result, str):
                        print(result)
                        await ctx.send(embed = Embed(title="SQL ERROR", description=result, color=0xFF0000)) 
                        return
                    else:
                        msg = (f"Successfully set {memStat.name} to active")
                        await ctx.send(embed = Embed(description=msg, color=0x00FF00)) 
            else:
                await ctx.send(embed = Embed(title="SQL ERROR", description=error.args[0], color=0xFF0000)) #send.args[0] == "database is locked":
                return

        error = dbconn.update_donations((
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            memStat.tag,
            memStat.achieve['Friend in Need']['value'],
            "True",
            memStat.trophies

        ))
        if isinstance(error, str):
            await ctx.send(embed = Embed(title="SQL ERROR", description=error, color=0xFF0000))
            return
        
        channel = botAPI.invite(discord_client, targetServer, targetChannel)
        await ctx.send(await channel.create_invite(max_age=600, max_uses=1))
        msg = (f"Welcome to Reddit Zulu {disc_userObj.mention}! "
        f"Please use the link above to join our planning server. The server is used to "
        "plan attacks with your new clanmates!")
        await ctx.send(msg)
        return

@useradd.error
async def info_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))


@discord_client.command()
async def mydonation(ctx):
    """
    Find the donation status of your users account
    """
    disc_UserID = ctx.author.id
    result = dbconn.get_usersTag(((205344025740312576,)))

    if not result:
        msg = (f"{ctx.author.display_name} was not found in our database. Have they been added?")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=msg, color=0xFF0000))
        return
    
    elif len(result) > 1:
        users =[ i[1] for i in result ]
        msg = (f"Oh oh, looks like we have duplicate entries with the same discord ID. Users list: {users}")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=msg, color=0xFF0000))
        return
    
    elif result[0][7] == "False":
        msg = (f"Sorry {result[0][1]}, I am no longer tracking your donations as your enrollment to Reddit Zulu is set to False. "
        "Please ping @CoC Leadership if this is a mistake.")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=msg, color=0xFF0000))
        return

    donation = dbconn.get_Donations((result[0][1], botAPI.lastSunday()))
    print(donation)
    return
    
    flag = False
    user_tupe = ()
    arg = ctx.message.content.split(" ")[1:]
    if len(arg) == 0:
        rows = DB.get_allUsers()
        for row in rows:
            if int(row[4]) == int(ctx.author.id):
                if row[7] == "True":
                    user_tupe = row
                    flag = True
                else:
                    msg = (f"User, {row[1]}, active flag is set to False. Please re-add this "
                    "user using /useradd.")
                    await ctx.send(embed = Embed(title=f"**Availability Error**", description=msg, color=0xff0000))
                    return

    elif len(arg) == 1:
        if arg[0].startswith("#"):
            pass
        else:
            arg[0] = "#"+arg[0]
        rows = DB.get_allUsers()
        for row in rows:
            if str(row[0]) == str(arg[0]):
                if row[7] == "True":
                    user_tupe = row
                    flag = True
                else:
                    msg = (f"User, {row[1]}, active flag is set to False. Please re-add this "
                    "user using /useradd.")
                    await ctx.send(embed = Embed(title=f"**Availability Error**", description=msg, color=0xff0000))
                    return

    if flag == False:
        msg = (f"Could not find the user {arg[0]} in the database. Please make sure "
        "that they exists in the clan by using the /lcm command, then add them using /useradd.")
        await ctx.send(embed = Embed(title=f"**DB ERROR**", description=msg, color=0xff0000))

    # if user exists proceed to calculate their donation
    if flag:
        # update the db first
        user_tag = user_tupe[0]
        res = coc_client.get_member(user_tag)
        mem_stat = CoC_Stats(res.json())
        in_zulu = "False"
        if mem_stat.currentClan_name == "Reddit Zulu":
            in_zulu = "True"
        else:
            in_zulu = "False"
        send = DB.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    mem_stat.coc_tag,
                    mem_stat.total_Donations,
                    in_zulu,
                    mem_stat.trophies
                ))
        if send != None:
            msg = f"Operational Error while inserting data."
            await ctx.send(embed = Embed(title=f"**SQL ERROR**\n{send}", description=msg, color=0xff0000))
            return

        rows = DB.get_allDonations(user_tupe[0], lastSunday())
        if len(rows) > 2:
            cur_donation = rows[-1][2] - rows[0][2]
            await ctx.send(f"{cur_donation}/300")
        else:
            await ctx.send(f"Not enough data to calcualte your progress. "
            f"current FIN #: {rows[-1][2]}")

# @mydonation.error
# async def mydonations_error(ctx, error):
#     await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def roster(ctx):
    """ Function is used to check what members are in which server """
    uniqueNames = []

    # All members in Reddit Zulu
    clashMembers = coc_client.get_clanMembers(config['Clash']['zuluclash_tag'])
    ClashMembers = [ (i['tag'], i['name']) for i in clashMembers.json()['items'] ]
    ClashMembers.sort(key = lambda tupe_item: tupe_item[1].lower())
    for member in ClashMembers:
        if member[1] not in uniqueNames:
            uniqueNames.append(member[1])

    # All members in the planning discord server
    planMembers = discord_client.get_guild(int(config['Discord']['plandisc_id'])).members  
    
    # All members registered 
    dbMembers = dbconn.get_allUsers()
    for member in dbMembers:
        if member[1] not in uniqueNames:
            uniqueNames.append(member[1])

    roster = {}
    for i in uniqueNames:
        roster[i] = {
            "Clash"   :   False,
            "DBZulu"  :   False,
            "PZulu"   :   False
        }

    for userName in roster.keys():
        for user in ClashMembers:
            if user[1] == userName:
                roster[userName]['Clash'] = True

        for user in planMembers:
            if user.display_name == userName:
                roster[userName]['PZulu'] = True

        for user in dbMembers:
            if user[1] == userName:
                roster[userName]['DBZulu'] = True

    line = (f"{emoticons['tracker bot']['zuluServer']}{emoticons['tracker bot']['planningServer']}{emoticons['tracker bot']['database']}\u0080\n")
    for userName in roster.keys():
        if roster[userName]['Clash'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        if roster[userName]['PZulu'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        if roster[userName]['DBZulu'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        line += f"  {userName}\n"
    await ctx.send(line)

    return


@discord_client.command()
async def mystats(ctx):
    userID = ctx.author.id
    result = dbconn.get_usersTag((205344025740312576,))
    if len(result) == 0:
        msg = (f"Could not find {ctx.author.display_name} in Zulu's database. Make sure they have "
        "been added.")
        await ctx.send(embed = Embed(title=f"SQL ERROR", description=msg, color=0xff0000))
        return

    # res = coc_client.get_member(result[0][0])
    res = coc_client.get_member("#L2G9VLUC")
    print(res)
    return
    if res.status_code != 200:
        msg = (f"Bad HTTPS request, please make sure that the bots IP is in the CoC whitelist. "
        f"Our current exit node is {get('https://api.ipify.org').text}")
        await ctx.send(embed = Embed(title=f"HTTP", description=msg, color=0xff0000))
        return

    memStat = ClashStats(res.json())
    troopLevels = (f"{emoticons['troops']['barbarian']} {str(memStat.troops['Barbarian']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['archer']} {str(memStat.troops['Archer']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['goblin']} {str(memStat.troops['Goblin']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['giant']} {str(memStat.troops['Giant']['level']):<2}|{str(9):<2}")
    troopLevels += (f"{emoticons['troops']['wallbreaker']} {str(memStat.troops['Wall Breaker']['level']):<2}|{str(8):<2}\n")
    troopLevels += (f"{emoticons['troops']['loon']} {str(memStat.troops['Balloon']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['Wizard']} {str(memStat.troops['Wizard']['level']):<2}|{str(9):<2}")
    troopLevels += (f"{emoticons['troops']['Healer']} {str(memStat.troops['Healer']['level']):<2}|{str(5):<2}")
    troopLevels += (f"{emoticons['troops']['drag']} {str(memStat.troops['Dragon']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['pekka']} {str(memStat.troops['P.E.K.K.A']['level']):<2}|{str(8):<2}\n")
    troopLevels += (f"{emoticons['troops']['minion']} {str(memStat.troops['Minion']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['hogrider']} {str(memStat.troops['Hog Rider']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['valkyrie']} {str(memStat.troops['Valkyrie']['level']):<2}|{str(7):<2}")
    troopLevels += (f"{emoticons['troops']['golem']} {str(memStat.troops['Golem']['level']):<2}|{str(8):<2}")
    troopLevels += (f"{emoticons['troops']['witch']} {str(memStat.troops['Witch']['level']):<2}|{str(4):<2}\n")
    troopLevels += (f"{emoticons['troops']['lavahound']} {str(memStat.troops['Lava Hound']['level']):<2}|{str(5):<2}")
    troopLevels += (f"{emoticons['troops']['bowler']} {str(memStat.troops['Bowler']['level']):<2}|{str(4):<2}")
    troopLevels += (f"{emoticons['troops']['miner']} {str(memStat.troops['Miner']['level']):<2}|{str(6):<2}")
    troopLevels += (f"{emoticons['troops']['babydragon']} {str(memStat.troops['Baby Dragon']['level']):<2}|{str(6):<2}")
    troopLevels += (f"{emoticons['troops']['icegolem']} {str(memStat.troops['Ice Golem']['level']):<2}|{str(4):<2}\n")
    troopLevels += (f"{emoticons['troops']['edrag']} {str(memStat.troops['Electro Dragon']['level']):<2}|{str(3):<2}")
    
    spellLevels = (f"{emoticons['spells']['lightning']} {str(memStat.spells['Lightning Spell']['level']):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['heal']} {str(memStat.spells['Healing Spell']['level']):<2}|{str(7):<2}")
    spellLevels += (f"{emoticons['spells']['rage']} {str(memStat.spells['Rage Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['jump']} {str(memStat.spells['Jump Spell']['level']):<2}|{str(3):<2}")
    spellLevels += (f"{emoticons['spells']['freeze']} {str(memStat.spells['Freeze Spell']['level']):<2}|{str(7):<2}\n")
    spellLevels += (f"{emoticons['spells']['poison']} {str(memStat.spells['Poison Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['earthquake']} {str(memStat.spells['Earthquake Spell']['level']):<2}|{str(4):<2}")
    spellLevels += (f"{emoticons['spells']['haste']} {str(memStat.spells['Haste Spell']['level']):<2}|{str(4):<2}")
    spellLevels += (f"{emoticons['spells']['clone']} {str(memStat.spells['Clone Spell']['level']):<2}|{str(5):<2}")
    spellLevels += (f"{emoticons['spells']['skeleton']} {str(memStat.spells['Skeleton Spell']['level']):<2}|{str(5):<2}\n")
    spellLevels += (f"{emoticons['spells']['batspell']} {str(memStat.spells['Bat Spell']['level']):<2}|{str(5)}")

    heroLevels = (f"{emoticons['heroes']['barbking']} {str(memStat.heroes['Barbarian King']['level']):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['archerqueen']} {str(memStat.heroes['Archer Queen']['level']):<2}|{str(60):<2}")
    heroLevels += (f"{emoticons['heroes']['grandwarden']} {str(memStat.heroes['Grand Warden']['level']):<2}|{str(30):<2}")

    embed = Embed(title = "Name variable", color = 0xE2E21A)
    embed.add_field(name = "Heroes", value=heroLevels, inline = False)
    embed.add_field(name = "Troops", value=troopLevels, inline = False)
    embed.add_field(name = "Spells", value=spellLevels, inline = False)
    await ctx.send(embed=embed)

#####################################################################################################################
                                             # Functions
#####################################################################################################################
async def weeklyRefresh(discord_client, botMode):
    """ Function used to update the databsae with new data """
    await discord_client.wait_until_ready()
    while not discord_client.is_closed():
        # Calculate the wait time in minute for next "top of hour"
        wait_time = 60 - datetime.utcnow().minute
        if wait_time <= 15:
            pass
        elif wait_time <= 30:
            wait_time = wait_time - 15
        elif wait_time <= 45:
            wait_time = wait_time - 30
        else:
            wait_time = wait_time - 45

        print(f"Waiting {wait_time} minutes until next update.")
        await asyncio.sleep(wait_time * 60)

        # Get all users in the database
        get_all = dbconn.get_allUsers()
        mem_ids = [ mem.id for mem in discord_client.get_guild(int(config[botMode]["guild_lock"])).members ]

        # See if the users are still part of the clan
        user = ''
        for user in get_all:
            if user[7] == "False":
                continue
            else:
                pass
            # Make user each user is in the planning server. Adjust their row accordingly 
            if user[6] == "True" and (user[4] in mem_ids):
                pass
            elif user[6] == "True" and (user[4] not in mem_ids):
                dbconn.set_inPlanning(("False", user[0]))
            elif user[6] == "False" and (user[4] in mem_ids):
                dbconn.set_inPlanning(("True", user[0]))
            elif user[6] == "False" and (user[4] not in mem_ids):
                pass
            else:
                print("Error")

            # Grab the users CoC stats to see if there is any updates needed on their row
            res = coc_client.get_member(user[0])
            playerStat = ClashStats(res.json())
            if res.status_code != 200:
                  print(f"Could not connect to CoC API with {user[0]}")
                  return

            # Grab the users discord object and the object for the TH role
            exists, disc_UserObj = botAPI.is_DiscordUser(discord_client, config, user[4])
            if exists == False:
                print(f"User does not exist {user[1]} does not exist in this server")
                continue
            roleObj_TH = botAPI.get_townhallRole(discord_client, playerStat.townHallLevel)
            
            # find if their TH role has changed
            for role in disc_UserObj.roles:
                if role.name.startswith('th'):
                    if role.name == roleObj_TH.name:
                        pass
                    else:
                        print("Updating TH level role")
                        await disc_UserObj.remove_roles(role)      # remove old th role
                        await disc_UserObj.add_roles(roleObj_TH)   # Give user TH# ROLE

            # Update donation table
            in_zulu = "False"
            if playerStat.currentClan_name == "Reddit Zulu":
                in_zulu = "True"
            else:
                in_zulu = "False"
            dbconn.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    playerStat.coc_tag,
                    playerStat.total_Donations,
                    in_zulu,
                    playerStat.trophies
                ))

            # update users table
            dbconn.update_users((playerStat.coc_tag, playerStat.th_lvl, playerStat.league))

if __name__ == "__main__":
    #discord_client.loop.create_task(weeklyRefresh(discord_client, botMode))
    discord_client.run(config[botMode]['Bot_Token'])
