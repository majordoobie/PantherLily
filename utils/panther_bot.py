# Built-in
import asyncio
import logging

# Non-built ins
from discord.ext import commands

class PantherLily(commands.Bot):
    def __init__(self, config):
        super().__init__(command_prefix='? ')
        self.config = config
        self.log = logging.getLogger('root.PantherLily')

    def run(self):
        print("running")
        super().run(self.config['devBot']['bot_token'], reconnect=True)

    async def on_ready(self):
        print("connected")
        self.log.info('In here bois')