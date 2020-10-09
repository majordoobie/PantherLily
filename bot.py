import logging

from discord.ext import commands

from packages.private.settings import Settings


class BotClient(commands.Bot):
    def __init__(self, settings: Settings):
        super().__init__(command_prefix=settings.bot_config['bot_prefix'])
        self.settings = settings
        # TODO: Set up the db connection here
        self.log = logging.getLogger('bot')

        # Set debugging mode
        self.debug = False

    def run(self):
        self.log.info('Hello ;alh;laksdhjf;ajslhd a;sldkha sd;lfhasd f')

        print("trying to connect")
        super().run(self.settings.bot_config['bot_token'], reconnect=True)

    async def on_ready(self):
        print("We in")