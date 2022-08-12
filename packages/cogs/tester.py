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
        async with self.bot.pool.acquire() as conn:
            sql = """SELECT panel_name FROM happy"""
            rows = await conn.fetch(sql)

        print(type(rows))
        print(rows)


    # Creates the embeds as a list.
def setup(bot):
    bot.add_cog(Tester(bot))
