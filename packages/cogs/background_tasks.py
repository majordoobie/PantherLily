import logging

import traceback
from discord import Member
from discord.ext import commands, tasks

from bot import BotClient
from packages.cogs.utils.bot_sql import sql_select_all_active_users
from packages.cogs.utils.utils import get_default_roles


class BackgroundTasks(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('PantherBot.BackgroundTasks')
        self.sync_clash_discord.start()

    def cog_unload(self):
        self.sync_clash_discord.cancel()

    @tasks.loop(seconds=600)
    async def sync_clash_discord(self):
        self.log.debug('Starting discord loop')
        async with self.bot.pool.acquire() as conn:
            active_users = await conn.fetch(sql_select_all_active_users())

        for user in active_users:
            member: Member
            # TODO: Add guild to a key somewhere else to support multiple guilds
            guild = self.bot.get_guild(293943534028062721)
            member = guild.get_member(user['discord_id'])
            if not member:
                self.log.error(f'Unable to retrieve member object for {user["discord_id"]}')
                continue

            # if member.id == 265368254761926667:
            #     print(member.display_name)
            #     print(user['clash_name'])
            #     rs = member.roles
            #     for role in rs:
            #         if role.id == 653562690937159683:
            #             rs.pop(rs.index(role))
            #     print(rs)
            #     rs.append(member.guild.get_role(455572149277687809))
            #     await member.edit(roles=rs)
            #     print('removed roles')

            if member.display_name != user['clash_name']:
                try:
                    old_name = member.display_name
                    await member.edit(nick=user['clash_name'], reason='Panther Bot Background Sync')
                    self.log.info(f'Changed `{old_name}` name to `{user["clash_name"]}`')
                except Exception as error:
                    self.log.error(error, exc_info=True)

            users_town_hall_role = self.bot.settings.default_roles.get(f"th{user['town_hall']}s")
            if users_town_hall_role not in (role.id for role in member.roles):
                self.log.debug(f'{member.display_name} does not contain the role th{user["town_hall"]}s - updating')
                member_roles = member.roles

                for role in member_roles:
                    if role.id == self.bot.settings.default_roles.get('CoC Members'):
                        continue
                    if role.id in self.bot.settings.default_roles.values():
                        member_roles.pop(member_roles.index(role))

                default_roles = get_default_roles(member.guild, self.bot.settings, user['town_hall'])
                default_roles = default_roles[0]
                member_roles.append(default_roles)
                if default_roles:
                    try:
                        await member.edit(roles=member_roles, reason="Panther Bot Background Sync")
                        self.bot.log_role_change(member, member_roles, log=self.log)
                    except Exception as error:
                        self.log.error(error, exc_info=True)

    @sync_clash_discord.before_loop
    async def before_sync_clash_discord(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BackgroundTasks(bot))
