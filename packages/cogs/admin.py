from discord.ext import commands
import logging

from packages.cogs.utils.utils import *
from bot import BotClient
from packages.database_schema import drop_tables


class Administrator(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Administrator')

    @commands.check(is_owner)
    @commands.command(aliases=['kill', 'k'])
    async def _logout(self, ctx):
        self.log.info('Closing connections...')
        await self.bot.embed_print(ctx, "Logging off")
        try:
            await self.bot.coc_client.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.pool.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.logout()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

    @commands.check(is_owner)
    @commands.command(aliases=['load'])
    async def load_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Loaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(aliases=['unload'])
    async def unload_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Unloaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(aliases=['re'])
    async def re_load(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'

        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Reloaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command()
    async def list_cogs(self, ctx):
        output = ''
        for i in self.bot.settings.enabled_cogs:
            output += i.split('.')[-1] + '\n'
        await ctx.send(output)



def setup(bot):
    bot.add_cog(Administrator(bot))
