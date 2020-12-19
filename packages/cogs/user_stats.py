from datetime import datetime
from discord.ext import commands
import logging

from bot import BotClient
from .utils.utils import get_utc_monday, get_discord_member

class UserStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('PantherBot.UserStats')

    @commands.command()
    async def donation(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `donation`')

        if arg_string:
            pass
        else:
            member = get_discord_member(ctx, ctx.author.id)

        start_date = get_utc_monday()
        end_date = datetime.utcnow()





def setup(bot):
    bot.add_cog(UserStats(bot))