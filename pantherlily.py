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
import aiohttp
import asyncio
import bs4
from collections import OrderedDict
from configparser import ConfigParser
from datetime import datetime, timedelta
from requests import Response
import io
from os import path, listdir
import pandas as pd
from pathlib import Path
import random
import re
from requests import get
from sys import argv
from sys import exit as ex # Avoid exit built in

# Data visualization
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

import json
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
    configLoc = 'Configurations/zuluConfig.ini'
    emoticonLoc = 'Configurations/emoticons.ini'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}".split(' '))
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
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}".split(' '))
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
prefx = config[botMode]['bot_Prefix'].split(' ')[0]

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
async def help(ctx, *option):
    """
    Display help menu to user
    """
    listroles = ("List all the available roles along with their role ID. This command is mainly used for diagnosing errors.")

    lcm = ("List the members that are currently in Reddit Zulu along with their Clash Tag. This command is useful for registering "
        "new members.")

    roster = ("This command identifies every user in the Reddit Zulu discord server that has the 'CoC Members' role and checks "
        "if they exist in Zulu Base Planning discord server and in the Database. The command will query if the user is present "
        "in Reddit Zulu (clan) only if the user exists in the database.")

    newinvite = ("Provides an invite link to Zulu Base Planning discord server. By default, the link will expire in 10 minutes. "
        "The command takes an optional integer argument. The optional integer is used to set the expiration time in minutes for the link.")

    newinvite_ex = ("Provides an invite link to Zulu Base Planning discord server. By default, the link will expire in 10 minutes. "
        "The command takes an optional integer argument. The optional integer is used to set the expiration time in minutes for the link.\n\n"
        f"**[Examples]**\n{prefx}newinvite\n{prefx}newinvite 20")

    stats  = ("Show a graphical output of the user's current Clash of Clans profile. By default, the user who invoked the command will be "
        "used to query Clash of Clans. The command takes an optional @mention argument to query that user instead.")

    donation = ("Display the user's current donation progress for the week. The donation cut off is every Monday at 0100 Zulu (Sunday at 2000 EST). "
        "The command takes an optional @mention argument to query that user instead.")

    useradd = ("Register a new user to the database. It is mandatory to supply the user's clash tag and @mention arguments when invoking this command. "
        "Registering the user will change the user's nickname on discord to their in-game name along with assigning 'CoC Members' and 'th#s' roles.")

    useradd_ex = ("Register a new user to the database. It is mandatory to supply the users clash tag and @mention arguments when invoking this command. "
        "Registering the user will change the user's nickname on discord to their in-game name along with assigning 'CoC Members' and 'th#s' roles.\n\n"
        f"**[Examples]**\n{prefx}useradd #ABC1233 @mention")

    disable_user = ("Command **does not** remove the user from discord. The command is used to set a users 'active' status to False. This terminates the "
        "donation tracking process on the user. The action is recorded in the Notes section of the users SQL table. ")

    enable_user = ("Command **does not** register a user. This command is used to re-enable tracking a users donations. ")

    addnote = ("Append an administrative note to the users SQL table. The bot will automatically append the date and the user who added the note. "
        f"Please use {prefx}help --verbose to see more information on how to craft notes")

    notes = ("Panther Lily makes it easy to keep track of infractions and administrative notes on users. Every time a note is appended to the user's "
        "table, a timestamp and a signature are automatically added. Panther Lily also supports extracting messages as long as you supply the keyword "
        "'msgID:' followed by the id of the message (right click a message > copy id). You can add as many msgID's as you like. This will become useful "
        f"when using {prefx}viewnote as it will offer the user the option to retrieve all the discord messages by parsing the msgID keyword in the note.\n\n"
        "**[Example]**\nMissed another attack\nmsgID:123456789\nmsgID:987654321\n\nResults in:\n[16-FEB-2019 22:12]\nNote By SgtMajorDoobie\nMissed another attack\n"
        "msgID:123456789\nmsgID:987654321")

    lookup = ("Used to lookup for a user in the SQL database. The command will return the users name, clash tag, discord ID, clash level, active status, and "
        "profile notes if they are found. This is useful to see the status of a member or to find members from years ago that are still in the database. This "
        "is due to the users in the database staying forever. The only data that is recycled is the donation tracking table.")

    lookup_ex = ("Used to lookup for a user in the SQL database. The command will return the users name, clash tag, discord ID, clash level, active status, and "
        "profile notes if they are found. This is useful to see the status of a member or to find members from years ago that are still in the database. This "
        "is due to the users in the database staying forever. The only data that is recycled is the donation tracking table.\n\n**[Example]**\n"
        f"{prefx}lookup --tag #YC12LPJ\n{prefx}lookup -t #YC12LPJ\n{prefx}lookup --mention @mention\n{prefx}lookup --name SgtMajorDoobie #Case sensitive")

    deletenote = (f"Used to delete a users note in the database. This is the only way to fix errors. It is best to first {prefx}viewnote to copy the content you "
        f"still want to keep and then {prefx}addnote to add the correct content.")

    viewnote = (f"View the text note in the user's profile with the option of retrieving any messages identified in the notes. These messages are identified by "
        f"scanning for the 'msgID:' key. Use {prefx}help --verbose to see more on Notes and how to craft them properly.")

    getmessage = (f"Used to manually retrieve a msgID. This command is mostly used to diagnose bugs.")

    helpp = (f"Display this help menu. Use {prefx}help --verbose for examples.")

    export = (f"Command is used to export the weekly report. New reports are only available on Mondays at 0100 GMT (Sundays 2000).")

    report = (f"Unlike export that only exports an XLSX of the last accepted donations for a week, report reports the current status of the clan. "
        "The output is a HTML file.")

    versioning = ("Panther Lily Version: 1.2 \nhttps://github.com/majordoobie/PantherLily")

    if len(option) == 0:
        embed = discord.Embed(title="__Accountability Commands__", url= "https://discordapp.com")
        embed.add_field(name=f"**{prefx}listroles**", value=listroles)
        embed.add_field(name=f"**{prefx}lcm**", value=lcm)
        embed.add_field(name=f"**{prefx}roster**", value=roster)
        await ctx.send(embed=embed)

        embed = discord.Embed(title="__Utility Commands__", url= "https://discordapp.com")
        embed.add_field(name=f"**{prefx}help** [__opt: --verbose__]", value=helpp)
        embed.add_field(name=f"**{prefx}newinvite** [__opt: <int>__]", value=newinvite)
        embed.add_field(name=f"**{prefx}stats** [__opt: <@mention>__]", value=stats)
        embed.add_field(name=f"**{prefx}donation** [__opt: <@mention>__]", value=donation)
        embed.add_field(name=f"**{prefx}export**",value=export)
        embed.add_field(name=f"**{prefx}report**",value=report)
        await ctx.send(embed=embed)

        embed = discord.Embed(title="__Administrative Commands__", url= "https://discordapp.com")
        embed.add_field(name=f"**{prefx}useradd** <__#clashTag__> <__@mention__ | __DiscordID__> [__opt: FIN Value__]", value=useradd)
        embed.add_field(name=f"**{prefx}disable_user** <__@mention__>", value=disable_user)
        embed.add_field(name=f"**{prefx}enable_user** <__@mention__>", value=enable_user)
        embed.add_field(name=f"**{prefx}addnote** <__@mention__>", value=addnote)
        embed.add_field(name=f"**{prefx}lookup** <--__name__ | --__tag__ | --__discordID__>", value=lookup)
        embed.add_field(name=f"**{prefx}deletenote** <__@mention__>", value=deletenote)
        embed.add_field(name=f"**{prefx}viewnote** <__@mention__>", value=viewnote)
        embed.add_field(name=f"**{prefx}getmessage** <__discordMsgID__>", value=getmessage)
        embed.set_footer(text=versioning)
        await ctx.send(embed=embed)

    if option:
        if option[0] in ['--verbose', '-v']:
            embed = discord.Embed(title="__Accountability Commands__", url= "https://discordapp.com")
            embed.add_field(name=f"**{prefx}listroles**", value=listroles)
            embed.add_field(name=f"**{prefx}lcm**", value=lcm)
            embed.add_field(name=f"**{prefx}roster**", value=roster)
            await ctx.send(embed=embed)

            embed = discord.Embed(title="__Utility Commands__", url= "https://discordapp.com")
            embed.add_field(name=f"**{prefx}help** [__opt: --verbose__]", value=helpp)
            embed.add_field(name=f"**{prefx}newinvite** [__opt: <int>__]", value=newinvite_ex)
            embed.add_field(name=f"**{prefx}stats** [__opt: <@mention>__]", value=stats)
            embed.add_field(name=f"**{prefx}donation** [__opt: <@mention>__]", value=donation)
            await ctx.send(embed=embed)

            embed = discord.Embed(title="__Administrative Commands__", url= "https://discordapp.com",)
            embed.add_field(name=f"**{prefx}useradd** <__#clashTag__> <__@mention__ | __DiscordID__> [__opt: FIN Value__]", value=useradd_ex)
            embed.add_field(name=f"**{prefx}disable_user** <__@mention__>", value=disable_user)
            embed.add_field(name=f"**{prefx}addnote** <__@mention__>", value=addnote)
            embed.add_field(name=f"**{prefx}lookup** <--__name__ | --__tag__ | --__mention__ | --__global__>", value=lookup_ex)
            embed.add_field(name=f"**{prefx}deletenote** <__@mention__>", value=deletenote)
            embed.add_field(name=f"**{prefx}viewnote** <__@mention__>", value=viewnote)
            embed.add_field(name=f"**{prefx}getmessage** <__discordMsgID__>", value=getmessage)
            embed.add_field(name=f"**How to Craft Notes**", value=notes)
            embed.set_footer(text=versioning)
            await ctx.send(embed=embed)





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
        with open("shit.txt", 'w', encoding='utf-8') as outfile:
            output = ''
            for index, user in enumerate(mem_list):
                output += "[{:>2}] {:<{}} {}\n".format(index+1, user[0], max_length, user[1])
                outfile.write(f"{user[0]}:{user[1]}\n")

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

        queryResult = dbconn.get_user_byDiscID((zMember.id,))
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
    if line != '':
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

@discord_client.command(aliases=["man"])
async def manual(ctx):
    f = discord.File("Configurations/PantherLily_V1.pdf", filename="Manual.pdf")
    await ctx.send(file=f)

@discord_client.command(aliases=["s"])
async def stats(ctx, *, user: discord.Member = None):
    if user == None:
        user = ctx.author
        userID = user.id
        result = dbconn.get_user_byDiscID((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {ctx.author.display_name}")
            return
    else:
        userID = user.id
        result = dbconn.get_user_byDiscID((userID,))
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
    embed = Embed(title = f"**__{memStat.name}__**", description=desc, color = 0x00ff00)
    embed.add_field(name = "**Heroes**", value=heroLevels, inline = False)
    embed.add_field(name = "**Troops**", value=troopLevels, inline = False)
    embed.add_field(name = "**Spells**", value=spellLevels, inline = False)
    if memStat.league_badgeSmall == None:
        f = discord.File("Images/Unranked_League.png", filename='unrank.png')
        embed.set_thumbnail(url="attachment://unrank.png")
        await ctx.send(embed=embed, file=f)
    else:
        embed.set_thumbnail(url=memStat.league_badgeSmall)
        await ctx.send(embed=embed)

@stats.error
async def stats_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command(aliases=["d"])
async def donation(ctx, *, user: discord.Member = None):
    """
    Find the donation status of your users account
    """

    if user == None:
        user = ctx.author
        userID = user.id
        result = dbconn.get_user_byDiscID((userID,))
        if len(result) == 0:
            await ctx.send(f"No data was found for {ctx.author.display_name}")
            return
    else:
        userID = user.id
        result = dbconn.get_user_byDiscID((userID,))
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
    nextSun = lastSun + timedelta(days=7)
    donation = dbconn.get_Donations((result[0][0], lastSun.strftime("%Y-%m-%d %H:%M:%S"), nextSun.strftime("%Y-%m-%d %H:%M:%S")))
    lastDon = datetime.strptime(donation[0][0], "%Y-%m-%d %H:%M:%S")


    if len(donation) > 2:
        val = (lastDon - lastSun)
        if val.days == 0:
            remain = nextSun - datetime.utcnow()
            day = remain.days
            time = str(timedelta(seconds=remain.seconds)).split(":")
            msg = (f"**Donation Stat:**\n{donation[-1][2] - donation[0][2]} | 300\n"
                f"**Time Remaining:**\n{day} days {time[0]} hours {time[1]} minutes")
            await ctx.send(embed = discord.Embed(title=f"__**{user.display_name}**__", description=msg, color=0x000080))
            return

        else:
            active = datetime.utcnow() - lastDon
            await ctx.send(f"**WARNING**\nOnly {active.days} day(s) of data have been recorded. \nFirst donation on: [{lastDon.strftime('%Y-%m-%d %H:%M:%S')} Zulu]")

            remain = nextSun - datetime.utcnow()
            day = remain.days
            time = str(timedelta(seconds=remain.seconds)).split(":")
            msg = (f"**Donation Stat:**\n{donation[-1][2] - donation[0][2]} | 300\n"
                f"**Time Remaining:**\n{day} days {time[0]} hours {time[1]} minutes")
            await ctx.send(embed = discord.Embed(title=f"__**{user.display_name}**__", description=msg, color=0x000080))
            return

    else:
        await ctx.send("No data was returned, try running me again.")

@donation.error
async def mydonations_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

#####################################################################################################################
                                             # Admin Commands
#####################################################################################################################
@discord_client.command()
async def useradd(ctx, clash_tag, disc_mention, fin_override=None):
    """
    Function to add a user to the database and initiate tracking of that user
    """
    # test if the user ran the command from the right server 
    if botAPI.rightServer(ctx, config):
        pass
    else:
        print("User is using the wrong server")
        return

    # If user is authorized to use this command
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send("You are not authorized to use this command")
        return

    
    clash_tag = clash_tag.lstrip("#")
    disc_userObj = await botAPI.userConverter(ctx, disc_mention)

    if disc_userObj == None:
        msg = (f"User id {disc_mention} does not exist on this server.")
        await ctx.send(embed = Embed(title="ERROR", description=msg, color=0xFF0000))
        return
    else:
        pass

    # Query CoC API to see if we have the right token and the right tag
    res = coc_client.get_member(clash_tag)

    # Handle HTTP error 
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
            msg = (f"Changed {memStat.name} discord nickname from {oldName} to {memStat.name}")
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
                await ctx.send(embed = Embed(title="SQL ERROR", description=result, color=0xFF0000))
                return

            elif result[7] == "True": # If activ
                msg = (f"{memStat.name} is already set to active in the database.")
                await ctx.send(embed = Embed(title="SQL ERROR", description=msg, color=0xFF0000))
                return
            else:
                result = dbconn.set_Active(("True", memStat.tag))

                if isinstance(result, str):
                    await ctx.send(embed = Embed(title="SQL ERROR", description=result, color=0xFF0000))
                    return
                else:
                    msg = (f"Successfully set {memStat.name} to active")
                    await ctx.send(embed = Embed(description=msg, color=0x00FF00))
        else:
            await ctx.send(embed = Embed(title="SQL ERROR", description=error.args[0], color=0xFF0000)) #send.args[0] == "database is locked":
            return

    # Add the ability to override the current fin so that we can get the fin from the last "Sunday"
    if fin_override:
        fin_apply = fin_override
    else:
        fin_apply = memStat.achieve['Friend in Need']['value']

    error = dbconn.update_donations((
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        memStat.tag,
        fin_apply,
        "True",
        memStat.trophies
        ))

    if isinstance(error, str):
        await ctx.send(embed = Embed(title="SQL ERROR", description=error, color=0xFF0000))
        return

    await ctx.send("User added")


    # Disabled for now
    # memStat = ''ClashStats.ClashStats(res.json())
    # desc, troopLevels, spellLevels, heroLevels = statStitcher(memStat, emoticonLoc)
    # embed = Embed(title = f"{memStat.name}", description=desc, color = 0x00FF00)
    # embed.add_field(name = "Heroes", value=heroLevels, inline = False)
    # embed.add_field(name = "Troops", value=troopLevels, inline = False)
    # embed.add_field(name = "Spells", value=spellLevels, inline = False)
    # embed.set_thumbnail(url=memStat.league_badgeSmall)
    # await ctx.send(embed=embed)


    # Disabled for now
    # channel = botAPI.invite(discord_client, targetServer, targetChannel)
    # await ctx.send(await channel.create_invite(max_age=600, max_uses=1))
    # msg = (f"Welcome to Reddit Zulu {disc_userObj.mention}! "
    # f"Please use the link above to join our planning server. The server is used to "
    # "plan attacks with your new clanmates!")
    # await ctx.send(msg)

    return

@useradd.error
async def info_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def enable_user(ctx, *, member: discord.Member = None):

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

    msg = (f"You are about to set {member.display_name} CoC Member status to True "
        "are you sure you would like to continue?\n(Yes/No)")
    await ctx.send(msg)

    response = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    example = (f"{member.display_name} Back from LOA\n\n"
        "msgID:546408720872112128\nmsgID:546408729155993615")

    await ctx.send("A message is required. You are able to enter any text you "
        f"like or message IDs. You can then use {prefx}retrieve_msg command to extract "
        "any message IDs you have included in this note. To include a message "
        "ID make sure to prefix the ID with msgID:<id> to make it easier to parse for you.\n\n**Example:**")
    
    await ctx.send("```\n"
        f"{example}\n"
        "```")

    await ctx.send("Please enter your message:")

    def check(m):
        return m.author.id == ctx.author.id

    response = await discord_client.wait_for('message', check=check)
    await ctx.send(f"**You have entered:**\n{response.content}\n\nContinue? (Yes/No)")

    response2 = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response2.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    oldNote = dbconn.get_user_byDiscID((member.id,))
    note = oldNote[0][8]
    note += f"\n\n[{datetime.utcnow().strftime('%d-%b-%Y %H:%M').upper()}]\nNote by {ctx.author.display_name}\n"
    note += f"{response.content}"
    result = dbconn.set_kickNote((note, "True", member.id,))
    if result == 1:
        desc = (f"Successfully set {member.display_name} active status to True with "
            "the note provided above.")
        await ctx.send(embed = discord.Embed(title="COMMIT SUCCESS", description=desc, color=0x00FF00))
        return  
    
    else:
        desc = (f"Unable to find {member.display_name} in the database. Use {prefx}roster to verify "
            "user.")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=desc, color=0xFF0000))
        return 

@enable_user.error
async def enable_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def disable_user(ctx, query):

    # Attempt to resolve the user name
    res = await botAPI.userConverter(ctx, query)

    # If converter fails attemp to search through the DB for the username with no caps
    result = None

    # Test if we got nothing from the discord converter 
    if res == None:
        allMems = dbconn.get_allUsers()
        for i in allMems:
            if i[1].lower() == query.lower():
                result = dbconn.get_user_byDiscID((i[4],))                 
    else:
        result = dbconn.get_user_byDiscID((res.id,))

    if result == None:
        desc = (f"Was unable to resolve {query}. This command supports mentions, "
            "IDs, username and nicknames.")
        await ctx.send(embed = discord.Embed(title="RESOLVE ERROR", description=desc, color=0xFF0000))
        return


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

    if query == None:
        desc = (f"Mention argument is required")
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        return

    msg = (f"You are about to set {query} CoC Member status to False "
        "are you sure you would like to continue?\n(Yes/No)")
    await ctx.send(msg)

    response = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    example = (f"SgtMajorDoobie failed to meet weekly donation quota\n\n"
        "msgID:546408720872112128\nmsgID:546408729155993615")

    await ctx.send("A kick message is required. You are able to enter any text you "
        f"like or message IDs. You can then use {prefx}retrieve_msg command to extract "
        "any message IDs you have included in this kick message. To include a message "
        "ID make sure to prefix the ID with msgID:<id> to make it easier to parse for you.\n\n**Example:**")
        
    await ctx.send("```\n"
        f"{example}\n"
        "```")

    await ctx.send("Please enter your message:")

    def check(m):
        return m.author.id == ctx.author.id

    response = await discord_client.wait_for('message', check=check)
    await ctx.send(f"**You have entered:**\n{response.content}\n\nContinue? (Yes/No)")

    response2 = await discord_client.wait_for('message', check = botAPI.yesno_check)
    if response2.content.lower() == 'no':
        await ctx.send("Terminating function")
        return

    oldNote = dbconn.get_user_byDiscID((result,))
    note = oldNote[0][8]
    note += f"\n\n[{datetime.utcnow().strftime('%d-%b-%Y %H:%M').upper()}]\nNote by {ctx.author.display_name}\n"
    note += f"{response.content}"
    result = dbconn.set_kickNote((note, "False", result,))
    if result == 1:
        desc = (f"Successfully set {oldNote[1]} active status to False with "
            "the note provided above.")
        await ctx.send(embed = discord.Embed(title="COMMIT SUCCESS", description=desc, color=0x00FF00))
        return  
    
    else:
        desc = (f"Unable to find {oldNote[1]} in the database. Use {prefx}roster to verify "
            "user.")
        await ctx.send(embed = discord.Embed(title="SQL ERROR", description=desc, color=0xFF0000))
        return 

@disable_user.error
async def kickuser_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def addnote(ctx, mem):
    # Get user object 
    member = await botAPI.userConverter(ctx, mem)

    # If user object can't re resolved then exit 
    if member == None:
        desc = (f"Was unable to resolve {mem}. This command supports mentions, "
        "IDs, username and nicknames.")
        await ctx.send(embed = discord.Embed(title="RESOLVE ERROR", description=desc, color=0xFF0000))
        return

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

    # Query the users dad 
    result = dbconn.get_user_byDiscID((member.id,))
    if len(result) == 1:
        example = (f"Missed attack\nmsgID:123456789654\nmsgID: 4654876135")
        await ctx.send(f"What would you like to add {ctx.author.display_name}? "
            f"Remember to use the 'msgID:' when you want to include message ids in your notes.\n**Example**\n")
                
        await ctx.send("```\n"
            f"{example}\n"
            "```")

        def check(m):
            return m.author.id == ctx.author.id

        response = await discord_client.wait_for('message', check=check)
        await ctx.send(f"**You have entered:**\n{response.content}\n\nContinue? (Yes/No)")

        response2 = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if response2.content.lower() == 'no':
            await ctx.send("Terminating function")
            return

        oldNote = dbconn.get_user_byDiscID((member.id,))
        note = oldNote[0][8]
        note += f"\n\n[{datetime.utcnow().strftime('%d-%b-%Y %H:%M').upper()}]\nNote by {ctx.author.display_name}\n"
        note += f"{response.content}"
        result = dbconn.set_kickNote((note, "True", member.id,))
        if result == 1:
            desc = (f"Successfully added a note to {member.display_name}")
            await ctx.send(embed = discord.Embed(title="COMMIT SUCCESS", description=desc, color=0x00FF00))
            return  
        
        else:
            desc = (f"Unable to find {member.display_name} in the database. Use {prefx}roster to verify "
                "user.")
            await ctx.send(embed = discord.Embed(title="SQL ERROR", description=desc, color=0xFF0000))
            return 

    else:
        await ctx.send("No results were found, or duplicate results were found. Please checkout logs")

@discord_client.command()
async def lookup(ctx, option, query):
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

    if option not in ['--tag', '-t', '--name', '-n', '--global', '-g']:
        desc = (f"Invalid argument supplied: {option}")
        await ctx.send(embed = discord.Embed(title="ARG ERROR", description=desc, color=0xFF0000))
        return
    
    # disable showing notes if user is not in coc_head chats
    inLeaderChat = False
    if ctx.channel.id in [293953660059385857, 293953660059385857, 498720245691973672, 331565220688297995, 503660106110730256]: #513334681354240000  
        inLeaderChat = True

    # -tag option
    if option in ['--tag', '-t']:
        # Add a hash tag for the user if it's not there
        if query.startswith("#"):
            tag = query
        else:
            tag = f"#{query}"

        # Query the tab looking for this tag
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
                if result[7] == "True":
                    active = "Active"
                else:
                    active = "Inactive"
                embed.add_field(name="Status:", value=active, inline=False)
                if inLeaderChat:
                    embed.add_field(name="Profile Note:", value=note, inline=False)
                else:
                    embed.add_field(name="Profile Note:", value="Disabled in this channel.", inline=False)
                await ctx.send(embed=embed)
            return
        else:
            desc = (f"No results found in the database using ClashTag: {tag}")
            await ctx.send(embed = discord.Embed(title="RECORD NOT FOUND", description=desc, color=0xFF0000))
            return

    if option in ['--name', '-n']:
        # Attempt to resolve the user name
        res = await botAPI.userConverter(ctx, query)

        # If converter fails attemp to search through the DB for the username with no caps
        result = None

        # Test if we got nothing from the discord converter 
        if res == None:
            allMems = dbconn.get_allUsers()
            for i in allMems:
                if i[1].lower() == query.lower():
                    result = dbconn.get_user_byDiscID((i[4],))                 
        else:
            result = dbconn.get_user_byDiscID((res.id,))

        if result == None:
            await ctx.send("Could not find that user in the database.")
            return

        if len(result) > 0:
            result = result[0]
            if result[8] == '':
                note = "Empty"
            else:
                note = result[8]
            embed = discord.Embed(title=result[1], color=0x00FF80)
            embed.add_field(name="ClashTag:", value=result[0], inline=False)
            embed.add_field(name="TownHallLevel:", value=result[2], inline=False)
            embed.add_field(name="DiscordID:", value=result[4], inline=False)
            embed.add_field(name="Database Join:", value=result[5], inline=False)
            if result[7] == "True":
                active = "Active"
            else:
                active = "Inactive"
            embed.add_field(name="Status:", value=active, inline=False)
            if inLeaderChat:
                embed.add_field(name="Profile Note:", value=note, inline=False)
            else:
                embed.add_field(name="Profile Note:", value="Disabled in this channel.", inline=False)
            await ctx.send(embed=embed)
        return

    if option in ['--global', '-g']:
        res = await botAPI.userConverter(ctx, query)
        print("hello?")
        if res == None:
            await ctx.send("Could not find user in this server")
        else: 
            embed = discord.Embed(title="Global Lookup", color=0x00FF80)
            embed.add_field(name="Username: ", value=res, inline=False)
            embed.add_field(name="Display: ", value=res.display_name, inline=False)
            embed.add_field(name="Discord ID: ", value=res.id, inline=False)
            embed.add_field(name="Joined Server: ", value=res.joined_at.strftime("%d %b %Y %H:%M:%S").upper(), inline=False)
            out = ''
            for i in res.roles:
                out += f"{i.name}\n"
            embed.add_field(name="Current Roles: ", value=out, inline=False)
            print("here")
            await ctx.send(embed=embed)

@lookup.error
async def search_error(ctx, error):
    embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000)
    embed.add_field(name=f"**{prefx}lookup** <--__name__ | --__tag__ | --__discordID__> <__argument__>", value="See help menu")  
    await ctx.send(embed=embed)


@discord_client.command()
async def deletenote(ctx, mem):
    """ Function used to delete notes for the user supplieds database """
    # Get user object 
    member = await botAPI.userConverter(ctx, mem)

    # If user object can't re resolved then exit 
    if member == None:
        desc = (f"Was unable to resolve {mem}. This command supports mentions, "
        "IDs, username and nicknames.")
        await ctx.send(embed = discord.Embed(title="RESOLVE ERROR", description=desc, color=0xFF0000))
        return

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

    result = dbconn.get_user_byDiscID((member.id,))
    if len(result) == 1:
        note = result[0][8]
        await ctx.send(f"The current note set for {member.display_name} is:\n\n```{note}```\n\n ")

        await ctx.send("```\n"
            f"{note}\n"
            "```")

        await ctx.send("Would you like to proceed with deleting this note? This action cannot be undone.\n(Yes/No)")

        response = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if response.content.lower() == "no":
            await ctx.send("Terminating function")
            return
        else: 
            note = f"[{datetime.utcnow().strftime('%d-%b-%Y %H:%M').upper()}]\nDeleted by {ctx.author.display_name}"
            res = dbconn.set_kickNote((note, result[0][7], member.id,))
            if res == 1:
                desc = (f"Successfully cleared {member.display_name} note in the database")
                await ctx.send(embed = discord.Embed(title="COMMIT SUCCESS", description=desc, color=0x00FF00))
                return  
            
            else:
                desc = (f"Unable to find {member.display_name} in the database. Use {prefx}roster to verify "
                    "user.")
                await ctx.send(embed = discord.Embed(title="SQL ERROR", description=desc, color=0xFF0000))
                return 

@deletenote.error
async def deletenote_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def viewnote(ctx, mem):
    # Get user object 
    member = await botAPI.userConverter(ctx, mem)

    # If user object can't re resolved then exit 
    if member == None:
        desc = (f"Was unable to resolve {mem}. This command supports mentions, "
        "IDs, username and nicknames.")
        await ctx.send(embed = discord.Embed(title="RESOLVE ERROR", description=desc, color=0xFF0000))
        return
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
        
    result = dbconn.get_user_byDiscID((member.id,))
    if len(result) == 1:
        note = result[0][8]
        ids = []
        search = False
        if re.findall(r"msgID:.\d+", note, re.IGNORECASE):
            for i in re.findall(r"msgID:.\d+", note, re.IGNORECASE):
                ids.append(re.search(r"\d+", i).group())
        if ids:
            search = True
        await ctx.send(f"Current Notes for {member.display_name}:\n```{note}```")
        if search:
            await ctx.send(f"Message IDs found, would you like those messages retrieved?\n(Yes/No)")
            try:
                response = await discord_client.wait_for('message', check = botAPI.yesno_check, timeout=30)
                if response.content.lower() == 'no':
                    return
            except asyncio.TimeoutError:
                await ctx.send("Just letting you know.. I am no longer waiting for a response")
                return
            
            for msgID in ids:
                zuluServer = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
                leaderChannel = zuluServer.get_channel(int(config['Discord']['leadernotes']))
                try:
                    await ctx.send("Loading.. ")
                    msg = await leaderChannel.get_message(int(msgID))
                except discord.Forbidden as e:
                    msg = (f"Permission denied to view {leaderChannel.name}\n{e}")
                    await ctx.send(embed = discord.Embed(title="Forbidden Exception", description=msg, color=0xFF0000))
                    return
                except discord.NotFound as e:
                    msg = (f"Message not found")
                    await ctx.send(embed = discord.Embed(title=f"Message not found for id number {msgID}", description=msg, color=0xFF0000))
                    continue
                    
                if msg.attachments:
                    files = []
                    async with aiohttp.ClientSession() as session:
                        for attachment_obj in msg.attachments:
                            async with session.get(attachment_obj.url) as resp:
                                buffer = io.BytesIO(await resp.read())
                                files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
                    files = files or None
                    await ctx.send(f"**Message by:**\n{msg.author.display_name} on {msg.created_at.strftime('%d %b %Y %H:%M').upper()} Zulu\n"
                        f"**Content:**\n{msg.clean_content}", files=files)
                else:
                    await ctx.send(f"**Message by:**\n{msg.author.display_name} on {msg.created_at.strftime('%d %b %Y %H:%M').upper()} Zulu\n"
                        f"**Content:**\n{msg.clean_content}")
            return
    
    else:
        await ctx.send("No results were found, or duplicate results were found. Please checkout logs")

@viewnote.error
async def viewnote_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def getmessage(ctx, msgID):
    """ Get messages from leader-notes """
    if msgID.isdigit() == False:
        desc = (f"Invalid argument {msgID}")
        await ctx.send(embed = discord.Embed(title="RECORD NOT FOUND", description=desc, color=0xFF0000))
        return

    zuluServer = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
    leaderChannel = zuluServer.get_channel(int(config['Discord']['leadernotes']))
    try:
        await ctx.send("Loading.. ")
        msg = await leaderChannel.get_message(int(msgID))
    except discord.Forbidden as e:
        msg = (f"Permission denied to view {leaderChannel.name}\n{e}")
        await ctx.send(embed = discord.Embed(title="Forbidden Exception", description=msg, color=0xFF0000))
        return
    except discord.NotFound as e:
        msg = (f"Message not found")
        await ctx.send(embed = discord.Embed(title="Message not found", description=msg, color=0xFF0000))
        return
        
    if msg.attachments:
        files = []
        async with aiohttp.ClientSession() as session:
            for attachment_obj in msg.attachments:
                async with session.get(attachment_obj.url) as resp:
                    buffer = io.BytesIO(await resp.read())
                    files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
        files = files or None
        await ctx.send(f"**Message by:**\n{msg.author.display_name} on {msg.created_at.strftime('%d %b %Y %H:%M').upper()} Zulu\n"
            f"**Content:**\n{msg.clean_content}", files=files)
    else:
        await ctx.send(f"**Message by:**\n{msg.author.display_name} on {msg.created_at.strftime('%d %b %Y %H:%M').upper()} Zulu\n"
            f"**Content:**\n{msg.clean_content}")

@getmessage.error
async def getmsg_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))



@discord_client.command()
async def caketime(ctx):
    cakePath = "Images/cakes"
    ranCake = Path(cakePath).joinpath(random.choice(listdir(cakePath)))
    f = discord.File(str(ranCake), filename=str(ranCake.name))
    if ranCake.suffix == ".mp4":
        await ctx.send(file=f)
    else:
        embed = discord.Embed(title='Nubbz',color=0xFFD700)
        embed.set_footer(text=f"{str(ranCake.name)}")
        embed.set_image(url=f"attachment://{str(ranCake.name)}")
        await ctx.send(embed=embed, file=f)
     

#####################################################################################################################
                                             # Displaying pandas data
#####################################################################################################################
@discord_client.command()
async def export(ctx):
    # get last sunday integer to calculate last sunday. Then pull from that day and beyond
    today = datetime.utcnow()
    # use 5 minutes as a grace peried for when the db takes too long to update
    lastSunday = (today + timedelta(days=(1 - today.isoweekday()))).replace(hour=1, minute=5, second=0, microsecond=0)
    # Calculate the date range for the sql query
    startDate = (lastSunday - timedelta(weeks=4)).strftime('%Y-%m-%d %H:%M:%S')
    endDate = lastSunday.strftime('%Y-%m-%d %H:%M:%S')
    
    # query
    sql = (f"""
    SELECT 
        MembersTable.Name, 
		Memberstable.Tag, 
		MembersTable.is_Active, 
		DonationsTable.Tag, 
		DonationsTable.increment_date, 
		DonationsTable.Current_Donation 
    FROM 
		MembersTable, DonationsTable 
	WHERE
		MembersTable.Tag = DonationsTable.Tag
	AND
		DonationsTable.increment_date BETWEEN '{startDate}' AND '{endDate}'
	AND
		MembersTable.is_Active = 'True';
       """)
    # Create df out of sql data
    df = pd.read_sql_query(sql, dbconn.conn)
    df['increment_date'] = pd.to_datetime(df['increment_date'], format='%Y-%m-%d %H:%M:%S')

    if df.empty:
        await ctx.send("Not enough data collected to generate a report")
        return
    
    # Remove duplicate Tag column
    df = df.loc[:,~df.columns.duplicated()]
    
    # Create the date ranges
    mask1 = (df['increment_date'] > (lastSunday - timedelta(days=7))) & (df['increment_date'] < lastSunday)
    mask2 = (df['increment_date'] > (lastSunday - timedelta(days=14))) & (df['increment_date'] < (lastSunday - timedelta(days=7)))
    mask3 = (df['increment_date'] > (lastSunday - timedelta(days=21))) & (df['increment_date'] < (lastSunday - timedelta(days=14)))
    mask4 = (df['increment_date'] > (lastSunday - timedelta(days=28))) & (df['increment_date'] < (lastSunday - timedelta(days=21)))

    # Take the max FIN of each user as a series and convert to our new DF
    df_out = df.loc[mask1].groupby(['Name', 'Tag'])['Current_Donation'].max().reset_index()

    # Set index to the tags instead of the built-int int index
    df_out.set_index('Tag', inplace=True)

    # Change column name of "Current FIN" to the date
    df_out.rename(columns={"Current_Donation":f"{(lastSunday - timedelta(days=1)).strftime('%d%b').upper()}"}, inplace=True)

    # Do the same for the second column
    df_out[f'{(lastSunday - timedelta(days=8)).strftime("%d%b").upper()}'] = df.loc[mask2].groupby(['Name', 'Tag'])['Current_Donation'].max().reset_index().set_index('Tag')['Current_Donation']
    df_out[f'{(lastSunday - timedelta(days=8)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=8)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)
    # And the third and fourth
    df_out[f'{(lastSunday - timedelta(days=15)).strftime("%d%b").upper()}'] = df.loc[mask3].groupby(['Name', 'Tag'])['Current_Donation'].max().reset_index().set_index('Tag')['Current_Donation']
    df_out[f'{(lastSunday - timedelta(days=15)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=15)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)
    df_out[f'{(lastSunday - timedelta(days=22)).strftime("%d%b").upper()}'] = df.loc[mask4].groupby(['Name', 'Tag'])['Current_Donation'].max().reset_index().set_index('Tag')['Current_Donation']
    df_out[f'{(lastSunday - timedelta(days=22)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=22)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)

    # Calculate the difference between the two weeks
    #df_out['Diff'] = df_out.iloc[:,1] - df_out.iloc[:,2]
    df_out['Diff'] = df_out.apply(lambda x: x[1] - x[2] if x[2] > 0 else 0, axis=1)

    # Re order the columns
    cols = df_out.columns.tolist()
    cols.pop(-1)
    cols.insert(1, "Diff")
    df_out = df_out[cols]


    # # Calculate the donatio difference
    # df_out = df.loc[mask1].groupby(['Name', 'Tag'])['Current_Donation'].agg(['min','max']).diff(axis=1)

    # # Fix up the new column name
    # df_out.drop('min', axis=1, inplace=True)
    # df_out.rename(columns={'max':'Diff'}, inplace=True)
    # df_out = df_out[['Diff']].astype(np.int64)
    # df_out.reset_index(inplace=True)

    # # Set index to tag
    # df_out.set_index('Tag', inplace=True)

    # # Add a column for day of week, only count peoples donations that have a 0
    # df_out['Collection'] = df.loc[mask1].groupby('Tag')['increment_date'].min().dt.dayofweek

    # # Add a column for FIN
    # lastSunday = (lastSunday - timedelta(days=1))
    # df_out[lastSunday.strftime("%d%b").upper()] = df.loc[mask1].groupby('Tag')['Current_Donation'].max()
    # df_out = df_out[['Name','Collection','Diff', lastSunday.strftime("%d%b").upper()]]
    
    # # Create the other three columns in the excel sheet
    # df_out[f'{(lastSunday - timedelta(days=7)).strftime("%d%b").upper()}'] = df.loc[mask2].groupby('Tag')[['Current_Donation']].max()
    # df_out[f'{(lastSunday - timedelta(days=7)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=7)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)

    # df_out[f'{(lastSunday - timedelta(days=14)).strftime("%d%b").upper()}'] = df.loc[mask3].groupby('Tag')[['Current_Donation']].max()
    # df_out[f'{(lastSunday - timedelta(days=14)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=14)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)

    # df_out[f'{(lastSunday - timedelta(days=21)).strftime("%d%b").upper()}'] = df.loc[mask4].groupby('Tag')[['Current_Donation']].max()
    # df_out[f'{(lastSunday - timedelta(days=21)).strftime("%d%b").upper()}'] = df_out[f'{(lastSunday - timedelta(days=21)).strftime("%d%b").upper()}'].fillna(0).astype(np.int64)

    # df_out.loc[df_out.Collection > 0, 'Diff'] = 0
    # df_out.drop('Collection', axis=1, inplace=True)

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
   
    redFill = openpyxl.styles.fills.PatternFill(patternType='solid', fgColor=openpyxl.styles.colors.Color(rgb='00FF0000'))
    yelFill = openpyxl.styles.fills.PatternFill(patternType='solid', fgColor=openpyxl.styles.colors.Color(rgb='00FFFF00'))
    greFill = openpyxl.styles.fills.PatternFill(patternType='solid', fgColor=openpyxl.styles.colors.Color(rgb='0000FF00'))

    for r in dataframe_to_rows(df_out, index=False, header=True):
        ws.append(r)

    for cell in ws['A'] + ws[1]:
        cell.style = 'Pandas'

    for cell in ws['B']:
        if cell.value == 'Diff':
            continue
        if int(cell.value) < 300:
            if int(ws['D'+str(cell.row)].value) == 0:
                cell.fill = yelFill
            else:
                cell.fill = redFill
        else:
            cell.fill = greFill
    
    wb.save("pandas_openpyxl.xlsx")
    f = discord.File("pandas_openpyxl.xlsx", filename=f'{(lastSunday - timedelta(days=1)).strftime("%d%b").upper()}.xlsx')
    await ctx.send(file=f)

@export.error
async def export_err(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def report(ctx):
    today = datetime.utcnow()
    lastSunday = (today + timedelta(days=(1 - today.isoweekday()))).replace(hour=1, minute=0, second=0, microsecond=0)
    today = today.strftime('%Y-%m-%d %H:%M:%S')
    startDate = (lastSunday - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')

    sql = (f"""
        SELECT MembersTable.Name, 
            Memberstable.Tag, 
            MembersTable.is_Active, 
            DonationsTable.Tag, 
            DonationsTable.increment_date, 
            DonationsTable.Current_Donation 
        FROM 
            MembersTable, DonationsTable 
        WHERE
            MembersTable.Tag = DonationsTable.Tag
        AND
            DonationsTable.increment_date BETWEEN '{startDate}' AND '{today}'
        AND
            MembersTable.is_Active = 'True';
        """)

    # read SQL then convert date to tdate
    df = pd.read_sql_query(sql, dbconn.conn)
    df['increment_date'] = pd.to_datetime(df['increment_date'], format='%Y-%m-%d %H:%M:%S')

    # Remove duplicate Tag column
    df = df.loc[:,~df.columns.duplicated()]

    # First make the two masks
    before_sun = df['increment_date'] <= lastSunday
    after_sun = df['increment_date'] >= lastSunday   

    # Calculate the diff for this week and save it to its own DF
    # Rename column, reset index
    df_out = df.loc[after_sun].groupby(['Tag', 'Name'])['Current_Donation'].agg(['min','max']).diff(axis=1)
    df_out.drop('min', axis=1, inplace=True)
    df_out.rename(columns={'max':'Current'}, inplace=True)
    df_out.reset_index(inplace=True)
    df_out.set_index('Tag', inplace=True)

    # Create current FIN column
    df_out['Current_FIN'] = df.loc[after_sun].groupby(['Tag'])['Current_Donation'].max()

    # create last sunday column
    df_out[f'{(lastSunday - timedelta(days=1)).strftime("%d%b").upper()}'] = df.loc[before_sun].groupby(['Tag'])['Current_Donation'].max()

    # Clean up data change NaN and Float to 
    df_out[df_out.columns[1:]] = df_out[df_out.columns[1:]].fillna(0).astype(np.int64)

    # Sort names column
    df_out.sort_values('Name', inplace=True)

    # Dataframe to html
    html = df_out.to_html(index=False, justify="center")
    # load into a BS object
    soup = bs4.BeautifulSoup(html, "lxml")
    # extract the table
    table = soup.find("table")

    scriptTag = """// Query for the table tags and coloring to the table
const tableElm = document.getElementsByTagName("table")[0]; 
for (const row of tableElm.rows) {
  const childToStyle = row.children[1];
  console.log(childToStyle.textContent);
  if (Number(childToStyle.textContent) < 300) { 
    childToStyle.classList.add("redClass");
  } else if (Number(childToStyle.textContent) > 299) {
      childToStyle.classList.add("greenClass")
  }
}  """

    cssTag = """.redClass {
                    background-color: red;
                    font-weight : bold;
                    }
                    .greenClass {
                        background-color : green;
                        font-weight : bold;
                    }"""

    base = (f"""<!DOCTYPE html>
                <html>
                <head>
                    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0"> 
                    <title>Reddit Zulu</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/normalize.css@8.0.1/normalize.css"/>
                    <style>
                    {cssTag}
                    </style>
                </head>
                <body>
                {table}
                <script type="text/javascript">
                {scriptTag}
                </script>
                </body>
                </html>""") #.format(cssTag, table, scriptTag)

    soup = bs4.BeautifulSoup(base, "lxml")
    #new_link = soup.new_tag("script", src="pandamod.js")
    #soup.html.append(new_link)

    with open("Web/report.html", "w") as outfile:
        outfile.write(str(soup))

    f = discord.File("Web/report.html", filename="report.html")
    await ctx.send(file=f)
    await ctx.send(f"Keep in mind that the database only updates every 15 minutes.")
    return

@discord_client.command()
async def test(ctx, mem):
    print(mem)
    #m = await userConverter(ctx, mem)
    m = await botAPI.userConverter(ctx, mem)
    if m == None:
        await ctx.send(f"Sorry dude, couldn't find who ever {mem} was")
        return
    print(type(m))
    await ctx.send(m)
#####################################################################################################################
                                             # Loops & Kill Command
#####################################################################################################################
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
        await asyncio.sleep(wait_time * 60) #60
        #await asyncio.sleep(60)

        # Update message every time we update db
        game = Game("Updating Donations")
        await discord_client.change_presence(status=discord.Status.dnd, activity=game)

        guild = discord_client.get_guild(int(config[botMode]['guild_lock']))
        # Get all users in the database
        get_all = dbconn.get_allUsersWhereTrue()

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
            try:
                res = coc_client.get_member(user[0])
            except:
                print(f"Could not retrive clash member {user[0]} data")
                await (discord_client.get_channel(int(config["Discord"]["thelawn"]))).send(f"Could not retrive clash member {user[0]} data")
                continue

            if isinstance(res, Response) == False:
                print(f"Could not retrive clash member {user[0]} {user[1]} data. Returned a None object")
                await (discord_client.get_channel(int(config["Discord"]["thelawn"]))).send(f"Could not retrive clash member {user[0]} data. Returned a None object")
                continue

            if res.status_code != 200:
                  print(f"Could not connect to CoC API with {user[0]}")
                  await (discord_client.get_channel(int(config["Discord"]["thelawn"]))).send(f"Could not connect to CoC API with {user[0]}")
                  continue

            # Instantiate the users clash data
            try:
                memStat = ClashStats.ClashStats(res.json())
            except:
                print(f"Could not instantiate ClashStat object: {user[0]} {user[1]}")
                await (discord_client.get_channel(int(config["Discord"]["thelawn"]))).send(f"Could not instantiate ClashStat object: {user[0]} {user[1]}")
                continue

            # Grab the users discord object and the object for the TH role
            exists, disc_UserObj = botAPI.is_DiscordUser(guild, config, user[4])

            if exists == False:
                print(f"User does not exist {user[1]} does not exist in this server")
                await (discord_client.get_channel(int(config["Discord"]["thelawn"]))).send(f"User does not exist {user[1]} does not exist in this server")
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

        # reset message
        messages = [
            (discord.ActivityType.watching.listening ,   "Spotify"),
            (discord.ActivityType.watching.playing   ,   "Overwatch"),
            (discord.ActivityType.watching.playing   ,   "Clash of Clans"),
            (discord.ActivityType.watching.playing   ,   "with cat nip~"),
            (discord.ActivityType.watching.watching ,   "Fairy Tail"),
            (discord.ActivityType.watching.playing   ,   "I'm not a cat!"),
            (discord.ActivityType.watching.watching  ,   "panther.help")
        ]

        activ = random.choice(messages)
        activity = discord.Activity(type = activ[0], name=activ[1])
        await discord_client.change_presence(status=discord.Status.online, activity=activity)


if __name__ == "__main__":
    discord_client.loop.create_task(weeklyRefresh(discord_client, botMode))
    discord_client.run(config[botMode]['Bot_Token'])
