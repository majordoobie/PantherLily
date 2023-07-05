import argparse
import asyncio
import json
from pathlib import Path

import asyncpg
import disnake

import coc
import pandas as pd

from bot import BotClient
from packages.clash_stats import clash_stats_levels
from packages.private.settings import Settings
from packages.logging_setup import BotLogger


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


def _get_settings() -> Settings:
    # Get args
    args = _bot_args()

    # Get settings based on args mode
    project_path = Path.cwd().resolve()

    if args.dev_mode:
        return Settings(project_path, "dev_mode")
    elif args.live_mode:
        return Settings(project_path, "live_mode")


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
        print("Got an error; ", error)
        exit(error)


async def _get_coc_client(settings: Settings) -> coc.EventsClient:
    """
    Init the Client class with custom settings

    :param settings: configuration for the bot
    :type settings: settings
    :return: Configured Client class
    """
    client = coc.EventsClient(
            key_count=4,
            throttler_limit=30,
            key_names=settings.bot_config["key_name"],
        )

    try:
        await client.login(settings.coc_user, settings.coc_pass)
        return client

    except coc.InvalidCredentials as error:
        exit(error)



def _get_bot_client(settings: Settings, coc_client: coc.EventsClient,
                    pool: asyncpg.Pool, troop_df: pd.DataFrame) -> BotClient:
    intents = disnake.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    intents.emojis = True
    intents.guilds = True

    return BotClient(
        settings=settings,
        pool=pool,
        troop_df=troop_df,
        coc_client=coc_client,
        command_prefix=settings.bot_config["bot_prefix"],
        intents=intents,
        activity=disnake.Game(name=settings.bot_config.get("version")),
    )


async def main():
    settings = _get_settings()
    BotLogger(settings)

    # Fetch the pool and coc_client
    pool = await _get_pool(settings)
    coc_client = await _get_coc_client(settings)

    # Refresh the sheets on disk
    clash_stats_levels.download_sheets()
    troop_df = clash_stats_levels.get_troop_df()

    # Get bot class
    bot = _get_bot_client(settings, coc_client, pool, troop_df)

    # Run the runner function
    try:
        await bot.start(settings.bot_config["bot_token"])

    except KeyboardInterrupt:
        pass  # Ignore interrupts and go to clean up

    finally:
        # Close both pool and client sessions
        await pool.close()
        await coc_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
