from discord.ext import commands
from discord import Forbidden, NotFound, HTTPException

class Administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def __repr__(self):
        return 'COG: packages.cogs.administrator'

    @commands.command(aliases=['kill'])
    async def _logout(self, ctx):
        await self.bot.logout()

    @commands.command(aliases=['load'])
    async def load_cog(self, ctx, cog : str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Loaded {cog} successfully')

    @commands.command(aliases=['unload'])
    async def unload_cog(self, ctx, cog : str):
        cog = f'{self.bot.cog_path}{cog}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Unloaded {cog} successfully')
        
    @commands.command(aliases=['re'])
    async def re_load(self, ctx, cog : str):
        cog = f'{self.bot.cog_path}{cog}'

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Reloaded {cog} successfully')

    @commands.command()
    async def list_cogs(self, ctx):
        output = ''
        for i in self.bot.cog_tupe:
            output += i.split('.')[-1] +'\n'
        await ctx.send(output)

def setup(bot):
    bot.add_cog(Administrator(bot))
    