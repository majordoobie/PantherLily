# Built-in
import asyncio
import logging
import traceback

# Non-built ins
from discord.ext import commands

COG_PATH = 'packages.cogs.'
COG_TUPLE = (
    'packages.cogs.administrator',
    'packages.cogs.tester',
    )
class PantherLily(commands.Bot):
    __slots__ = ('config', 'bot_mode', 'log')
    def __init__(self, config, bot_mode):
        self.config = config
        self.bot_mode = bot_mode
        self.cog_tupe = COG_TUPLE
        self.cog_path = COG_PATH
        super().__init__(command_prefix=self.config[self.bot_mode]['bot_prefix'])
        self.log = logging.getLogger('root.PantherLily')

    def run(self):
        print("Loading cogs...")
        for extension in COG_TUPLE:
            try:
                self.load_extension(extension)
            except Exception:
                print(f'Failed to load extension {extension}')
                self.log.error(traceback.print_exc())

        print('Cogs loaded - establishing connection...')
        super().run(self.config[self.bot_mode]['bot_token'], reconnect=True)
    
    # Connections
    async def on_resumed(self):
        self.log.info('Resumed connection from lost connection')

    async def on_ready(self):
        print("connected")
        self.log.info('Bot successfully logged on')

    # Commands
    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, commands.errors.ExtensionNotFound):
                print("Extension not found brah")

            elif isinstance(original, commands.errors.CommandNotFound):
                print('BROOO')

    async def on_error(self, ctx, error):
        await ctx.send("```py\n{}: {}\n```".format(type(error).__name__, str(error)))

