# Built-ins
from argparse import ArgumentParser
import asyncio
from json import load
import logging
import logging.handlers
from pathlib import Path

# Local
from utils.panther_bot import PantherLily

# Global
PANTHER_LOG = Path('logs/panther.log')
PANTHER_CONFIG = Path('utils/docs/panther_conf.json')

class Panther_Args(ArgumentParser):
    def __init__(self):
        super().__init__(description="Clash of Clans Discord administration bot")
        self.group = self.add_mutually_exclusive_group(required=True)
        self.group.add_argument('--live', help='Run bot in PantherLily shell',
                                    action='store_true', dest='live_mode')

        self.group.add_argument('--dev', help='Run bot in devShell shell',
                                    action='store_true', dest='dev_mode')

    def parse_the_args(self):
        return self.parse_args()

def setup_logging():
    log = logging.getLogger('root')
    log.setLevel(logging.DEBUG)
    log_handler = logging.handlers.RotatingFileHandler(
        PANTHER_LOG,
        encoding='utf-8',
        maxBytes=100000000,
        backupCount=2
        )

    formatter = logging.Formatter('''\
[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Func:%(funcName)s]
[Path:%(pathname)s]
MSG: %(message)s
''',
"%d %b %H:%M:%S"
        )
    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    log.info('Logger initialized')

def load_settings():
    with open(PANTHER_CONFIG, encoding='utf-8') as infile:
        return load(infile)

def main(bot_mode):
    #loop = asyncio.get_event_loop()
    setup_logging()
    bot = PantherLily(config=load_settings(), bot_mode=bot_mode)
    bot.run()

if __name__ == '__main__':
    args = Panther_Args().parse_the_args()
    if args.live_mode:
        main('live_mode')
    else:
        main('dev_mode')