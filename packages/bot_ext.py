from discord import Embed
from discord.ext.commands import MemberConverter, UserConverter, NotOwner, BadArgument

EMBED_COLORS = {
    'info': 0x000080,  # blue
    'error': 0xff0010,  # red
    'success': 0x00ff00,  # green
    'warning': 0xFFFF00  # yellow
}


class BotExt:
    def __init__(self, settings):
        self.settings = settings

    async def embed_print(self, ctx, description, title='', color='info', codeblock=False, _return=False):
        if not description:
            raise BadArgument("No value to encapsulate in a embed")

        if len(description) < 1900:
            if codeblock:
                description = f'```{description}```'

            embed = Embed(
                title=title,
                description=description,
                color=EMBED_COLORS[color]
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
                color=EMBED_COLORS[color]
            ))
            for i in blocks[1:]:
                embed_list.append(Embed(
                    description=i,
                    color=EMBED_COLORS[color]
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

