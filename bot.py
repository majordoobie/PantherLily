import logging
import traceback
from logging import Logger
from typing import List, Optional, Union

import asyncpg
import disnake
from disnake.errors import Forbidden
from disnake.ext import commands

import coc
import packages.utils.bot_sql as sql
from packages.private.settings import Settings
from packages.utils.utils import EmbedColor


class BotClient(disnake.ext.commands.Bot):
    # limits
    EMBED_TITLE = 256
    EMBED_DESCRIPTION = 4096
    EMBED_FOOTER = 2048
    EMBED_AUTHOR = 256
    EMBED_TOTAL = 6000
    EMBED_SEND_TOTAL = 10

    def __init__(self, settings: Settings, pool: asyncpg.Pool, coc_client: coc.Client, *args, **kwargs):
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
        self.space = "\u00A0"

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
            for sql_table in sql.create_tables():
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

        :param error:
        :param inter: disnake.ApplicationCommandInteraction
        :return:
        """
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
            if isinstance(original, disnake.InvalidData):
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
                embeds = await self.inter_send(inter,
                                               panel=err,
                                               title="UNKNOWN - Have doobie check the "
                                                     "logs",
                                               color=EmbedColor.ERROR,
                                               return_embed=True
                                               )
                for embed_group in embeds:
                    await inter.send(embeds=embed_group)

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

    async def send(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            description,
            title='',
            color: EmbedColor = EmbedColor.INFO,
            code_block=False,
            _return=False,
            footnote=True,
            author: Union[list, None] = None) -> Optional[list]:
        if not description:
            raise commands.BadArgument("No value to encapsulate in a embed")

        blocks = await self.text_splitter(description, code_block)
        embed_list = [disnake.Embed(
            title=f'{title}',
            description=blocks[0],
            color=color.value
        )]
        for i in blocks[1:]:
            embed_list.append(disnake.Embed(
                description=i,
                color=color.value
            ))
        if footnote:
            embed_list[-1].set_footer(text=self.settings.bot_config['version'])
        if author:
            embed_list[0].set_author(name=author[0], icon_url=author[1])

        if _return:
            return embed_list

        else:
            for i in embed_list:
                await ctx.send(embed=i)
        return

    async def inter_send(self,
                         inter: Union[disnake.ApplicationCommandInteraction, disnake.MessageInteraction, None],
                         panel: str = "",
                         panels: List[str] = [],
                         title: str = "",
                         color: EmbedColor = EmbedColor.INFO,
                         code_block: bool = False,
                         footer: str = "",
                         author: disnake.Member = None,
                         view: disnake.ui.View = None,
                         return_embed: bool = False,
                         flatten_list: bool = False
                         ) -> Union[list[disnake.Embed], list[list[disnake.Embed]]]:
        """
        Wrapper function to print embeds

        :param flatten_list: If a single list of embeds should be returned
        :param return_embed: If the embed should be returned instead of printing
        :param view: Optional view to submit
        :param panel: Text to send
        :param author: Optional author to send
        :param footer: Optional footer to use
        :param code_block: If the text should be in a code block
        :param color: Color to use for the embed
        :param title: The optional title of the embed
        :param inter: The Interaction object
        :param panels: Optional list of panels to send
        """
        total_panels = []

        if panel:
            total_panels.append(panel)

        for panel in panels:
            for sub_panel in await self.text_splitter(panel, code_block):
                total_panels.append(sub_panel)

        last_index = len(total_panels) - 1
        total_embeds = []
        embeds = []
        author_set = False
        for index, panel in enumerate(total_panels):
            embed = disnake.Embed(
                description=panel,
                color=color.value,
                title=title if index == 0 else "",
            )

            if index == 0:
                if author and not author_set:
                    author_set = True
                    embed.set_author(
                        name=author.display_name,
                        icon_url=author.avatar.url
                    )

            if index == last_index:
                if footer != "":
                    embed.set_footer(text=footer)

            # If the current embed is going to make the embeds block exceed
            # to send size, then create a new embed block
            embeds_size = sum(len(embed) for embed in embeds)
            if len(embeds) == BotClient.EMBED_SEND_TOTAL:
                total_embeds.append(embeds.copy())
                embeds = []

            if embeds_size + len(embed) > BotClient.EMBED_TOTAL:
                total_embeds.append(embeds.copy())
                embeds = []

            embeds.append(embed)

        if embeds:
            total_embeds.append(embeds)

        if return_embed:
            if flatten_list:
                return [embed for embed_list in total_embeds for embed in embed_list]
            return total_embeds

        if hasattr(inter, "response"):
            send_func = inter.response.send_message
        else:
            send_func = inter.send

        last_embed = len(total_embeds) - 1
        for index, embeds in enumerate(total_embeds):
            if last_embed == index and view:
                await send_func(embeds=embeds, view=view)
            else:
                await send_func(embeds=embeds)

    @staticmethod
    async def text_splitter(text: str, code_block: bool) -> list[str]:
        """Split text into blocks and return a list of blocks"""
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > BotClient.EMBED_DESCRIPTION:
                block = block.rstrip('\n')
                if code_block:
                    blocks.append(f'```{block}```')
                else:
                    blocks.append(block)
                block = f'{i}\n'
            else:
                block += f'{i}\n'
        if block:
            if code_block:
                blocks.append(f'```{block}```')
            else:
                blocks.append(block)
        return blocks

    def is_owner(self, ctx):
        if ctx.author.id == self.settings.owner:
            return True
        else:
            raise commands.NotOwner("Please ask a developer to run this command")

    @staticmethod
    def log_role_change(
            member: disnake.Member,
            role: Union[List[disnake.Role], disnake.Role],
            log: Logger,
            removed: bool = False) -> None:
        """
        Simple centralized place to log role changes. The input will either be a list of roles or
        a single role
        Parameters
        ----------
        member: Member
            Member whose role has changed
        role: Role
            Role or roles that have changed
        log: Logger
            Logger root to log to
        removed: bool
            Bool stating if the role or roles have been removed

        Returns
        -------
        None
        """
        if isinstance(role, disnake.Role):
            msg = 'lost role' if removed else 'received role'
            log.info(f'`{member.display_name}` {msg} `{role.name}`')

        else:
            msg = 'lost role' if removed else 'received role'
            for _role in role:
                log.info(f'`{member.display_name}` {msg} `{_role.name}`')

