import asyncio
import logging
from pathlib import Path

import asyncpg
import argparse
import json

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
        Parser objec
    """
    parser = argparse.ArgumentParser(description="Process arguments for discord bot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--live", help="Run bot with Panther shell", action="store_true", dest="live_mode",
                       default=False)
    group.add_argument("--dev", help="Run in dev shell", action="store_true", dest="dev_mode", default=False)
    return parser


async def run(settings: Settings, coc_client: coc, pool: asyncpg.pool):
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
    intents = Intents.default()
    intents.members = True
    intents.messages = True
    intents.reactions = True
    bot = BotClient(settings=settings, pool=pool, coc_client=coc_client,
                    command_prefix=settings.bot_config["bot_prefix"], intents=intents)

    log = logging.getLogger(f"{settings.bot_config['log_name']}.Main")

    await bot.start(settings.bot_config["bot_token"])


async def _get_pool(settings: Settings):
    try:
        async def init(con):
            """Create custom column type, json."""
            await con.set_type_codec("json", schema="pg_catalog",
                                     encoder=json.dumps, decoder=json.loads)

        pool = await asyncpg.create_pool(settings.dsn, init=init)
        return pool
    except Exception as error:
        exit(error)


def main():
    """
    Sets up the environment for the bot. Uses .env for any sensitive information and puts them
    in the Settings class. Then uses the information to instantiate the bot.
    """
    parser = bot_args()
    args = parser.parse_args()

    settings = None
    project_path = Path(".").resolve()
    if args.dev_mode:
        settings = Settings(project_path, "dev_mode")
    elif args.live_mode:
        settings = Settings(project_path, "live_mode")

    BotLogger(settings)
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(_get_pool(settings))

    print("type of loop", type(loop))
    coc_client = coc.login(
                settings.coc_user,
                settings.coc_pass,
                client=coc.EventsClient,
                loop=loop,
                key_names=settings.bot_config["key_name"]
    )

    try:
        loop.run_until_complete(run(settings, coc_client, pool))

    except KeyboardInterrupt:
        print("Cleanup up resources")
        await pool.close()
        coc_client.close()
        loop.close()


if __name__ == "__main__":
    main()
