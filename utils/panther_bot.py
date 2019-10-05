# Built-in
import asyncio
import logging
from utils import context
# Non-built ins
from discord.ext import commands

#TODO add cog loaders
class PantherLily(commands.Bot):
    def __init__(self, config, bot_mode):
        self.config = config
        self.bot_mode = bot_mode
        super().__init__(command_prefix=self.config[self.bot_mode]['bot_prefix'])
        self.log = logging.getLogger('root.PantherLily')
        self.add_command(self.ping)
    def run(self):
        print("running")
        super().run(self.config[self.bot_mode]['bot_token'], reconnect=True)

    async def on_ready(self):
        print("connected")
        self.log.info('Bot successfully logged on')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=commands.Context)
        if ctx.command == None:
            return
        await ctx.invoke(ctx.command, ctx)


    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()

    # async def on_command_error(self, ctx, error):
    #     print(error)
    #     await ctx.send(error)

    @commands.command(name='ping')
    async def ping(self, ctx):
        print('here')
        await ctx.send('pong')