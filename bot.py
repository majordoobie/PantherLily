import logging
import traceback
from typing import Any

import coc
import disnake
from asyncpg.pool import Pool
from disnake import Game, InvalidData, Status
from disnake.errors import Forbidden
from disnake.ext import commands

from packages.bot_ext import BotExt
from packages.utils.bot_sql import sql_create_tables
from packages.private.settings import Settings
from packages.utils.utils import EmbedColor


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

        self.log = logging.getLogger(f"{self.settings.log_name}.BotClient")

        # Set debugging mode
        self.debug = False

        # load cogs
        print("Loading cogs...")
        for cog in self.settings.enabled_cogs:
            try:
                print(f"Loading {cog}")
                self.log.debug(f"Loading {cog}")
                self.load_extension(cog)
            except Exception as error:
                print(f"Failed to load cog {cog}\n{error}")
                self.log.critical(f"Failed to load cog {cog}", exc_info=True)

        if self.settings.bot_mode == "dev_mode":
            self.load_extension("packages.cogs.tester")

        print("cogs loaded")

    async def on_ready(self):
        print("Connected")
        self.log.debug("Established connection")

        # create tables if they do no exit
        async with self.pool.acquire() as con:
            for sql_table in sql_create_tables():
                await con.execute(sql_table)

    async def on_resume(self):
        self.log.info("Resuming connection...")

    async def on_slash_command(self,
                               inter: disnake.ApplicationCommandInteraction
                               ) -> None:
        """
        Function logs all the commands made by the users

        :param inter: disnake.ApplicationCommandInteraction
        :return:
        """

        space = 0
        if inter.options:
            space = max(len(option) + 1 for option in inter.options.keys())

        if space < 9:
            space = 9  # Length of the 'Command: ' key

        name = f"{inter.author.name}#{inter.author.discriminator}"
        msg = (
            f"{'User:':<{space}} {name}\n"
            f"{'Command:':<{space}} {inter.data.name}\n"
        )

        for option, data in inter.options.items():
            option = f"{option}:"

            if isinstance(data, disnake.Member):
                data: disnake.Member
                name = f"{data.name}#{data.discriminator}"
                msg += f"{option:<{space}} {name}\n"
            else:
                msg += f"{option:<{space}} {data}\n"

        self.log.warning(f"```{msg}```")

    async def on_slash_command_error(
            self,
            inter: disnake.ApplicationCommandInteraction,
            error: commands.CommandError
    ) -> None:
        """
        Log all errors made by slash commands

        :param inter: disnake.ApplicationCommandInteraction
        :return:
        """
        print("Did I get an error")

        if self.debug:
            exc = "".join(
                traceback.format_exception(type(error), error,
                                           error.__traceback__, chain=True))

            await self.inter_send(inter, panel=f"{exc}", title="DEBUG ENABLED",
                                  color=EmbedColor.WARNING, code_block=True)

        # Catch all errors within command logic
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            # Catch errors such as roles not found
            if isinstance(original, InvalidData):
                await self.inter_send(inter, panel=original.args[0],
                                      title="INVALID OPERATION",
                                      color=EmbedColor.ERROR)
                return

            # Catch permission issues
            elif isinstance(original, Forbidden):
                await self.inter_send(inter,
                                      panel="Even with proper permissions, the "
                                            "target user must be lower in the "
                                            "role hierarchy of this bot.",
                                      title="FORBIDDEN",
                                      color=EmbedColor.ERROR)
                return

            else:
                err = "".join(traceback.format_exception(type(error), error,
                                                         error.__traceback__,
                                                         chain=True))
                await self.inter_send(inter,
                                      panel=err,
                                      title="UNKNOWN - Have doobie check the "
                                            "logs",
                                      color=EmbedColor.ERROR)

                self.log.error(err, exc_info=True)
                return


        # Catch command.Check errors
        if isinstance(error, commands.CheckFailure):
            try:
                if error.args[0] == "Not owner":
                    await self.inter_send(inter, panel="Only doobie can run "
                                                       "this command",
                                          title="COMMAND FORBIDDEN",
                                          color=EmbedColor.ERROR)
                    return
            except:
                pass
            await self.inter_send(inter,
                                  panel="Only `CoC Leadership` are permitted "
                                        "to use this command",
                                  title="COMMAND FORBIDDEN",
                                  color=EmbedColor.ERROR)
            return

        # Catch all
        err = "".join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        title = error.__class__.__name__
        if title is None:
            title = "Command Error"
        await self.inter_send(inter, panel=str(error), title=title,
                              color=EmbedColor.ERROR)

        self.log.error(err, exc_info=True)
