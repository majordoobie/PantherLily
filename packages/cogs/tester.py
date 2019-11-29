from discord.ext import commands

class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('ponnnnnnng')

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

def setup(bot):
    bot.add_cog(Tester(bot))