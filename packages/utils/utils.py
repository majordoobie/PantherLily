from typing import Optional, Union, List

from asyncpg.pool import Pool
from asyncpg import Record
from coc import NotFound, EventsClient, Player
from coc.utils import is_valid_tag
from datetime import datetime, timedelta
from disnake.member import Member
from disnake.ext.commands import NotOwner
from disnake.ext.commands import Context
from disnake import Role, Guild
import disnake

from packages.private.settings import *
from packages.utils.discord_arg_parser import DiscordArgParse, DiscoArgParseException, DiscordCommandError
from packages.bot_ext import BotExt
from packages.utils.bot_sql import sql_select_member_find


async def get_discord_member(
        ctx: disnake.ApplicationCommandInteraction,
        disco_id: Union[str, int],
        print_prt=None,
        _return=False) -> Optional[Member]:
    """
    Attempt to get a member object with the string provided. Converters are
    ignored they do not ignore case

    Parameters
    ----------
    ctx: Context
        Discord command context

    disco_id: str
        Any information about the user

    print_prt: Method
        Pointer to the global embed function of the bot
    _return: bool
        Return on failure instead of printing and raising error

    Returns
    -------
    member: Member or None
        Returns a member object
    """
    member = None
    if isinstance(disco_id, int):
        for guild_member in ctx.guild.members:
            if guild_member.id == disco_id:
                member = guild_member
    else:
        for guild_member in ctx.guild.members:
            if str(guild_member.id) == disco_id:
                member = guild_member
            elif guild_member.name.lower() == disco_id.lower():
                member = guild_member
            elif guild_member.display_name.lower() == disco_id.lower():
                member = guild_member
            elif f"{guild_member.name}#{guild_member.discriminator}".lower() == disco_id.lower():
                member = guild_member
    if member:
        return member
    else:
        # Return None for further evaluation
        if _return:
            return None

        if print_prt:
            await print_prt(ctx, f'Discord member: {disco_id} was not found', color=BotExt.WARNING)
            return None
        else:
            print(f'Discord member: {disco_id} was not found')


async def get_database_user(user_token: str, pool: Pool) -> Optional[Record]:
    """
    Search the database for the user string. The string will be casted to upper.
    Parameters
    ----------
    user_token: str
        Token used to match with
    pool:
        Database

    Returns
    -------
    record: Records or None
        Returns the record if a result was found

    Raises
    ------
    RuntimeError:
        Returns a error message followed by the list of list of users hist followed by all the records returned
    """
    sql = sql_select_member_find()
    integer_id = int(user_token) if user_token.isdigit() else -1
    async with pool.acquire() as con:
        members = await con.fetch(sql, user_token.upper(), integer_id)
    if len(members) > 1:
        records = [f"{record['discord_name']}" for record in members]
        raise RuntimeError("The query used resulted in more than one result which should not happen. "
                           "Please use a different string to query and let doobie know about this "
                           "situation.", records, members)
    elif not members:
        return None

    return members[0]


def get_default_roles(guild: Guild, settings: Settings, level: int) -> Union[List[Role], None]:
    """
    Return default roles for new users
    Parameters
    ----------
    guild: Guild
        Guild object in question
    settings: Setting
        Settings for the bot
    level: int
        Town hall level of the user

    Returns
    -------
    List[Role]
        List of default roles for the user
    """
    role_town_hall = settings.default_roles.get(f'th{level}s')
    role_coc_member = settings.default_roles.get('CoC Members')
    if role_town_hall:
        role_town_hall = guild.get_role(role_town_hall)
        role_coc_member = guild.get_role(role_coc_member)
        if isinstance(role_coc_member, Role) and isinstance(role_town_hall, Role):
            return [role_town_hall, role_coc_member,]

    return None


async def get_coc_player(ctx: Context, player_tag: str, coc_client: EventsClient, print_ptr) -> Optional[Player]:
    """
    Wrapper for querying for a player object to avoid duplicating code
    Parameters
    ----------
    ctx: Context
        Bot context

    player_tag: str
        Clash of Clans player tag

    coc_client: EventsClient
        Pointer to the coc_client object from the bot

    print_ptr: Method
        Simple pointer to the printing method for the bot_ext

    Returns
    -------
    Optional[Player]
    """
    # Clean up the tag a bit
    if not player_tag[0] == '#':
        player_tag = '#'+player_tag
    player_tag = player_tag.upper()

    if not is_valid_tag(player_tag):
        await print_ptr(ctx, title="Invalid Tag", description=f"`{player_tag}` is a invalid Clash Of Clans tag",
                        color=BotExt.WARNING)
        return None
    try:
        player = await coc_client.get_player(player_tag)
    except NotFound:
        await print_ptr(ctx, title="Invalid Tag", description=(f"Player with provided [`{player_tag}`] tag does "
                                                               f"not exist"), color=BotExt.WARNING)
        return None

    return player


def is_admin(ctx):
    """
    Simple check to see if the user invoking a command contains the elder role
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    Returns
    -------
    bool:
        True or False if user is an elder
    """
    for role in ctx.author.roles:
        if role.id == OWNER:
            return True
    return False


def is_owner(ctx):
    """
    Simple check to see if the user invoking a command is the owner
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    Returns
    -------
    bool:
        True or False if user is an elder
    """
    if ctx.author.id == OWNER:
        return True
    else:
        raise NotOwner("Not owner")


def is_leader(ctx):
    if ctx.author.id == OWNER:
        return True
    for role in ctx.author.roles:
        if role.id == LEADERS:
            return True
    return False


def role_list(ctx, guild_member, new_roles):
    """
    Simple function to extend the roles of a user
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    guild_member : discord.member.Member
        Discord guild user object
    new_roles : list
        List of discord roles to apply to the user
    Returns
    -------
    Complete list of roles to add to the user
    """
    # Users current roles
    member_roles = guild_member.roles
    # Static town hall roles
    static_roles = ctx.bot.keys.static_th_roles.values()
    # all of users town hall roles - ideally just one role
    town_hall_roles = [role for role in member_roles if role.id in static_roles]

    # Remove town hall roles if new one is present
    for role in new_roles:
        if role.id in static_roles:
            if town_hall_roles:
                for r in town_hall_roles:
                    member_roles.pop(member_roles.index(r))
            member_roles.append(role)
        else:
            member_roles.append(role)

    return list(set(member_roles))  # Remove potential duplicates


async def parse_args(ctx: Context, settings: Settings, arg_dict: dict, arg_string: str) -> Optional[DiscordArgParse]:
    """
    Quick way to parse arguments for all bot commands instead of repeating code
    Parameters
    ----------
    ctx: Context
        Discord context from the command

    settings: Settings
        Settings class

    arg_dict: dict
        Dictionary containing the DiscordArgParse specific arguments

    arg_string: str
        String of the users specified arguments

    Returns
    -------
    DiscordArgParse
    """
    try:
        parsed_args = DiscordArgParse(arg_dict, arg_string)
        return parsed_args
    except DiscoArgParseException as error:
        bot_ext = BotExt(settings)
        await bot_ext.send(ctx=ctx, title=error.base_name, description=error.msg, color=BotExt.ERROR)
        return None


def get_utc_monday() -> datetime:
    """Get the last monday for that week in eastern time as the "start of week" """
    today = datetime.utcnow()
    idx = today.weekday()  # MON = 0 -- SUN = 6
    if idx == 0:
        if today > today.replace(hour=1, minute=0, second=0, microsecond=0):
            last_monday = today.replace(hour=1, minute=0, second=0, microsecond=0)
        else:
            last_monday = today - timedelta(days=7)
            last_monday = last_monday.replace(hour=1, minute=0, second=0, microsecond=0)
    else:
        last_monday = today - timedelta(days=idx)
        last_monday = last_monday.replace(hour=1, minute=0, second=0, microsecond=0)

    return last_monday

