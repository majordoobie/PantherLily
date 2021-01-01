"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
# Little hack to get the parent packages for the bot working in here
import sys
sys.path.append('/opt/project')

import asyncio
import nest_asyncio
import asyncpg
import coc
from datetime import datetime
import logging
import traceback

from packages.private.settings import Settings
from packages.logging_setup import BotLogger as LoggerSetup

SQL_GET_ACTIVE = """SELECT * 
FROM discord_user, clash_account
WHERE is_active = 'true'
  and discord_user.discord_id = clash_account.discord_id
  and clash_account.is_primary_account = 'true'"""

SQL_UPDATE_CLASSIC = """INSERT INTO clash_classic_update (increment_date, tag, current_donations) VALUES ($1, $2, $3);"""

async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.classic_update')

    try:
        while True:
            log.debug("Starting update loop")
            # Get all active members
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)

                updates = 0
                async for player in coc_client.get_players((member['clash_tag'] for member in active_members)):
                    try:
                        await conn.execute(SQL_UPDATE_CLASSIC,
                                datetime.utcnow(),
                                player.tag,
                                player.get_achievement("Friend in Need").value,
                                player.clan.tag,
                                player.clan.name,
                        )
                        updates +=1
                    except asyncpg.ForeignKeyViolationError as error:
                        log.error(error, stack_info=True)
                    except Exception as error:
                        log.error(error, stack_info=True)

                log.info(f"Updated {updates} members")
            log.debug(f'Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        log.debug('CTRL + C executed')
    except Exception as error:
        log.critical(error, stack_info=True)


async def main(coc_client_):
    """Async start point will for all background tasks"""
    LoggerSetup(SETTINGS, 'PantherDaemon')
    log = logging.getLogger('PantherDaemon')
    log.debug("Starting background loops")
    pool : asyncpg.pool.Pool = await asyncpg.create_pool(SETTINGS.dsn)
    loop = asyncio.get_running_loop()

    tasks = [
        loop.create_task(update_active_users(300, coc_client_, pool))
    ]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    SETTINGS = Settings(daemon=True)

    # Nest patches asyncio to allow for nested loops to allow logging into coc
    nest_asyncio.apply()

    _coc_client: coc.client.Client = coc.login(
        SETTINGS.coc_user,
        SETTINGS.coc_pass,
        key_names="Panther Daemon",
    )
    asyncio.run(main(_coc_client))