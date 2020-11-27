from discord.ext import commands
import logging

from bot import BotClient

class GroupStats(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.GroupStats')

    @commands.command()
    async def roster(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `roster`')

        # Get all users with the member role
        coc_members = []
        for member in ctx.guild.members:
            if 'CoC Members' in (role.name for role in member.roles):
                coc_members.append(member)

        # sort list of member objects by lower chars
        coc_members.sort(key=lambda x: x.display_name.lower())

        # Create legend to display
        clan = self.bot.settings.emojis["reddit_zulu"]
        db = self.bot.settings.emojis["database"]
        discord = self.bot.settings.emojis["zulu_server"]
        waze = self.bot.settings.emojis["waze"]

        legend = f'{clan} Member is in Reddit Zulu in-game.\n'
        legend += f'{db} Member is registered with Pantherlily.\n'
        legend += f'{discord} Member is Reddit Zulu Discord server.\n'
        legend += f'{waze} Get realtime location of members.\n'

        await self.bot.embed_print(ctx, legend)

        # Populate the roster dictionary
        roster = {"total": 0}

        #TODO: Stop for now we need to populate clash_account for this to work









def setup(bot):
    bot.add_cog(GroupStats(bot))