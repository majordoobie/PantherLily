from discord.ext import commands
from discord import Embed

EMBED_COLORS = {
    'blue' : 0x000080
    }

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def embed_print(self, ctx, title=None, description=None, color='blue'):
        '''
        Method is used to standarize how text is displayed to discord
        '''
        if len(description) < 1000:
            embed = Embed(
                title=title,
                description=description,
                color=EMBED_COLORS[color]
            )
            embed.set_footer(text=self.bot.config[self.bot.bot_mode]['version'])
            await ctx.send(embed=embed)
        else:
            blocks = await self.text_splitter(description)
            embeds = []
            embeds.append(Embed(
                title=title,
                description=blocks[0],
                color=EMBED_COLORS[color]
            ))
            for i in blocks[1:]:
                embeds.append(Embed(
                    description=i,
                    color=EMBED_COLORS[color]
                ))
            embeds[-1].set_footer(text=self.bot.config[self.bot.bot_mode]['version'])
            for i in embeds:
                await ctx.send(embed=i)

    async def text_splitter(self, text):
        '''
        Method is used to split text by 1000 character increments to avoid hitting the
        1400 character limit on discord
        '''
        blocks = [] 
        block = '' 
        for i in text.split('\n'): 
            if (len(i) + len(block)) > 1000: 
                block = block.rstrip('\n')
                blocks.append(block) 
                block = f'{i}\n'
            else: 
                block += f'{i}\n' 
        if block: 
            blocks.append(block) 
        return blocks


def setup(bot):
    bot.add_cog(Utils(bot))

# EMBED_COLORS = {
#     'blue' : 0x000080
# }
# async def embed_print(ctx, title=None, description=None, color='blue'):
#     '''
#     Function used to print embeds to discord
#     '''
#     if len(description) < 1000:
#         embed = Embed(
#             title=title,
#             description=description,
#             color=EMBED_COLORS[color]
#         )
#         await ctx.send(embed=embed)
    



#    async def embed(self, title= EmptyEmbed,
#               author = EmptyEmbed,
#               description = EmptyEmbed,
#               fields = None,
#               footer = EmptyEmbed,
#               color = None,
#               url = EmptyEmbed,
#               icon_url = EmptyEmbed,
#               footer_icon_url = EmptyEmbed,
#               thumbnail = None,
#               image = None,
#               timestamp = EmptyEmbed,
#               send = False,
#               channel=None):
#         embed = discord.Embed(title = title,
#                               description = description,
#                               timestamp = timestamp,
#                               color = getattr(color, 'value', EmptyEmbed) and color)
#         if author:
#             embed.set_author(name=title, url=url, icon_url=icon_url)
#         if fields:
#             for field in fields:
#                 name, value = field[:2]
#                 embed.add_field(name = name,
#                                 value = value,
#                                 inline = get(field, 2, default=True))
#         if thumbnail:
#             embed.set_thumbnail(url=thumbnail)
#         if image:
#             embed.set_image(url=image)
#         if footer:
#             embed.set_footer(text=footer, icon_url=footer_icon_url)

#         if send:
#             channel = channel or self
#             return await channel.send(embed=embed)
#         return embed