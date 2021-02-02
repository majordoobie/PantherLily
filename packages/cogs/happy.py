from discord.ext import commands
import logging

from bot import BotClient
from packages.cogs.utils.utils import parse_args

EMOJI_REACTIONS = (
    'rcs1',
    'rcs2',
    'rcs3',
    'rcs4',
    'rcs5',
    'rcs6',
    'rcs7',
    'rcs8',
    'rcs9',
    'rcs10',
    'stop',
    'topoff2',
    'super_troop',
)
class Happy(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Happy')
        self.emojis = {emoji: self.bot.settings.emojis[emoji] for emoji in EMOJI_REACTIONS}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

    @commands.group(
        aliases=['h'],
        invoke_without_command=True,
        brief='',
        description='Create and View interactive panels to volunteer for zones to donate to for war preparations.',
        usage='',
        help=''
    )
    async def happy(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy",
                                   args=args,
                                   arg_string=arg_string)

        msg = f'Welcome to the Happy module! To see what I can do, run `panther.help Happy`'
        await self.bot.embed_print(ctx, msg)

        msg = ''
        for k,v in self.emojis.items():
            if len(msg)>1800:
                await ctx.send(msg)
                msg = ''
            msg += f'{k} {v}'
        await ctx.send(msg)
        msg = ''
        #
        # for emoji in self.bot.emojis:
        #     if len(msg)>1800:
        #         await ctx.send(msg)
        #         msg = ''
        #     msg += f'{emoji} {emoji.name} {emoji.id}\n'
        # await ctx.send(msg)



    @happy.command(
        name='list',
        aliases=['l'],
        brief='',
        help=''
    )
    async def list_panels(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy list",
                                   args=args,
                                   arg_string=arg_string)

        await ctx.send("Hitting view")


def setup(bot):
    bot.add_cog(Happy(bot))