#Discord
import discord
from discord.ext import commands
from discord import Embed, Game, Guild

#APIs
from APIs.discordBotAPI import BotAssist
from APIs.ClashConnect import ClashConnectAPI
from APIs import ClashStats

# Database
from Database.ZuluBot_DB import ZuluDB

#New Functions
import asyncio
from collections import OrderedDict
from configparser import ConfigParser
from datetime import datetime, timedelta
from os import path
import pandas as pd
from requests import get
from sys import argv
from sys import exit as ex # Avoid exit built in

# Delete after production
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
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}")
    discord_client.remove_command("help")

elif botMode == "devBot":
    configLoc = 'Configurations/zuluConfig.ini'
    emoticonLoc = 'Configurations/emoticons.ini'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}")
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
prefx = config[botMode]['bot_Prefix']

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
        f"Prefix set to:          {prefx}\n"
        f"Config file set to:     {configLoc}\n"
        f"DB File set to:         {dbLoc}\n"
        f"Current exit node:      {get('https://api.ipify.org').text}\n"
        "------------------------------------------")

    game = Game(config[botMode]['game_msg'])
    await discord_client.change_presence(status=discord.Status.online, activity=game)

#####################################################################################################################
                                             # Help Menu
#####################################################################################################################
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

@help.error
async def help_erro(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))
#####################################################################################################################
                                             # Accountability Functions
#####################################################################################################################
@discord_client.command()
async def listroles(ctx):
    """ List the roles and ID in the current channel """
    if botAPI.rightServer(ctx, config):
        pass
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

@listroles.error
async def listroles_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def lcm(ctx):
    """ List users in the current clan with their tag """

    if botAPI.rightServer(ctx, config):
        pass
    else:
        print("User is using the wrong server")
        return

    res = coc_client.get_clan(config['Clash']['ZuluClash_Tag'])

    # Quick check to  make sure that the https request was good
    if int(res.status_code) != 200:
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

        await ctx.send("Current Members in Reddit Zulu\n```{}```".format(output))

@lcm.error
async def lcm_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def roster(ctx):
    """ Function is used to check what members are in which server """
    if botAPI.rightServer(ctx, config):
        pass
    else:
        print("User is using the wrong server")
        return

    # get all clan members
    res = coc_client.get_clan(config['Clash']['ZuluClash_Tag'])

    # Quick check to  make sure that the https request was good
    if int(res.status_code) != 200:
        embed = Embed(color=0xff0000)
        msg = (f"Bad HTTPS request, please make sure that the bots IP is in the CoC whitelist. "
        f"Our current exit node is {get('https://api.ipify.org').text}")
        embed.add_field(name="Bad Request: {}".format(res.status_code),value=msg)
        await ctx.send(embed=embed)
        return

    zuluServer = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
    zbpServer = discord_client.get_guild(int(config['Discord']['plandisc_id']))

    if zuluServer == None or zbpServer == None:
        await ctx.send("Unable to instantiate the guild object")
        return

    roster = {}
    # for zMember in (mem for mem in zuluServer.members if 'CoC Members' in (role.name for role in mem.roles)):
    mems = [ mem for mem in zuluServer.members if 'CoC Members' in (role.name for role in mem.roles) ]
    mems.sort(key=lambda x: x.display_name.lower())
    for zMember in mems:
        roster[zMember.display_name] = {
            "Clash"       :   False,
            "zuluServer"  :   True,
            "zbpServer"   :   False,
            "database"    :   False
        }
         # check if member is in zbpServer
        if zMember.id in ( pMember.id for pMember in zbpServer.members ):
            roster[zMember.display_name]['zbpServer'] = True

        queryResult = dbconn.get_usersTag((zMember.id,))
        if len(queryResult) == 1:
            roster[zMember.display_name]['database'] = True

            if queryResult[0][0] in ( member['tag'] for member in res.json()['memberList'] ):
                roster[zMember.display_name]['Clash'] = True


    line = (f"{emoticons['tracker bot']['zuluServer']}{emoticons['tracker bot']['planningServer']}{emoticons['tracker bot']['redditzulu']}{emoticons['tracker bot']['database']}\u0080\n")
    for userName in roster.keys():
        if roster[userName]['zuluServer'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        if roster[userName]['zbpServer'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        if roster[userName]['Clash'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        if roster[userName]['database'] == True:
            line += f"{emoticons['tracker bot']['true']}"
        else:
            line += f"{emoticons['tracker bot']['false']}"

        line += f"  {userName}\n"
        if len(line) > 1700:
            await ctx.send(line)
            line = ''
    await ctx.send(line)
    await ctx.send(f"**WARNING**\nClash query is not performed if user is missing from the database. Use {prefx}lcm "
        "to get an up to date list of clan members.")

@roster.error
async def roster_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))
#####################################################################################################################
                                             # Commands for all users
#####################################################################################################################
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

@newinvite.error
async def newinvite_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def stats(ctx, *, user: discord.Member = None):
    if user == None:
        user = ctx.author
        userID = user.id
        result = dbconn.get_usersTag((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {ctx.author.display_name}")
            return
    else:
        userID = user.id
        result = dbconn.get_usersTag((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {user.display_name}")
            return

    if len(result) == 0:
        msg = (f"Could not find {ctx.author.display_name} in Zulu's database. Make sure they have "
        "been added.")
        await ctx.send(embed = Embed(title=f"SQL ERROR", description=msg, color=0xff0000))
        return

    elif len(result) > 1:
        msg = (f"Found duplicate discord ID entries")
        await ctx.send(embed = Embed(title=f"SQL ERROR", description=msg, color=0xff0000))
        return

    res = coc_client.get_member(result[0][0])
    #res = coc_client.get_member("#L2G9VLUC") # L2G9VLUC zag; YRR9Y9LO mike

    if res.status_code != 200:
        msg = (f"Bad HTTPS request, please make sure that the bots IP is in the CoC whitelist. "
        f"Our current exit node is {get('https://api.ipify.org').text}")
        await ctx.send(embed = Embed(title=f"HTTP", description=msg, color=0xff0000))
        return

    memStat = ClashStats.ClashStats(res.json())
    desc, troopLevels, spellLevels, heroLevels = ClashStats.statStitcher(memStat, emoticonLoc)
    embed = Embed(title = f"{memStat.name}", description=desc, color = 0x00ff00)
    embed.add_field(name = "Heroes", value=heroLevels, inline = False)
    embed.add_field(name = "Troops", value=troopLevels, inline = False)
    embed.add_field(name = "Spells", value=spellLevels, inline = False)
    embed.set_thumbnail(url=memStat.league_badgeSmall)
    await ctx.send(embed=embed)

@stats.error
async def stats_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def donation(ctx, *, user: discord.Member = None):
    """
    Find the donation status of your users account
    """

    if user == None:
        user = ctx.author
        userID = user.id
        result = dbconn.get_usersTag((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {ctx.author.display_name}")
            return
    else:
        userID = user.id
        result = dbconn.get_usersTag((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {user.display_name}")
            return

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

    res = coc_client.get_member(result[0][0])
    memStat = ClashStats.ClashStats(res.json())

    in_zulu = "False"
    if memStat.clan_name == "Reddit Zulu":
        in_zulu = "True"
    else:
        in_zulu = "False"
    dbconn.update_donations((
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            memStat.tag,
            memStat.achieve["Friend in Need"]['value'],
            in_zulu,
            memStat.trophies
        ))

    lastSun = botAPI.lastSunday()
    donation = dbconn.get_Donations((result[0][0], botAPI.lastSunday()))
    lastSun = datetime.strptime(lastSun, "%Y-%m-%d %H:%M:%S")
    nextSun = datetime.strptime(botAPI.nextSunday(), "%Y-%m-%d %H:%M:%S")

    if len(donation) > 1:
        lastData = datetime.strptime(donation[0][0],"%Y-%m-%d %H:%M:%S" )
        val = (lastData - lastSun)
        if val.days == 0:
            remain = nextSun - datetime.utcnow()
            day = remain.days
            time = str(timedelta(seconds=remain.seconds)).split(":")
            msg = (f"**Donation Stat:**\n{donation[-1][2] - donation[0][2]} | 300\n"
                f"**Time Remaining:**\n{day} days {time[0]} hours {time[1]} minutes [Zulu Time]")
            await ctx.send(embed = discord.Embed(title=f"__**{user.display_name}**__", description=msg, color=0x000080))

        else:
            active = 7 - int(val.days)
            await ctx.send(f"**WARNING**\nOnly {active} days of data has been recorded. Please "
                "wait a full week before using this metric.")

            remain = nextSun - datetime.utcnow()
            day = remain.days
            time = str(timedelta(seconds=remain.seconds)).split(":")
            msg = (f"**Donation Stat:**\n{donation[-1][2] - donation[0][2]} | 300\n"
                f"**Time Remaining:**\n{day} days {time[0]} hours {time[1]} minutes [Zulu Time]")
            await ctx.send(embed = discord.Embed(title=f"__**{user.display_name}**__", description=msg, color=0x000080))

@donation.error
async def mydonations_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

#####################################################################################################################
                                             # Admin Commands
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
        exists, disc_userObj = botAPI.is_DiscordUser(ctx.guild, config, disc_mention)

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
            memStat = ClashStats.ClashStats(res.json())

        # Retrieve the CoC Members Role Object
        CoCMem_Role = botAPI.get_RoleObj(ctx.guild, "CoC Members")
        if isinstance(CoCMem_Role, discord.Role) == False:
            msg = (f"Clash role [CoC Members] was not found in Reddit Zulu discord")
            await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
            return

        # Retrieve the townHall Role Object
        thLvl_Role = botAPI.get_townhallRole(ctx.guild, memStat.townHallLevel)
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
                print(result)
                if isinstance(result, str):
                    print(result)
                    await ctx.send(embed = Embed(title="SQL ERROR", description=result, color=0xFF0000))
                    return

                elif result[7] == "True": # If activ
                    msg = (f"{memStat.name} is already set to active in the database.")
                    await ctx.send(embed = Embed(title="SQL ERROR", description=msg, color=0xFF0000))
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

        memStat = ClashStats.ClashStats(res.json())
        desc, troopLevels, spellLevels, heroLevels = ClashStats.statStitcher(memStat, emoticonLoc)
        embed = Embed(title = f"{memStat.name}", description=desc, color = 0x00FF00)
        embed.add_field(name = "Heroes", value=heroLevels, inline = False)
        embed.add_field(name = "Troops", value=troopLevels, inline = False)
        embed.add_field(name = "Spells", value=spellLevels, inline = False)
        embed.set_thumbnail(url=memStat.league_badgeSmall)
        await ctx.send(embed=embed)

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
async def kickuser(ctx, *, member: discord.Member = None):

    if botAPI.rightServer(ctx, config):
        pass
    else:
        print("User is using the wrong server")
        return
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    if member == None:
        desc = (f"Mention argument is required")
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        return

    msg = (f"You are about to set {member.display_name} CoC Member status to False "
        "are you sure you would like to continue?\n(Yes/No)")
    await ctx.send(msg)

    response = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    example = (f"{member.display_name} failed to meet weekly donation quota\n\n"
        "msgID:546408720872112128\nmsgID:546408729155993615")

    await ctx.send("A kick message is required. You are able to enter any text you "
        f"like or message IDs. You can then use {prefx}retrieve_msg command to extract "
        "any message IDs you have included in this kick message. To include a message "
        "ID make sure to prefix the ID with msgID:<id> to make it easier to parse for you.\n\n**Example:**"
        f"```{example}```")

    await ctx.send("Please enter your message:")

    def check(m):
        return m.author.id == ctx.author.id

    response = await discord_client.wait_for('message', check=check)
    await ctx.send(f"**You have entered:**\n{response.content}\n\nContinue? (Yes/No)")

    response2 = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response2.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    result = dbconn.set_kickNote((response.content, "False", member.id,))
    if result == 1:
        desc = (f"Successfully set {member.display_name} active status to False with "
            "the note provided above.")
        await ctx.send(embed = discord.Embed(title="COMMIT SUCCESS", description=desc, color=0x00FF00))
        return  
    
    else:
        desc = (f"Unable to find {member.display_name} in the database. Use {prefx}roster to verify "
            "user.")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=desc, color=0xFF0000))
        return 

@kickuser.error
async def kickuser_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def search(ctx, option, *query):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        print("User is using the wrong server")
        return
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    if option not in ['--tag', '-t', '--mention', '-m', '--name', '-n']:
        desc = (f"Invalid argument supplied: {option}")
        await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
        return
    
    if option in ['--tag', '-t']:
        if len(query) != 1:
            desc = (f"Invalid argument supplied: {''.join(query)}")
            await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
            return

        tag = query[0]
        results = dbconn.get_user_byTag((tag,))
        if len(results) > 0:
            for result in results:
                if result[8] == '':
                    note = "Empty"
                else:
                    note = result[8]
                embed = discord.Embed(title=result[1], color=0x00FF80)
                embed.add_field(name="ClashTag:", value=result[0], inline=False)
                embed.add_field(name="TownHallLevel:", value=result[2], inline=False)
                embed.add_field(name="DiscordID:", value=result[4], inline=False)
                embed.add_field(name="Database Join:", value=result[5], inline=False)
                embed.add_field(name="Active Status:", value=result[7], inline=False)
                embed.add_field(name="Profile Note:", value=note, inline=False)
                await ctx.send(embed=embed)
            return
        else:
            desc = (f"No results found in the database using ClashTag: {tag}")
            await ctx.send(embed = discord.Embed(title="RECORD NOT FOUND", description=desc, color=0xFF0000))
            return

    if option in ['--name', '-n']:
        if len(query) != 1:
            desc = (f"Invalid argument supplied: {''.join(query)}")
            await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
            return

        name = ''.join(query)
        results = dbconn.get_user_byName((name,))
        if len(results) > 0:
            for result in results:
                if result[8] == '':
                    note = "Empty"
                else:
                    note = result[8]
                embed = discord.Embed(title=result[1], color=0x00FF80)
                embed.add_field(name="ClashTag:", value=result[0], inline=False)
                embed.add_field(name="TownHallLevel:", value=result[2], inline=False)
                embed.add_field(name="DiscordID:", value=result[4], inline=False)
                embed.add_field(name="Database Join:", value=result[5], inline=False)
                embed.add_field(name="Active Status:", value=result[7], inline=False)
                embed.add_field(name="Profile Note:", value=note, inline=False)
                await ctx.send(embed=embed)
            return
        else:
            desc = (f"No results found in the database using ClashName: {name}\n\nRemember that "
                "searching by name is case sensitive. Consider using clash tag or discord id.")
            await ctx.send(embed = discord.Embed(title="RECORD NOT FOUND", description=desc, color=0xFF0000))
            return

    if option in ['--mention', '-m']:
        if len(query) != 1:
            desc = (f"Invalid argument supplied: {''.join(query)}")
            await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
            return

        query = query[0]
        if ''.join(query).isdigit():
            discID = ''.join(query)

        elif ''.join(query).startswith("<"):
            temp_discID = ''.join(list(query)[2:-1])
            if temp_discID.startswith("!"):
                discID = temp_discID[1:]
            else:
                discID = temp_discID
        else:
            desc = (f"Invalid argument supplied: {''.join(query)}")
            await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
            return

        results = dbconn.get_user_byDiscID((discID,))
        if len(results) > 0:
            for result in results:
                if result[8] == '':
                    note = "Empty"
                else:
                    note = result[8]
                embed = discord.Embed(title=result[1], color=0x00FF80)
                embed.add_field(name="ClashTag:", value=result[0], inline=False)
                embed.add_field(name="TownHallLevel:", value=result[2], inline=False)
                embed.add_field(name="DiscordID:", value=result[4], inline=False)
                embed.add_field(name="Database Join:", value=result[5], inline=False)
                embed.add_field(name="Active Status:", value=result[7], inline=False)
                embed.add_field(name="Profile Note:", value=note, inline=False)
                await ctx.send(embed=embed)
            return
        else:
            desc = (f"No results found in the database using Discord ID {discID}.")
            await ctx.send(embed = discord.Embed(title="RECORD NOT FOUND", description=desc, color=0xFF0000))
            return


@discord_client.command()
async def killbot(ctx):
    """ Send kill signal to bot to properly close down databse and config file """
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

@killbot.error
async def killbot_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

#####################################################################################################################
                                             # Loops
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

        print(f"\n\nWaiting {wait_time} minutes until next update.")
        await asyncio.sleep(wait_time * 60)

        guild = discord_client.get_guild(int(config[botMode]['guild_lock']))
        # Get all users in the database
        get_all = dbconn.get_allUsers()

        # See if the users are still part of the clan
        user = ''
        for user in get_all:
            # if mem in planning server
            if int(user[4]) in (mem.id for mem in discord_client.get_guild(int(config['Discord']['plandisc_id'])).members):
                if user[6] == "True":
                    pass
                else:
                    dbconn.set_inPlanning(("True", user[0]))
            else:
                if user[6] == "False":
                    pass
                else:
                    dbconn.set_inPlanning(("False", user[0]))

            # Grab the users CoC stats to see if there is any updates needed on their row
            res = coc_client.get_member(user[0])
            memStat = ClashStats.ClashStats(res.json())
            if res.status_code != 200:
                  print(f"Could not connect to CoC API with {user[0]}")
                  return

            # Grab the users discord object and the object for the TH role
            exists, disc_UserObj = botAPI.is_DiscordUser(guild, config, user[4])
            if exists == False:
                print(f"User does not exist {user[1]} does not exist in this server")
                continue

            # Grab users role object
            roleObj_TH = botAPI.get_townhallRole(guild, memStat.townHallLevel)

            # find if their TH role has changed
            thRoles =[ role for role in disc_UserObj.roles if role.name.startswith('th') ]
            if len(thRoles) == 0:
                await disc_UserObj.add_roles(roleObj_TH)
            elif len(thRoles) > 1:
                for role in thRoles:
                    await disc_UserObj.remove_roles(role)
                await disc_UserObj.add_roles(roleObj_TH)
            else:
                if thRoles[0].name.lower() == roleObj_TH.name.lower():
                    pass
                else:
                    await disc_UserObj.remove_roles(thRoles[0])
                    await disc_UserObj.add_roles(roleObj_TH)

            # Check to see if they are current in zulu or somewhere else
            in_zulu = "False"
            if memStat.clan_name == "Reddit Zulu":
                in_zulu = "True"
            else:
                in_zulu = "False"
            dbconn.update_donations((
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    memStat.tag,
                    memStat.achieve["Friend in Need"]['value'],
                    in_zulu,
                    memStat.trophies
                ))

            # update users table
            dbconn.update_users((memStat.tag, memStat.townHallLevel, memStat.league_name))


if __name__ == "__main__":
    discord_client.loop.create_task(weeklyRefresh(discord_client, botMode))
    discord_client.run(config[botMode]['Bot_Token'])
