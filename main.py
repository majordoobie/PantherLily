"""
100 % @ 1734
"""
import asyncio
import logging
import asyncpg
import argparse

import coc
from discord import Intents

from bot import BotClient
from packages.logging_setup import BotLogger
from packages.private.settings import Settings


def bot_args() -> argparse.ArgumentParser:
    """
    Sets up the arguments to run the bot.

    Returns
    -------
    parser: argparser.ArgumentParser
        Parser object
    """
    parser = argparse.ArgumentParser(description="Process arguments for discord bot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--live', help='Run bot with Panther shell', action='store_true', dest='live_mode',
                       default=False)
    group.add_argument('--dev', help='Run in dev shell', action='store_true', dest='dev_mode', default=False)
    return parser


async def run(settings: Settings, coc_client: coc):
    """
    Uses the event loop created in main to run the async libraries that need it
<class 'asyncpg.pool.Pool'>
<class 'coc.events.EventsClient'>

    Parameters
    ----------
    settings: Settings
        Configuration for the mode given
    coc_client: coc.events.EventsClient
        Clash of Clans client of interacting with the Clash of Clans API
    """
    pool = await asyncpg.create_pool(settings.dsn)
    intents = Intents.default()
    intents.members = True
    bot = BotClient(settings=settings, pool=pool, coc_client=coc_client,
                    command_prefix=settings.bot_config['bot_prefix'], intents=intents)
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
    parser = bot_args()
    args = parser.parse_args()

    settings = None
    if args.dev_mode:
        settings = Settings('dev_mode')
    elif args.live_mode:
        settings = Settings('live_mode')

    BotLogger(settings)
    loop = asyncio.get_event_loop()
    coc_client = coc.login(settings.coc_user, settings.coc_pass, client=coc.EventsClient, loop=loop,
                           key_names=settings.bot_config['key_name'])
    try:
        loop.run_until_complete(run(settings, coc_client))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
