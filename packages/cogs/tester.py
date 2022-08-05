from disnake.ext import commands


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Tester")
    async def ping(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')



def setup(bot):
    bot.add_cog(Tester(bot))
