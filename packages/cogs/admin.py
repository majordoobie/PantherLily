from discord.ext import commands
import logging

from packages.cogs.utils.utils import *
from bot import BotClient
from packages.database_schema import drop_tables


class Administrator(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Administrator')

    @commands.command(alias='bot_roles')
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

    @commands.check(is_owner)
    @commands.command(aliases=['kill', 'k'])
    async def _logout(self, ctx):
        self.log.info('Closing connections...')
        await self.bot.embed_print(ctx, "Logging off")
        try:
            await self.bot.coc_client.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.pool.close()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

        try:
            await self.bot.logout()
        except Exception as error:
            self.log.critical("Could not close coc connection", exc_info=True)

    @commands.check(is_owner)
    @commands.command(aliases=['load'])
    async def load_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Loaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(aliases=['unload'])
    async def unload_cog(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Unloaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command(aliases=['re'])
    async def re_load(self, ctx, cog: str):
        cog = f'{self.bot.settings.cog_path}.{cog}'

        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        await ctx.send(f'Reloaded {cog} successfully')

    @commands.check(is_owner)
    @commands.command()
    async def list_cogs(self, ctx):
        output = ''
        for i in self.bot.settings.enabled_cogs:
            output += i.split('.')[-1] + '\n'
        await ctx.send(output)

    @commands.check(is_owner)
    @commands.command()
    async def migrate_db(self, ctx):
        from database.migration import RecordObject, NoteObject, migrate_user
        import sqlite3
        db_file = 'database/livedatabase.db'
        db = sqlite3.connect(db_file)
        cur = db.cursor()
        cur.execute('select * from MembersTable;')
        all_data = cur.fetchall()
        cur.close()
        db.close()
        db_objects = []
        for record in all_data:
            user_id = record[4]
            try:
                member = await get_discord_member(ctx, user_id)
                print(member.name)
            except:
                print("was not able to find " + record[1])
            #migrate_user(RecordObject(record))
            db_objects.append(RecordObject(record))

        print(db_objects)



def setup(bot):
    bot.add_cog(Administrator(bot))
