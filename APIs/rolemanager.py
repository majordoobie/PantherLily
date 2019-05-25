import discord

class Rolemgr:
    """
    Class used to manage roles
    """
    def __init__(self, config, guild):
        self.config = config
        self.guild = guild

    def get_role(self, role_str):
        """Simple method to get rule objects""" 
        for role in self.guild.roles:
            if role.name == role_str:
                return role
        return None