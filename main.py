import asyncio
import coc
import logging

import asyncpg
import argparse

from bot import BotClient
from packages.logging_setup import BotLogger
from packages.private.settings import Settings


def bot_args():
    """
    Creates the argument parse and returns it to the caller
    Returns
    -------
    parser
    """
    parser = argparse.ArgumentParser("Process arguments for discord bot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--live', help='Run bot with Panther shell', action='store_true', dest='live_mode', default=False)
    group.add_argument('--dev', help='Run in dev shell', action='store_true', dest='dev_mode', default=False)
    # Testing update
    return parser

async def run(settings, coc_client):
    pool = await asyncpg.create_pool(settings.dsn)
    bot = BotClient(settings=settings, pool=pool, coc_client=coc_client, command_prefix=settings.bot_config['bot_prefix'])
    log = logging.getLogger('root')

    try:
        await bot.start(settings.bot_config['bot_token'])

    except KeyboardInterrupt:
        log.info("Interrupt detected")
        pass

    finally:
        await coc_client.close()
        await pool.close()
        await bot.close()


def main():
    """
    Sets up the environment for the bot. Uses .env for any sensitive information and puts them
    in the Settings class. Then uses the information to instantiate the bot.
    """
    args = bot_args().parse_args()
    settings = None
    if args.dev_mode:
        settings = Settings('dev_mode')
    elif args.live_mode:
        settings = Settings('live_mode')

    BotLogger(settings)
    #coc_client = coc.login(settings.coc_user, settings.coc_pass, client=coc.EventsClient)
    loop = asyncio.get_event_loop()
    coc_client = coc.login(settings.coc_user, settings.coc_pass, client=coc.EventsClient, loop=loop)
    try:
        loop.run_until_complete(run(settings, coc_client))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
