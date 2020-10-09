import logging

from discord import Embed, Status, Game, InvalidData
from discord.ext import commands

from packages.private.settings import Settings


class BotClient(commands.Bot):
    def __init__(self, settings: Settings):
        super().__init__(command_prefix=settings.bot_config['bot_prefix'])
        self.settings = settings
        # TODO: Set up the db connection here
        self.log = logging.getLogger('root')

        # Set debugging mode
        self.debug = False

    def run(self):
        print('Loading cogs...')
        for cog in self.settings.enabled_cogs:
            try:
                self.load_extension(cog)
            except Exception as error:
                self.log.error(error, exc_info=True)

        print('Cogs loaded, establishing connection')
        super().run(self.settings.bot_config['bot_token'], reconnect=True)

    async def on_ready(self):
        print("Connected")
        self.log.debug('Established connection')
        await self.change_presence(status=Status.online, activity=Game(name=self.settings.bot_config['version']))

    async def on_resume(self):
        self.log.info('Resuming connection...')

    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()