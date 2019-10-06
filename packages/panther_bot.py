# Built-in
import asyncio
import logging
import traceback

# Non-built ins
from discord.ext import commands

COGS = [
    "packages.administrator"
]
class PantherLily(commands.Bot):
    def __init__(self, config, bot_mode):
        self.config = config
        self.bot_mode = bot_mode
        super().__init__(command_prefix=self.config[self.bot_mode]['bot_prefix'])
        self.log = logging.getLogger('root.PantherLily')
        
        for extension in COGS:
            try:
                self.load_extension(extension)
            except Exception:
                print(f'Failed to load extension {extension}')
                self.log.error(traceback.print_exc())

    def run(self):
        print("running")
        super().run(self.config[self.bot_mode]['bot_token'], reconnect=True)

    async def on_ready(self):
        print("connected")
        self.log.info('Bot successfully logged on')

    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()    