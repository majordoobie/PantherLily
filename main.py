import argparse
import logging
import traceback

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
    logger = logging.getLogger('root')

    try:
        bot = BotClient(settings=settings, command_prefix=settings.bot_config['bot_prefix'])
        bot.run()
        
    except Exception as error:
        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        print(exc)
        logger.error(error, exc_info=True)
        
    finally:
        print("closing DB")


if __name__ == '__main__':
    main()
