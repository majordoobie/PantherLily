# Built-ins
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

def main():
    #loop = asyncio.get_event_loop()
    setup_logging()
    bot = PantherLily(config=load_settings())
    bot.run()

if __name__ == '__main__':
    main()