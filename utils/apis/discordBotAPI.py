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
    def __init__(self, botMode, configLoc, dbconn, emoji, config):
        """
        Constructor for BotAssist class.

        Parameters:
            botMode     (str):      Mode bot is running in [liveBot, devBot]
            configLoc   (str):      File path to the configuration file
        """ 
        self.botMode = botMode
        self.configLoc = configLoc
        self.dbconn = dbconn 
        self.emoji = emoji,
        self.config = config

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
        f"  ConfigName:       {config[self.botMode]['bot_name']}\n"
        f"  BotName:          {bot.user.name}\n\n"
        f"[Config Data]\n"
        f"  Called From:      {ctx.guild.name}\n"
        f"  Called From:      {ctx.guild.id}\n"
        f"  Set To:           {config[self.botMode]['guild_name']}\n"
        f"  Set To:           {config[self.botMode]['guild_Lock']}\n"
        f"  ConfigLoc:        {self.configLoc}\n"
        f"  Pref:             {ctx.prefix}\n"
        f"  Created:          {bot.user.created_at}"
        )
        return data

    async def authorized(self, ctx, config):
        """
        Method used to evaluate a user

        Parameters:
            ctx     (obj):      Objected intercepted by discord decorator
            config  (obj):      configparser object
        """
        for role in ctx.author.roles:
            if role.name == "CoC Leadership":
                return True
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. {self.emoji['happy bot']['nyancat_big']}")
        return False

    async def rightServer(self, ctx, config):
        """ 
        Method to make sure the bot is running on the proper channel based on botMode

        Parameters:
            ctx     (obj):      Objected intercepted by discord decorator
            config  (obj):      configparser object 
        """
        if str(ctx.guild.id) == str(config[self.botMode]['guild_lock']):
            return True
        else:
            await ctx.channel.send("You are using this command from the wrong server.")
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

    def last_sunday(self):
        """
        Method used to return the last monday or "sunday" in eastern
        """
        today = datetime.utcnow()
        idx = (today.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
        if idx == 1:
            if today > today.replace(hour=1, minute=0, second=0, microsecond=0):
                last_monday = today.replace(hour=1, minute=0, second=0, microsecond=0)
        else:
            #last_monday = today - timedelta(7 + idx - 1)
            last_monday = today - timedelta(days=idx - (idx - 1))
            last_monday = last_monday.replace(hour=1, minute=0, second=0, microsecond=0)
    
        return last_monday

    def next_sunday(self):
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
            pass

        # Manually search through the server for members without case
        if isinstance(arg, int):
            for member in ctx.guild.members:
                if member.id == arg:
                    return member
            return None

        for member in ctx.guild.members:
            if arg.lower() == member.name.lower() or arg.lower() == member.display_name.lower():
                return member
        return None

    async def user_converter_db(self, ctx, arg):
        """ Used to find a user in the databse """
        member = None
        try:
            member = await discord.ext.commands.MemberConverter().convert(ctx, arg) 
            return member
        except:
            pass

        print('checking db')
        # Check by database
        all_users = self.dbconn.get_allUsers()
        user_id = None
        for user in all_users:
            if arg.lower() == user[1].lower():
                user_id = user[4]
            elif arg.lower().lstrip("#") == user[0].lstrip("#").lower():
                user_id = user[4]
            elif arg == str(user[4]):
                user_id = user[4]
        if user_id:
            print(user_id)
            try:
                member = await ctx.bot.fetch_user(user_id)
                if member:
                    return member
            except:
                pass
               
        # Check by name
        for member in ctx.guild.members:
            if arg.lower() == member.name.lower():
                return member
            if arg.lower() == member.display_name.lower():
                return member
        return None

    async def await_error(self, ctx, description, title="INPUT ERROR"):
        """ Display an error message to the user """
        embed = discord.Embed(
            title=title,
            description=description,
            color=0xFF0000,
        )
        embed.set_footer(text=self.config[self.botMode]["version"])
        await ctx.send(embed=embed)

    async def arg_parser(self, arg_dict, arg_string):
        """Parses out string and returns a dictionry

        Parses the arg_string to build a dictionary payload containing
        the switches used by the user.

        Example:
            arg_dict = {
                'option1': {
                    'default' : None,
                    'flags' : ['-o','--option1']
                }
            }
        Args:
            arg_dict: Dictioary containing the name of the switch with
                the expected switches used in the command line and a default.
            arg_string: String to parse to build the return dictionary payload.

        Returns:
            Dictioanry containing all the registered commands and their value.
            If the command was not used, then the default value for that command
            is used.
        """
        # Empty return payload
        parsed_args = {}

        # Set default positional if empty
        if arg_string is None:
            for switch, dictt in arg_dict.items():
                parsed_args[switch] = dictt['default']
            parsed_args['positional'] = None
            return parsed_args

        # create parsed_args
        arg_list = arg_string.split()

        # parse arg_list
        for switch, dictt in arg_dict.items():
            if any(i in dictt['flags'] for i in arg_list):
                if dictt['flags'][0] in arg_list:
                    index = arg_list.index(dictt['flags'][0])
                else:
                    index = arg_list.index(dictt['flags'][1])
                if (index + 1) < len(arg_list):
                    arg = arg_list.pop(index + 1)
                    arg_list.pop(index)
                    parsed_args[switch] = arg
                else:
                    parsed_args[switch] = dictt['default']
            else:
                parsed_args[switch] = dictt['default']

        if arg_list:
            parsed_args['positional'] = ' '.join(arg_list)
        else:
            parsed_args['positional'] = None 
        return parsed_args
