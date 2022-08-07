import logging
import traceback
from typing import Any

import coc
from asyncpg.pool import Pool
from disnake import Game, InvalidData, Status
from disnake.errors import Forbidden
from disnake.ext import commands

from packages.bot_ext import BotExt
from packages.utils.bot_sql import sql_create_tables
from packages.private.settings import Settings


class BotClient(commands.Bot, BotExt):
    def __init__(self, settings: Settings, pool: Pool, coc_client: coc.Client, *args, **kwargs):
        """
        Inherits the Discord.py bot to create a bot that manages a group of clash of clans players

        Parameters
        ----------
        settings: Settings
            Configuration settings based on the bot mode
        pool: Pool
            Asyncpg connection pool object
        coc_client: EventsClient
            Authenticated connection wrapper for Clash of Clans API
        """
        super(BotClient, self).__init__(*args, **kwargs)  # command_prefix

        self.settings = settings
        self.pool = pool
        self.coc_client = coc_client

        self.log = logging.getLogger(f'{self.settings.log_name}.BotClient')

        # Set debugging mode
        self.debug = False

        # load cogs
        print('Loading cogs...')
        for cog in self.settings.enabled_cogs:
            try:
                print(f'Loading {cog}')
                self.log.debug(f'Loading {cog}')
                self.load_extension(cog)
            except Exception as error:
                print(f'Failed to load cog {cog}\n{error}')
                self.log.critical(f'Failed to load cog {cog}', exc_info=True)

        print("cogs loaded")

    async def on_ready(self):
        print("Connected")
        self.log.debug('Established connection')

        #TODO: Move this to the bot building area
        await self.change_presence(status=Status.online, activity=Game(name=self.settings.bot_config['version']))

        # create tables if they do no exit
        async with self.pool.acquire() as con:
            for sql_table in sql_create_tables():
                await con.execute(sql_table)

    async def on_resume(self):
        self.log.info('Resuming connection...')

    async def on_command(self, ctx):
        await ctx.trigger_typing()

    async def on_error(self,
                       event_method: str,
                       *args: Any,
                       **kwargs: Any) -> None:
        print("Where you here??")
        return

        if self.debug:
            exc = ''.join(
                traceback.format_exception(type(error), error, error.__traceback__, chain=True))

            await self.send(ctx, title='DEBUG ENABLED', description=f'{exc}', code_block=True, color=self.WARNING)

        # Catch all errors within command logic
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            # Catch errors such as roles not found
            if isinstance(original, InvalidData):
                await self.send(ctx, title='INVALID OPERATION', color=self.ERROR,
                                description=original.args[0])
                return

            # Catch permission issues
            elif isinstance(original, Forbidden):
                await self.send(ctx, title='FORBIDDEN', color=self.ERROR,
                                description='Even with proper permissions, the target user must be lower in the '
                                            'role hierarchy of this bot.')
                return

            else:
                err = ''.join(traceback.format_exception(type(error), error,
                                                         error.__traceback__,
                                                         chain=True))
                await self.send(
                    ctx,
                    title='UNKNOWN - Have doobie check the logs',
                    color=self.ERROR,
                    description=str(error))

                self.log.error(err, exc_info=True)
                return



        # Catch command.Check errors
        if isinstance(error, commands.CheckFailure):
            try:
                if error.args[0] == 'Not owner':
                    await self.send(ctx, title='COMMAND FORBIDDEN', color=self.ERROR,
                                    description='Only Doobie can run this command')
                    return
            except:
                pass
            await self.send(ctx, title='COMMAND FORBIDDEN', color=self.ERROR,
                            description='Only `CoC Leadership` are permitted to use this command')
            return

        # Catch all
        err = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        title = error.__class__.__name__
        if title is None:
            title = 'Command Error'
        await self.send(ctx, title=title, description=str(error), color=self.ERROR)
        self.log.error(err, exc_info=True)
