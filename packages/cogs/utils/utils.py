from discord.ext.commands import MemberConverter, UserConverter, NotOwner
import discord

from packages.private.settings import *

async def get_discord_member(ctx, obj):
    """
    Function used to get a member string if possible, if not a user string is returned. Otherwise it returns none.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        Represents the context in which a command is being invoked under.
    obj : str
        Argument representing one of the elements needed for retrieving a discord user/member object
    Returns
    -------
    Member : discord.member.Member
        Returns a member object is the user element is found within the guild
    User : discord.user.User
        Returns a user object if the user element is not within the guild
    None :
        Returns None if the element was not able to be converted
    in_guild : bool
        True is member is in the guild "discord.member.Member"
    """
    # Attempting guild manual check
    for member in ctx.guild.members:
        if str(member.id) == str(obj):
            return member, True
        elif member.name.lower() == obj.lower():
            return member, True
        elif member.display_name.lower() == obj.lower():
            return member, True
        elif f"{member.name}#{member.discriminator}".lower() == obj.lower():
            return member, True

    # Try a global fetch
    try:
        global_member = await ctx.bot.fetch_user(obj)
        if isinstance(global_member, discord.User):
            for member in ctx.guild.members:
                if member.id == global_member.id:
                    return member, True
            return global_member, False
    except:
        pass

    # Attempting global converter
    try:
        global_member = await UserConverter().convert(ctx, obj)
        if isinstance(global_member, discord.User):
            for member in ctx.guild.members:
                if member.id == global_member.id:
                    return member, True
            return global_member, False
    except:
        return None, False

    # TODO: Add what to do with the db obj

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
