from typing import List

import asyncpg
from disnake.ext import commands
import disnake
import asyncio

from packages.utils.paginator import Paginator
from packages.utils.utils import is_leader
import packages.utils.bot_sql as sql

class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        description="Tester")
    async def error(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')

    @commands.slash_command(auto_sync=True)
    async def test(self, inter):
        embeds = [
            disnake.Embed(
                title="Paginator example",
                description="This is the first embed.",
                colour=disnake.Colour.random(),
            ),
            disnake.Embed(
                title="Paginator example",
                description="This is the second embed.",
                colour=disnake.Color.random(),
            ),
            disnake.Embed(
                title="Paginator example",
                description="This is the third embed.",
                colour=disnake.Color.random(),
            ),
        ]

        view = Paginator(embeds, 5)
        await inter.send(embeds=view.embed, view=view)



    # Creates the embeds as a list.
def setup(bot):
    bot.add_cog(Tester(bot))
