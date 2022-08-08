import logging
from logging import Logger
from typing import Union, List, Optional

import disnake
from disnake.ext.commands import Context, NotOwner, BadArgument

from packages.utils.utils import EmbedColor


class BotExt:

    # limits
    EMBED_TITLE = 256
    EMBED_DESCRIPTION = 4096
    EMBED_FOOTER = 2048
    EMBED_AUTHOR = 256
    EMBED_TOTAL = 6000

    def __init__(self, settings):
        self.settings = settings
        self.log = logging.getLogger('root.bot_ext')

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
            raise BadArgument("No value to encapsulate in a embed")

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
                         inter: disnake.ApplicationCommandInteraction,
                         panel: str = "",
                         panels: List[str] = [],
                         title: str = "",
                         color: EmbedColor = EmbedColor.INFO,
                         code_block: bool = False,
                         footer: str = "",
                         author: disnake.Member = None
                         ):
        """
        Limits:

        :param panel:
        :param author:
        :param footer:
        :param code_block:
        :param color:
        :param title:
        :param inter:
        :param panels:
        :return:
        """
        total_panels = []

        if panel:
            total_panels.append(panel)

        for panel in panels:
            for sub_panel in await self.text_splitter(panel, code_block):
                total_panels.append(sub_panel)

        last = len(total_panels)
        total_embeds = []
        embeds = []
        author_set = False
        for index, panel in enumerate(total_panels):
            embed = disnake.Embed(
                description=panel,
                color=color.value,
                title=title if index == 0 else ""
            )

            if index == 0:
                if author and not author_set:
                    author_set = True
                    embed.set_author(
                        name=author.display_name,
                        icon_url=author.avatar.url
                    )

            if index == last - 1:
                if footer != "":
                    embed.set_footer(text=footer)

            # If the current embed is going to make the embeds block exceed
            # to send size, then create a new embed block
            embeds_size = sum(len(embed) for embed in embeds)
            if embeds_size + len(embed) > BotExt.EMBED_TOTAL:
                total_embeds.append(embeds.copy())
                embeds = []

            embeds.append(embed)

        if embeds:
            total_embeds.append(embeds)

        for embeds in total_embeds:
            await inter.send(embeds=embeds)




    @staticmethod
    async def text_splitter(text: str, code_block: bool) -> list[str]:
        """Split text into blocks and return a list of blocks"""
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > BotExt.EMBED_DESCRIPTION:
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
            raise NotOwner("Please ask a developer to run this command")

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
        if isinstance(role, Role):
            msg = 'lost role' if removed else 'received role'
            log.info(f'`{member.display_name}` {msg} `{role.name}`')

        else:
            msg = 'lost role' if removed else 'received role'
            for _role in role:
                log.info(f'`{member.display_name}` {msg} `{_role.name}`')

    @staticmethod
    def log_user_commands(log: Logger, **kwargs) -> None:
        """
        Centralized command line logging

        Parameters
        ----------
        log: Logger
            Logger root used for the cog
        kwargs
            user=ctx.author.display_name,
            command="donation",
            args=None,
            arg_string=arg_string

        Returns
        -------
        None
        """
        #TODO: Fix me
        msg = f'''
```
User:        {kwargs["user"]}               
Executed:    {kwargs["command"]}
```

'''
        log.warning(msg)
