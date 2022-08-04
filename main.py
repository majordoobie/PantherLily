import argparse
import asyncio
import json
import logging
from asyncio import CancelledError, shield
from pathlib import Path

import asyncpg
import coc
from discord import Intents

from bot import BotClient
from packages.logging_setup import BotLogger
from packages.private.settings import Settings


def _bot_args() -> argparse.Namespace:
    """
    Creates mutually exclusive arguments that dictates how the bot should run.

    The settings change the db that is connected, the bot logged into and
    the logs to use

    :return: Namespace of parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Process arguments for discord bot")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--live",
        help="Run bot with Panther shell",
        action="store_true",
        dest="live_mode",
        default=False)

    group.add_argument(
        "--dev",
        help="Run in dev shell",
        action="store_true",
        dest="dev_mode",
        default=False)

    return parser.parse_args()


async def _get_pool(settings: Settings) -> asyncpg.pool.Pool:
    """
    Creates a conection pool to the database. Before it does that it sets
    a custom json encoder for the database pool

    :param settings: configuration for the bot
    :type settings: settings
    :return: Connection pool
    :rtype: asyncpg.pool.Pool
    """

    try:
        async def init(con):
            """Create custom column type, json."""
            await con.set_type_codec("json", schema="pg_catalog",
                                     encoder=json.dumps, decoder=json.loads)

        pool = await asyncpg.create_pool(settings.dsn, init=init)
        return pool
    except Exception as error:
        exit(error)


def _get_coc_client(settings: Settings) -> coc.Client:
    """
    Init the Client class with custom settings

    :param settings: configuration for the bot
    :type settings: settings
    :return: Configured Client class
    """
    return coc.Client(
        key_count=4,
        throttler_limit=30,
        client=coc.EventsClient,
        key_names=settings.bot_config["key_name"],
    )


async def main() -> None:
    """
    Sets up the environment for the bot

    :return: None
    """

    # Get args
    args = _bot_args()

    # Get settings based on args mode
    project_path = Path.cwd().resolve()
    settings = None

    if args.dev_mode:
        settings = Settings(project_path, "dev_mode")
    elif args.live_mode:
        settings = Settings(project_path, "live_mode")

    # Get a coc client to call into
    client = _get_coc_client(settings)

    BotLogger(settings)

    # Get the db connection pool for the bot
    pool = await _get_pool(settings)

    # Log into coc client
    await client.login(settings.coc_user, settings.coc_pass)

    intents = Intents.default()
    intents.members = True
    intents.messages = True
    intents.reactions = True

    bot = BotClient(
        settings=settings,
        pool=pool,
        coc_client=client,
        command_prefix=settings.bot_config["bot_prefix"], intents=intents
    )

    log = logging.getLogger(f"{settings.bot_config['log_name']}.Main")

    # Shield catches the keyboard interupt giving time to cleanup
    try:
        await shield(bot.start(settings.bot_config["bot_token"]))
    except CancelledError:
        msg = "Closing db connection pool before exiting"
        log.debug(msg)
        print(msg)
        await pool.close()


if __name__ == "__main__":
    # Run bot loop. Ignore keyboard interupt errors
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
