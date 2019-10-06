from discord.ext import commands

class Administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        print('here')
        await ctx.send('pong')

def setup(bot):
    bot.add_cog(Administrator(bot))
    