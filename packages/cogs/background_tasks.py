import logging
from random import choice

import asyncpg
import disnake
from disnake import Activity, ActivityType, Game, Member, Status
from disnake import errors
from disnake.ext import commands, tasks

import packages.utils.bot_sql as sql
from bot import BotClient
from packages.utils.utils import get_default_roles, get_utc_monday


class BackgroundTasks(commands.Cog):
    def __init__(self, bot: BotClient):
        if bot.settings.bot_mode == "dev_mode":
            return

        self.bot = bot
        self._setup_logging()
        self.sync_clash_discord.start()
        self.sync_discord_names.start()
        # self.update_presence.start()

    def _setup_logging(self):
        """Setup custom logging for the background tasks"""
        # settings = Settings(daemon=True)
        # LoggerSetup(settings, self.bot.settings.log_name)
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.BackgroundSync')

        self.log.debug('Logging initialized')

    def cog_unload(self):
        self.sync_clash_discord.cancel()
        self.update_presence.cancel()

    @tasks.loop(seconds=60)
    async def update_presence(self):
        messages = [
            (ActivityType.playing, "Spotify"),
            (ActivityType.playing, "Overwatch"),
            (ActivityType.watching, "/help"),
            (ActivityType.playing, "Clash of Clans"),
            (ActivityType.playing, "with cat nip~"),
            (ActivityType.watching, "Fairy Tail"),
            (ActivityType.playing, "I'm not a cat!"),
            (ActivityType.watching, "/help"),
            (ActivityType.playing, "/top"),
            (ActivityType.watching, "Dragon Ball Z"),
            (ActivityType.watching, "/help"),
            (ActivityType.playing, "Reddit Zulu is #1")
        ]
        activity = choice(messages)
        activity_obj = Activity(type=activity[0], name=activity[1])
        activity = Game(activity[1])
        try:
            await self.bot.change_presence(status=Status.online,
                                           activity=activity_obj)
        except Exception:
            self.log.critical(f'Could not change presence with '
                              f'{activity}', exc_info=True)

    @tasks.loop(seconds=600)
    async def sync_discord_names(self):
        self.log.debug("Starting discord name loop")
        changes = 0

        if (guild := self.bot.get_guild(293943534028062721)) is None:
            return

        member_ids = {member.id: member for member in guild.members}

        async with self.bot.pool.acquire() as conn:
            conn: asyncpg.Connection
            users = await conn.fetch(sql.select_discord_users(),
                                     list(member_ids.keys()))

            member: disnake.Member
            for user in users:
                if not (member := member_ids.get(user["discord_id"])):
                    continue

                update_user = False
                if member.name != user["discord_name"]:
                    update_user = True
                elif member.discriminator != user["discord_discriminator"]:
                    update_user = True
                elif member.display_name != user["discord_nickname"]:
                    update_user = True

                if update_user:
                    changes += 1
                    await conn.execute(sql.update_discord_user_names(),
                                       member.id,
                                       member.name,
                                       member.discriminator,
                                       member.display_name)

        self.log.info(f"Updated {changes} users discord names")

    @tasks.loop(seconds=600)
    async def sync_clash_discord(self):
        self.log.debug('Starting discord loop')
        async with self.bot.pool.acquire() as conn:
            active_users = await conn.fetch(sql.select_all_active_users().format(get_utc_monday()))

        # Counter for how many changes were done
        update_count = 0
        for user in active_users:
            member: Member
            # TODO: Add guild to a key somewhere else to support multiple guilds
            guild = self.bot.get_guild(293943534028062721)
            member = guild.get_member(user['discord_id'])
            if not member:
                self.log.critical(f'Unable to retrieve member object for {user["discord_id"]}')
                continue

            if member.display_name != user['clash_name']:
                try:
                    old_name = member.display_name
                    await member.edit(nick=user['clash_name'], reason='Panther Bot Background Sync')
                    self.log.info(f'Changed `{old_name}` name to `{user["clash_name"]}`')
                    update_count += 1
                except errors.Forbidden:
                    msg = f'Unable to change the name of {member.display_name} due to lack of permission'
                    self.log.error(msg)
                except Exception as error:
                    self.log.error(error, exc_info=True)

            users_town_hall_role = self.bot.settings.default_roles.get(f"th{user['town_hall']}s")
            if users_town_hall_role not in (role.id for role in member.roles):
                self.log.info(f'{member.display_name} does not contain the role th{user["town_hall"]}s - updating')
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
                        update_count += 1
                    except errors.Forbidden:
                        msg = f'Unable to provide roles to {member.display_name} due to lack of permissions'
                        self.log.error(msg)
                    except Exception as error:
                        self.log.critical(error, exc_info=True)
        self.log.info(f'Conducted {update_count} changes')

    @sync_clash_discord.before_loop
    async def before_sync_clash_discord(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BackgroundTasks(bot))
