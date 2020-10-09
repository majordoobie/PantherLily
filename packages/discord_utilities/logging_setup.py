import logging
from logging.handlers import QueueListener, QueueHandler
from queue import Queue

from discord import Webhook, RequestsWebhookAdapter, Embed

DEFAULT_FORMAT = ('''\
[%(asctime)s]:[%(levelname)s]:[%(name)s]:[Line:%(lineno)d][Func:%(funcName)s]
[Path:%(pathname)s]
MSG: %(message)s
''')

# TODO: Set up the logging module use settings.py to keep the settings
class DiscordLogger:
    def __init__(self, settings):
        self.settings
        self.log_queue = Queue(-1)

