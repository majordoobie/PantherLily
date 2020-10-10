from discord.ext import commands
from packages.cogs.utils import Utils

class Role_Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.util = Utils(self.bot)

    @commands.group(aliases=['r'])
    async def roles(self, ctx):
        '''
        Group method used to manage roles

        Commands
        --------
        list
            List all the roles of the server

        find 
            Find members with the specified role, with the options of using the
            with statement to find members with two roles.
        '''
        # TODO: Test if user is a admin
        pass

    @roles.command(name='list')
    async def roles_list(self, ctx):
        '''
        Method is used to list all the roles in the server so the user can use
        the find command
        '''
        output = ''
        for index,role in enumerate(ctx.guild.roles):
            if role.id != 293943534028062721: # @everyone
                output += f"` {index:<2} ` ` {role.name} `\n"
        #await self.bot.embed_print(ctx, title='**__SERVER ROLES__**', description=output)
        await self.util.embed_print(ctx, title='**__SERVER ROLES__**', description=output)

    @roles.command(name='find')
    async def roles_find(self, ctx, *, cmd):
        '''
        Method is used to find users with a specific role. Optionally, you can
        specify the with statement to check for users with two roles.

        Examples:

        p.roles find th11s
        p.roles find th11s with elephino cwl
        '''
        primary = ''
        if 'with' in cmd:
            primary, secondary = cmd.split(' with ')
           
        # Test to see if the with statement was used
        if primary:
            for i in ctx.guild.roles:
                if str(i.id) == primary.lower() or i.name.lower() == primary.lower():
                    primary_role = i
                elif str(i.id) == secondary.lower() or i.name.lower() == secondary.lower():
                    secondary_role = i
            output = f"` TH ` ` Player `\n"
            for member in primary_role.members:
                if member in secondary_role.members:
                    output += f"` 00 ` ` {member.name:<25.25} `\n"
            await self.util.embed_print(ctx, title=f'**__MEMBERS WITH {primary_role.name} and {secondary_role.name}__**', description=output)

        # Send without the with statement
        else:
            for i in ctx.guild.roles:
                if str(i.id) == cmd.lower() or i.name.lower() == cmd.lower():
                    role = i
            output = f"` TH ` ` Player `\n"
            for member in role.members:
                output += f"` 00 ` ` {member.name:<25.25} `\n"
            await self.util.embed_print(ctx, title=f'**__MEMBERS WITH {role.name}__**', description=output)

    @roles.command(name='give')
    async def roles_give(self, ctx, *, cmd):
        role = ''
        role_str, members = cmd.split(' to ', 1)

        # Check if role exists
        for i in ctx.guild.roles:
            if str(i.id) == role_str.lower() or i.name.lower() == role_str.lower():
                role = i
        if not role:
            await ctx.send('Role does not exist')
        
        # Check that all users provide are valid
def setup(bot):
    bot.add_cog(Role_Manager(bot))