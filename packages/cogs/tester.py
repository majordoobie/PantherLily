from disnake.ext import commands

from disnake import client

class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.slash_command(description="Tester")
    async def ping(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')
        print([][10])



def setup(bot):
    bot.add_cog(Tester(bot))
