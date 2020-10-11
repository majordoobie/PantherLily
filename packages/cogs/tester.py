from discord.ext import commands
from coc import utils, NotFound
from discord import Embed
#from packages.cogs.utils import embed_print

class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await self.bot.embed_print(ctx=ctx, description='ponnnnnnnnng')

    @commands.command()
    async def test(self, ctx):
        print(dir(ctx.message.author))
        print(ctx.message.author.joined_at)
        print(ctx.message.author.name)
        print(ctx.message.author.nick)
        print(ctx.message.author.roles)
        print(ctx.message.author.created_at)
        print(ctx.message.author.display_name)
        print(ctx.message.author.id)
        print(ctx.message.author)


    @commands.command()
    async def get_user(self, ctx, player_tag):
        if not utils.is_valid_tag(player_tag):
            self.bot.embed_print(ctx, title="Invalid Tag", description="Please provide a valid player tag", color='warning')

        try:
            player = await self.bot.coc_client.get_player(player_tag)
        except NotFound:
            await self.bot.embed_print(ctx, title="Invalid Tag", description="Player using tag provided does not exist.",
                                       color='warning')


        self.bot.embed_print(ctx, player.name)


def setup(bot):
    bot.add_cog(Tester(bot))