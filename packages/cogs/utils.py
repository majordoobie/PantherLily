import discord
from discord import Embed

EMBED_COLORS = {
    'blue' : 0x000080
}
async def embed_print(ctx, title=None, description=None, color='blue'):
    '''
    Function used to print embeds to discord
    '''
    if len(description) < 1000:
        embed = Embed(
            title=title,
            description=description,
            color=EMBED_COLORS[color]
        )
        await ctx.send(embed=embed)
    



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