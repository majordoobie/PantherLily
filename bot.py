import logging
import sys
import traceback

from discord import Embed, Status, Game, InvalidData
from discord.errors import Forbidden
from discord.ext import commands

from packages.bot_ext import BotExt


class BotClient(commands.Bot, BotExt):
    def __init__(self, settings, pool, coc_client,  *args, **kwargs):
        super(BotClient, self).__init__(*args, **kwargs) # command_prefix

        self.settings = settings
        self.pool = pool
        self.coc_client = coc_client

        self.log = logging.getLogger('root')

        # Set debugging mode
        self.debug = False

        # load cogs
        print('Loading cogs...')
        for cog in self.settings.enabled_cogs:
            try:
                print(f'Loading {cog}')
                self.load_extension(cog)
            except Exception as e:
                print(f'Failed to load cog {cog}', file=sys.stderr)
                traceback.print_exc()
                self.log.critical(f'Failed to load cog {cog}')
        print("cogs loaded")

    async def on_ready(self):
        print("Connected")
        self.log.debug('Established connection')
        await self.change_presence(status=Status.online, activity=Game(name=self.settings.bot_config['version']))

    async def on_resume(self):
        self.log.info('Resuming connection...')

    async def on_command(self, ctx):
        await ctx.trigger_typing()
        #await ctx.message.channel.trigger_typing()

    async def on_command_error(self, ctx, error):
        if self.debug:
            exc = ''.join(
                traceback.format_exception(type(error), error, error.__traceback__, chain=True))

            await self.embed_print(ctx, title='DEBUG ENABLED', description=f'{exc}',
                                   codeblock=True, color='warning')

        # Catch all errors within command logic
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            # Catch errors such as roles not found
            if isinstance(original, InvalidData):
                await self.embed_print(ctx, title='INVALID OPERATION', color='error',
                                       description=original.args[0])
                return

            # Catch permission issues
            elif isinstance(original, Forbidden):
                await self.embed_print(ctx, title='FORBIDDEN', color='error',
                                       description='Even with proper permissions, the target user must be lower in the '
                                                   'role hierarchy of this bot.')
                return

        # Catch command.Check errors
        if isinstance(error, commands.CheckFailure):
            try:
                if error.args[0] == 'Not owner':
                    await self.embed_print(ctx, title='COMMAND FORBIDDEN', color='error',
                                           description='Only Doobie can run this command')
                    return
            except:
                pass
            await self.embed_print(ctx, title='COMMAND FORBIDDEN', color='error',
                                   description='Only `CoC Leadership` are permitted to use this command')
            return

        # Catch all
        err = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))

        await self.embed_print(ctx, title='COMMAND ERROR',
                               description=err, color='error')
