from discord.ext import commands
from coc import utils, NotFound
from discord import Embed
#from packages.cogs.utils import embed_print
from packages.cogs.utils.utils import parse_args


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')

    @commands.command()
    async def test(self, ctx):
        members = await self.bot.coc_client.get_members('#2Y28CGP8')
        a = members[0]
        print(dir(a))
        print(dir(a.clan))
        for i in members:print(i.clan)


    @commands.command()
    async def get_user(self, ctx, *, arg_string):
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
                'required': True,
                'type': 'int'
            },
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return

        async with self.bot.pool.acquire() as con:
            row = await con.fetchrow('select * from discord_user where discord_id = $1', args.discord_id)

        print(row)


def setup(bot):
    bot.add_cog(Tester(bot))