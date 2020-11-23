import logging

from discord import Embed
from discord.ext.commands import MemberConverter, UserConverter, NotOwner, BadArgument

class BotExt:
    INFO = 0x000080         # blued
    ERROR = 0xff0010        # red
    SUCCESS = 0x00ff00      # green
    WARNING = 0xff8000      # orange

    def __init__(self, settings):
        self.settings = settings
        self.log = logging.getLogger('root.bot_ext')

    async def embed_print(self, ctx, description, title='', color=INFO, codeblock=False, _return=False):
        if not description:
            raise BadArgument("No value to encapsulate in a embed")

        if len(description) < 1900:
            if codeblock:
                description = f'```{description}```'

            embed = Embed(
                title=title,
                description=description,
                color=color
            )
            # TODO think it looks ugly having this here come back later to decide
            embed.set_footer(text=self.settings.bot_config['version'])

            if _return:
                return embed
            else:
                await ctx.send(embed=embed)

        else:
            blocks = await self.text_splitter(description, codeblock)
            embed_list = []
            embed_list.append(Embed(
                title=f'{title}',
                description=blocks[0],
                color=color
            ))
            for i in blocks[1:]:
                embed_list.append(Embed(
                    description=i,
                    color=color
                ))
            embed_list[-1].set_footer(text=self.settings.bot_config['version'])
            if _return:
                return embed_list

            for i in embed_list:
                await ctx.send(embed=i)

    async def text_splitter(self, text, codeblock):
        '''
        Method is used to split text by 1000 character increments to avoid hitting the
        1400 character limit on discord
        '''
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > 1900:
                block = block.rstrip('\n')
                if codeblock:
                    blocks.append(f'```{block}```')
                else:
                    blocks.append(block)
                block = f'{i}\n'
            else:
                block += f'{i}\n'
        if block:
            if codeblock:
                blocks.append(f'```{block}```')
            else:
                blocks.append(block)
        return blocks

    def is_owner(self, ctx):
        if ctx.author.id == self.settings.owner:
            return True
        else:
            raise NotOwner("Please ask a developer to run this command")


    def log_role_change(self, member, role, removed=False):
        """Log roles gained and lost"""
        if removed:
            self.log.debug(f'`{member.name}` lost role `{role.name}`')
        else:
            self.log.debug(f'`{member.name}` received role `{role.name}`')