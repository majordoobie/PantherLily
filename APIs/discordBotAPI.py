from datetime import datetime, timedelta
import discord

class BotAssist:
    """
    BotAssist is used to assist making future bots by having one shared API

    Attributes:
        botMode     (str):      Mode bot is running in [liveBot, devBot]
        configLoc   (str):      File path to the configuration file
        botName     (str):      Name of the bot object
        servObj     (obj):      Server object the bot is running in
        botCreation (str):      Date the bot object was created
    """
    def __init__(self, botMode, configLoc):
        """
        Constructor for BotAssist class.

        Parameters:
            botMode     (str):      Mode bot is running in [liveBot, devBot]
            configLoc   (str):      File path to the configuration file
        """ 
        self.botMode = botMode
        self.configLoc = configLoc 

    def serverSettings(self, ctx, config, bot): 
        """
        Return bot related information for debugging

        Parameters:
            ctx     (obj):      Objected intercepted by discord decorator
            config  (obj):      configparser object
            bot     (obj):      Discord Bot object
        """
        data = (
        f"[Bot Data]\n"
        f"  Mode:             {self.botMode}\n"
        f"  ConfigName:       {config[self.botMode]['Bot_Name']}\n"
        f"  BotName:          {bot.user.name}\n\n"
        f"[Config Data]\n"
        f"  Called From:      {ctx.guild.name}\n"
        f"  Called From:      {ctx.guild.id}\n"
        f"  Set To:           {config[self.botMode]['Guild_Name']}\n"
        f"  Set To:           {config[self.botMode]['Guild_Lock']}\n"
        f"  ConfigLoc:        {self.configLoc}\n"
        f"  Pref:             {ctx.prefix}\n"
        f"  Created:          {bot.user.created_at}"
        )
        return data

    def authorized(self, ctx, config):
        """
        Method used to evaluate a user

        Parameters:
            ctx     (obj):      Objected intercepted by discord decorator
            config  (obj):      configparser object
        """
        for role in ctx.author.roles:
            if role.name == "CoC Leadership":
                return True
        return False

    def rightServer(self, ctx, config):
        """ 
        Method to make sure the bot is running on the proper channel based on botMode

        Parameters:
            ctx     (obj):      Objected intercepted by discord decorator
            config  (obj):      configparser object 
        """
        if str(ctx.guild.id) == str(config[self.botMode]['Guild_Lock']):
            return True
        else:
            return False

    def yesno_check(self, message):
        """
        Method used to return a boolean representing if a user selected the right choices

        Parameters:
            message     (obj):      wait_for discord object
        """
        if message.content.lower() in ['yes','no']:
            return True
        else:
            return False

    def is_DiscordUser(self, guild, config, discordUser_ID):
        """
        Method used to evalute a discord ID. Returns True and object if ID exists

        Parameters:
            bot             (obj):      Discord Bot object
            config          (obj):      configparser object
            member_ID       (str):      Discord id number of user 
        """
        userObj = guild.get_member(int(discordUser_ID))
        if userObj == None:
            return False, None
        else:
            return True, userObj

    def invite(self, bot, targetServer, targetChannel):
        """
        Method used to create an invitation for the planning server

        Parameters:
            bot             (obj):      Discord Bot object
            targetServer    (int):      ID of the server you want to get an invite for
            targetChannel   (int):      ID of the channel of the server you want to get # needed for inviteRequest
        """
        # Check to make sure that the guild we are attempting to reach is reachable
        allowed = False
        for guild in bot.guilds:
            if int(guild.id) == int(targetServer):
                allowed = True

        # If the bot is able to reach that server, continue grabbing the object of that server.
        if allowed:
            obj = bot.get_guild(targetServer)
            if isinstance(obj, discord.Guild):
                channel = obj.get_channel(targetChannel)
                if isinstance(channel, discord.TextChannel):
                    return channel
                else:
                    msg = (f"Unable to retrive the channel {targetChannel}. However, The guild {targetServer} "
                    "Does exist")
            else:
                msg = (f"Unable to retrieve the guild object using {targetServer} id")
                return msg
        else:
            msg = (f"Unable to perform this function. bot {bot.user.name}--{bot.user.id} must exist in "
            f"target server: {targetServer} ")
            return msg

    def lastSunday(self):
        """
        Method used to return the last sunday; used for the sql update
        """
        today = datetime.utcnow()
        delta = 1 - today.isoweekday()      # days till last "sunday"
        monday = today + timedelta(delta)   # datetime of last "sunday" #monday 0100 == sunday 2000
        monday = monday.replace(hour=1, minute=0, second=0, microsecond=0)
        #return_date = monday.strftime('%Y-%m-%d')+" 01:00:00"
        return monday

    def nextSunday(self):
        """
        Method used to return the next sunday; used for the sql update
        """
        today = datetime.utcnow()
        delta = 1 - today.isoweekday()
        monday = today + timedelta(delta)
        monday = monday + timedelta(days=7) 
        return_date = monday.strftime('%Y-%m-%d')+" 01:00:00"
        return return_date

    def get_RoleObj(self, guild, roleStr):
        """
        Method used to retrive a role object
        """
        for role in guild.roles:
            if role.name == roleStr:
                return role
        return None

    def contains_Role(self, userObj, roleStr):
        """
        Method is used to comfirm if the user already has the role string supplied
        """
        for role in userObj.roles:
            if role.name == roleStr:
                return True
        return False

    def contains_thRole(self, userObj):
        """
        Method used to see if the user already has a TH role that no longer applies
        """
        str_roles = ['th9s', 'th10s', 'th11s', 'th12s']
        for role in userObj.roles:
            if role in str_roles:
                return True, role
        return False, None
        
    def get_townhallRole(self, guild, townHallLvl):
        """
        Method used to retrive the object of a townhall role

        Parameters:
            ctx             (obj):      Discord Bot object
            townHallLvl     (int):      Level of the Town Hall
        """
        levels = [9, 10, 11, 12]
        str_roles = ['th9s', 'th10s', 'th11s', 'th12s']
        for level, str_role in zip(levels, str_roles):
            if townHallLvl == level:
                return self.get_RoleObj(guild, str_role)
        return None


    async def userConverter(self, ctx, arg):
        """ Used to find a user based on their mention / ID / or name """
        try:
            return await discord.ext.commands.MemberConverter().convert(ctx, arg) 
        except:
            return None

         

            




