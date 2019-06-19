class Rolemgr:
    """
    Class used to manage roles
    """
    def __init__(self, config):
        """Init"""
        self.config = config
        self.guild = None

    def initializer(self, guild):
        """Used to assign values to attributes"""
        self.guild = guild

    def get_role(self, role_str):
        """Simple method to get rule objects"""
        for role in self.guild.roles:
            if role.name == role_str:
                return role
        return None

    def get_th(self, thlvl):
        """Retrieves the proper role for the given TH value"""
        levels = [9, 10, 11, 12]
        str_roles = ['th9s', 'th10s', 'th11s', 'th12s']
        for level, str_role in zip(levels, str_roles):
            if thlvl == level:
                return self.get_role(str_role)
        return None

    async def change_name(self, disc_user, name):
        """Changes the users name"""
        await disc_user.edit(nick=name)
        return

    