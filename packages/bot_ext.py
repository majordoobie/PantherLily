import logging
from logging import Logger
from typing import Union, List, Optional

import disnake
from disnake.ext.commands import Context, NotOwner, BadArgument


class BotExt:
    INFO = 0x000080  # blued
    ERROR = 0xff0010  # red
    SUCCESS = 0x00ff00  # green
    WARNING = 0xff8000  # orange

    def __init__(self, settings):
        self.settings = settings
        self.log = logging.getLogger('root.bot_ext')

    async def send(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            description,
            title='',
            color=INFO,
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
            color=color
        )]
        for i in blocks[1:]:
            embed_list.append(disnake.Embed(
                description=i,
                color=color
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

    @staticmethod
    async def text_splitter(text: str, code_block: bool) -> list:
        """Split text into blocks and return a list of blocks"""
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > 1800:
                block = block.rstrip('\n')
                if code_block:
                    print("got it ")
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
