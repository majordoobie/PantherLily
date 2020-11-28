"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
import asyncio
import asyncpg
import coc
import logging

from packages.private.settings import Settings
from packages.logging_setup import BotLogger as LoggerSetup

async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool, log: logging.Logger):
    while True:
        async with pool.acquire() as conn:
            print(len(await conn.fetch("SELECT * FROM discord_user")))
        await asyncio.sleep(sleep_time)

def main():
    settings = Settings(daemon=True)
    loop = None
    try:
        LoggerSetup(settings)
        log = logging.getLogger('daemon.update')
        loop = asyncio.get_event_loop()

        # get pool and coc objects
        pool: asyncpg.pool.Pool = loop.run_until_complete(asyncpg.create_pool(settings.dsn))
        coc_client: coc.client.Client = coc.login(settings.coc_user, settings.coc_pass, loop=loop, key_names="Panther Daemon")

        loop.create_task(update_active_users(
            15,
            coc_client,
            pool,
            log
        ))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if loop:
            loop.close()

if __name__ == '__main__':
    main()