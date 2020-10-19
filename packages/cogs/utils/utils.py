from typing import Optional

from coc import NotFound, EventsClient, Player
from coc.utils import is_valid_tag
from discord import Member
from discord.ext.commands import MemberConverter, UserConverter, NotOwner
from discord.ext.commands import Context, UserNotFound, MemberNotFound
import discord

from packages.private.settings import *
from packages.cogs.utils.discord_arg_parser import DiscordArgParse, DiscoArgParseException, DiscordCommandError
from packages.bot_ext import BotExt


async def get_discord_member(ctx: Context, disco_id: str, print_prt) -> Optional[Member]:
    print(disco_id)
    member = None
    for guild_member in ctx.guild.members:
        print(guild_member)

        if str(guild_member.id) == disco_id:
            print("Here")
            member = guild_member
        elif guild_member.name.lower() == disco_id.lower():
            print("Here2")
            member = guild_member
        elif guild_member.display_name.lower() == disco_id.lower():
            print("Here3")
            member = guild_member
        elif f"{guild_member.name}#{guild_member.discriminator}".lower() == disco_id.lower():
            print("Here4")
            member = guild_member

    if member:
        return member

    print("in here")

    # This sucks and doesn't work; doing it my own way

    converter = MemberConverter()
    try:
        global_user = await converter.convert(ctx, disco_id)
    except MemberNotFound:
        await print_prt(ctx, f'User `{disco_id}` not found', color='warning')
        return None
    return global_user




    return
    # Attempting guild manual check

    # Try a global fetch
    try:
        global_member = await ctx.bot.fetch_user(obj)
        if isinstance(global_member, discord.User):
            for guild_member in ctx.guild.members:
                if guild_member.id == global_member.id:
                    return guild_member, True
            return global_member, False
    except:
        pass

    # Attempting global converter
    try:
        global_member = await UserConverter().convert(ctx, obj)
        if isinstance(global_member, discord.User):
            for guild_member in ctx.guild.members:
                if guild_member.id == global_member.id:
                    return guild_member, True
            return global_member, False
    except:
        return None, False

    # TODO: Add what to do with the db obj


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
    player : Player
        Player object from the coc wrapper
    """
    if not is_valid_tag(player_tag):
        await print_ptr(ctx, title="Invalid Tag", description=f"`{player_tag}` is a invalid Clash Of Clans tag",
                        color="error")
        return None
    try:
        player = await coc_client.get_player(player_tag)
    except NotFound:
        await print_ptr(ctx, title="Invalid Tag", description=(f"Player with provided: `{player_tag}` tag does "
                                                               f"not exist"), color='error')
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
    if is_owner(ctx):
        return True

    for role in ctx.author.roles:
        if role.id == LEADERS:
            return True
    return False


async def update_user(ctx, guild_member, update_dict):
    """
    Coro to update a users attributes from nickname to roles
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    guild_member : discord.member.Member
        Discord guild user object
    update_dict : dict
        Dictionary containing the items to change
    Raises
    ------
    discord.Forbidden
        Raised if the bot does not have the proper permissions or the roles of the target is higher than the bots
    """
    await guild_member.edit(nick=update_dict['nick'],
                            roles=role_list(ctx, guild_member, update_dict['roles']))


async def new_user_roles(ctx, player):
    """
    Coro users to return the two default roles every new user gets when they join the clan
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    player : coc.SearchPlayer
        Clash player object
    Returns
    -------
    List of default roles
    """
    # Check if the town hall is supported
    if player.town_hall not in ctx.bot.keys.static_th_roles:
        raise discord.InvalidData(f'Role `{player.town_hall}` does not exist. Create the role first.')
    # Get guild object
    zulu_server = ctx.bot.get_guild(ctx.bot.keys.zulu_server)

    # Get default user roles
    town_hall_role_id = ctx.bot.keys.static_th_roles[player.town_hall]
    town_hall_role = zulu_server.get_role(town_hall_role_id)
    member_role = zulu_server.get_role(ctx.bot.keys.coc_member_role)

    return [town_hall_role, member_role]


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
        await bot_ext.embed_print(ctx=ctx, title=error.base_name, description=error.msg, color='error')
        return None
