from disnake.ext import commands
import logging
import traceback

from packages.utils.paginator import Paginator
from packages.utils.utils import *
from bot import BotClient


class Administrator(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Administrator')

    @commands.slash_command(
        name="help",
        auto_sync=True
    )
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        admin_embed = disnake.Embed(
            title="Admin Commands",
            color=EmbedColor.INFO.value
        )

        admin_embed.add_field("/add",
                              "Add a new user to PantherLily",
                              inline=False)

        admin_embed.add_field("/remove",
                              "Disable a user from PantherLily. Their "
                              "records will be saved but their stats "
                              "tracking will be paused",
                              inline=False)

        admin_embed.add_field("/view",
                              "View a users current enrollment status with "
                              "the option of viewing a users records. A "
                              "record is added each time a user is enabled "
                              "or disabled with the \"kick message\".",
                              inline=False)

        admin_embed.add_field("/report",
                              "View an overall summary of the clans "
                              "donation progress for the week with the "
                              "option of requesting more weeks.",
                              inline=False)

        admin_embed.add_field("/del_coc",
                              "Clash tags are uniquely linked to one discord "
                              "account. If a user wants to switch their "
                              "discord account then you must use this "
                              "command to disassociate the clash tag with "
                              "the old discord account before adding them. "
                              "Failing to do so will result in an error "
                              "when enrolling them. This is no problem, the "
                              "error will let you know to use this command.",
                              inline=False)

        user_embed = disnake.Embed(
            title="User Commands",
            color=EmbedColor.INFO.value
        )

        user_embed.add_field("/donation",
                             "View your current donation progress for the "
                             "week. An optional argument to check another "
                             "user is a is also supported",
                             inline=False)

        user_embed.add_field("/stats",
                             "View the users Clash of Clans stats with the "
                             "option of also viewing other users. The "
                             "response also provides two buttons. One for "
                             "the Clash Of Stats website and another to "
                             "open the users account in game.",
                             inline=False)

        user_embed.add_field("/roster",
                             "Overall view of the users in the clan. The "
                             "output will also show users that are in the "
                             "clan but not registered. The output also has "
                             "the ability to show the current location of "
                             "all users",
                             inline=False)

        user_embed.add_field("/top",
                             "Show the top donors and top trophy gains "
                             "for the week.",
                             inline=False)

        view = Paginator([user_embed, admin_embed], 1)
        await inter.send(embeds=view.embed, view=view)
        view.message = await inter.original_message()










    @commands.command(
        alias='bot_roles',
        brief='',
        description = 'Display the roles needed for Panther Lily to work',
        usage='',
        help='The provided text are all the roles required for this bot to work.'
    )

    async def panther_roles(self, ctx):
        roles_required = {
            'manage_roles': 'Needed to add roles to users',
            'manage_nicknames': 'Needed to update user nicknames to match their clash accounts',
            'create_invite': 'Needed to create secure invite links that expire',
            'manage_webhooks': 'Needed to establish a logging channel',
            'read text channels': 'To see channel contents',
            'manage_massages': 'Ability to remove own messages and add reactions',
            'embed_links': 'Ability to create embeds',
            'attach_files': 'Ability to display rosters in other file formats',
            'read_message_history': 'See far back into a channels text messages',
            'use_external_emojis': 'Use own stored emojis',
            'add_reaction': 'Ability to add reaction to messages'
        }
        frame = ''
        for k, v in roles_required.items():
            frame += f'`{k}`\n{v}\n\n'
        await self.bot.send(ctx, frame)

    @commands.check(is_owner)
    @commands.command(
        aliases=['kill', 'k'],
        brief = '',
        description = 'Turn bot off',
        usage = '',
        help = ''
    )
    async def _logout(self, ctx):
        self.log.error('Closing connections...')
        await self.bot.send(ctx, "Logging off")
        try:
            await self.bot.coc_client.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.pool.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

    @commands.check(is_owner)
    @commands.command(
        aliases=['load'],
        hidden=True
    )
    async def load_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Loaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(
        aliases=['unload'],
        hidden = True
    )
    async def unload_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Unloaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(
        hidden=True,
        aliases=['r'],
    )
    async def re_load(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'

        try:
            self.bot.reload_extension(cog)
        except Exception as error:
            exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
            await ctx.send(exc)
            return
        msg = f"""```python\nReloaded '{cog}' successfully```"""
        await ctx.send(msg)

    @commands.check(is_owner)
    @commands.command(
        hidden=True
    )
    async def list_cogs(self, ctx):
        output = ''
        for i in self.bot.settings.enabled_cogs:
            output += i.split('.')[-1] + '\n'
        await ctx.send(output)

def setup(bot):
    bot.add_cog(Administrator(bot))
