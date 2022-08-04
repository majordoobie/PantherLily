from disnake.ext import commands
from disnake import Embed
# from packages.cogs.utils import embed_print
from packages.utils.utils import parse_args


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')

    @commands.command()
    async def test(self, ctx, arg_string):
        
        
        
        
        return
        HERO_PETS_ORDER = ["L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn"]

        player_tag = "#822ULGVY"
        player = await self.bot.coc_client.get_player(player_tag)
        print(dir(player))
        for i in player.home_troops:
            print(i.name)
            # if i.name in HERO_PETS_ORDER:
            #     print(i.name, i.is_max, i.level, i.max_level, i.village, sep="\n")
        return

        from packages.cogs.utils.utils import get_database_user
        user = await get_database_user(arg_string.upper(), self.bot.pool)
        print(user, "\n\n")

        return

        from packages.cogs.clash_stats.clash_stats_panel import ClashStats
        player = await self.bot.coc_client.get_player('L2G9VLUC')

        clash_stat = ClashStats(player)
        panel_a, panel_b = clash_stat.display_all()
        hero_pane = '\n'.join(clash_stat._get_heroes_panel().split('\n')[1:])
        troop_pane = '\n'.join(clash_stat._get_troops_panels().split('\n')[1:])
        siege_panel = '\n'.join(clash_stat._get_sieges_panel().split('\n')[1:])
        spell_panel = '\n'.join(clash_stat._get_spells_panels().split('\n')[1:])

        embed = {
            'fields': [
                {
                    'name': '\u200b',
                    'value': panel_a
                },
                {
                    'name': '**Heroes**',
                    'value': hero_pane
                },
                {
                    'name': '**Sieges**',
                    'value': siege_panel
                },
                {
                    'name': '**Troops**',
                    'value': troop_pane
                },
                {
                    'name': '**Spells**',
                    'value': spell_panel
                },
            ]
        }
        await ctx.send(embed=Embed.from_dict(embed))

    @commands.command()
    async def list_emojis(self, ctx):
        out = ''
        for emoji in self.bot.emojis:
            out += f'{emoji} | `<:{emoji.name}:{emoji.id}>`\n'
            if len(out) > 1900:
                await ctx.send(out)
                out = ''

        await ctx.send(out)

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
