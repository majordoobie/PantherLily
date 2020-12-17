"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
import asyncio
import nest_asyncio
import asyncpg
import coc
from datetime import datetime
import logging

from packages.private.settings import Settings
from packages.logging_setup import BotLogger as LoggerSetup

SQL_GET_ACTIVE = """SELECT * 
FROM discord_user, clash_account
WHERE is_active = 'true'
  and discord_user.discord_id = clash_account.discord_id
  and clash_account.is_primary_account = 'true'"""

SQL_UPDATE_CLASSIC = """INSERT INTO clash_classic_update (increment_date, tag, current_donations) VALUES ($1, $2, $3);"""

async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    LOG.debug("Running classic update daemon")
    try:
        while True:
            # Get all active members
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)

                async for player in coc_client.get_players((member['clash_tag'] for member in active_members)):
                    try:
                        await conn.execute(SQL_UPDATE_CLASSIC,
                                datetime.utcnow(),
                                player.tag,
                                player.get_achievement("Friend in Need").value
                        )
                    except asyncpg.ForeignKeyViolationError as error:
                        print(error)
                    except Exception as error:
                        import traceback
                        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))


            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        print("THis is the control c doe")
    except Exception as error:
        import traceback
        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        print(exc)



async def main(coc_client_):
    """Async start point will for all background tasks"""
    pool : asyncpg.pool.Pool = await asyncpg.create_pool(SETTINGS.dsn)
    loop = asyncio.get_running_loop()

    tasks = [
        loop.create_task(update_active_users(60, coc_client_, pool))
    ]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    SETTINGS = Settings(daemon=True)
    LoggerSetup(SETTINGS)
    LOG = logging.getLogger('daemon.update')

    # Nest patches asyncio to allow for nested loops to allow logging into coc
    nest_asyncio.apply()
    _coc_client: coc.client.Client = coc.login(
        SETTINGS.coc_user,
        SETTINGS.coc_pass,
        key_names="Panther Daemon",
    )

    asyncio.run(main(_coc_client))