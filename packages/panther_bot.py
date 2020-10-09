# Built-in
import asyncio
import logging
import traceback

# Non-built ins
from discord import Embed
from discord.ext import commands

COG_PATH = 'packages.cogs.'
COG_TUPLE = (
    'packages.cogs.administrator',
    'packages.cogs.tester',
    'packages.cogs.rolemanager',
    'packages.cogs.utils'
    )
EMBED_COLORS = {
    'blue' : 0x000080
    }
class PantherLily(commands.Bot):
    __slots__ = ('config', 'bot_mode', 'log')
    def __init__(self, config, bot_mode):
        self.config = config
        self.bot_mode = bot_mode
        self.cog_tupe = COG_TUPLE
        self.cog_path = COG_PATH
        super().__init__(command_prefix=self.config[self.bot_mode]['bot_prefix'])
        self.log = logging.getLogger('root.PantherLily')

    def run(self):
        print("Loading cogs...")
        for extension in COG_TUPLE:
            try:
                self.load_extension(extension)
            except Exception:
                print(f'Failed to load extension {extension}')
                self.log.error(traceback.print_exc())

        print('Cogs loaded - establishing connection...')
        super().run(self.config[self.bot_mode]['bot_token'], reconnect=True)
    
    # Connections
    async def on_resumed(self):
        self.log.info('Resumed connection from lost connection')

    async def on_ready(self):
        print("connected")
        self.log.info('Bot successfully logged on')

    # Commands
    async def on_command(self, ctx):
        await ctx.message.channel.trigger_typing()
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, commands.errors.ExtensionNotFound):
                print("Extension not found brah")

            elif isinstance(original, commands.errors.CommandNotFound):
                print('BROOO')

    async def on_error(self, ctx, error):
        await ctx.send("```py\n{}: {}\n```".format(type(error).__name__, str(error)))


    
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
            embed.set_footer(text=self.config[self.bot_mode]['version'])
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
            embeds[-1].set_footer(text=self.config[self.bot_mode]['version'])
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

