from disnake.ext import commands

from packages.utils.utils import is_leader


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        description="Tester")
    async def error(self, ctx):
        print([][10])
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')


def setup(bot):
    bot.add_cog(Tester(bot))
