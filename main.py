import asyncio
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
    group.add_argument('--live', help='Run bot with Panther shell',
                       action='store_true', dest='live_mode')
    group.add_argument('--dev', help='Run in dev shell',
                       action='store_true', dest='dev_mode')

    return parser

async def run(settings):
    pool = await asyncpg.create_pool(settings.dsn)
    bot = BotClient(settings=settings, pool=pool, command_prefix=settings.bot_config['bot_prefix'])
    try:
        await bot.start(settings.bot_config['bot_token'])

    except KeyboardInterrupt:
        await pool.close()
        await bot.logout()


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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(settings))


if __name__ == '__main__':
    main()
