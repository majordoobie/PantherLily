"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
import asyncio
import asyncpg
import coc
import logging

from packages.private.settings import Settings
from packages.logging_setup import BotLogger

async def update_active_users(sleep_time: int, coc_client: coc, log: logging.Logger, dsn: str):
    # TODO: can't be creating multiple connections it's counter intuitive I need to pass the pool in
    try:
        pool = await asyncpg.create_pool(dsn)
    except Exception as error:
        log.error(error, stack_info=True)


    # Sleep to re-run code
    pool.close()
    await asyncio.sleep(sleep_time)



def main():
    settings = Settings()
    BotLogger(settings)
    log = logging.getLogger('daemon.update')
    loop = asyncio.get_event_loop()
    coc_client = coc.login(settings.coc_user, settings.coc_pass, client=coc.EventsClient, loop=loop,
                           key_names=settings.bot_config['key_name'])

    loop.create_task(update_active_users(60, coc_client, log, settings.dsn))
    loop.run_forever()


if __name__ == '__main__':
    main()