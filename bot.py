from discord.ext import commands


class BotClient(commands.Bot):
    def __init__(self, settings):
        super().__init__(command_prefix=settings.bot_config['bot_prefix'])
        self.settings = settings

    def run(self):
        super().run(self.settings.bot_config['bot_token'],
                    reconnect=True)

    async def on_ready(self):
        print("We in")