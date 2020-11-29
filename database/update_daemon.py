"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
import asyncio
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

SQL_UPDATE_CLASSIC = """INSERT INTO clash_classic_update (increment_date, tag, current_donations) VALUES (?, ?, ?);"""

async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    LOG.debug("Running classic update daemon")
    async with pool.acquire() as conn:
        # Get all active members from the database
        active_members = await conn.fetch(SQL_GET_ACTIVE)

        # Get the coc object of each player
        active_players = []
        async for player in coc_client.get_players((member['clash_tag'] for member in active_members)):
            active_players.append(player)
            print(player.get_achievement("Friend in Need").value)
            print("FUCKKKKK")
            return

        # Update classic table
        for player in active_players:
            await conn.execute(SQL_UPDATE_CLASSIC, (
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                player.tag,
                #player.get_achievement("Friend in Need").value,
                10
            ))

async def test(pool, msg):
    try:
        while True:
            print(msg)
            async with pool.acquire() as conn:
                print(len(await conn.fetch("select * from discord_user;")))
                print("THis is that other one")

            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("THis is the control c doe")

async def main(coc_client_):
    pool : asyncpg.pool.Pool = await asyncpg.create_pool(SETTINGS.dsn)

    async with pool.acquire() as conn:
        print(len(await conn.fetch("select * from discord_user;")))
        print("that is how many we got")

    loop = asyncio.get_running_loop()
    tasks = [
        loop.create_task(test(pool, "This is the fist one")),
        loop.create_task(test(pool, "This is the second one"))
    ]
    await asyncio.wait(tasks)


   # Create tasks
   # loop.create_task(update_active_users(
   #     15,
   #     coc_client,
   #     pool
   # ))

if __name__ == '__main__':
    SETTINGS = Settings(daemon=True)
    LoggerSetup(SETTINGS)
    LOG = logging.getLogger('daemon.update')

    _coc_client: coc.client.Client = coc.login(
        SETTINGS.coc_user,
        SETTINGS.coc_pass,
        key_names="Panther Daemon",
    )
    asyncio.run(main(_coc_client))

"""
    _loop = None
    _coc = None

    try:
        LOG.debug("Creating event loop and running main coroutine")
        
        _loop = asyncio.get_event_loop()

        _loop.run_until_complete(main(_coc))
    except KeyboardInterrupt:
        print("Keyboard interrupt")
    except Exception as error:
        print(error)
        print("\n\nWe here\n\n")
        LOG.error(error, stack_info=True)
    finally:
        if _loop:
            _coc.close()
            _loop.close()
            """