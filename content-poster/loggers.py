import logging
from os.path import isdir
from os import mkdir
if not isdir('logs'):
    mkdir('logs')

# logging severity levels, ASC: debug, info, warning, error, critical

logging.basicConfig(handlers=[logging.FileHandler('logs/bot.log', 'a', 'utf-8')],
                    format='|%(asctime)s| %(name)s->%(levelname)s:\t%(message)s',
                    datefmt='%d-%m-%y %H:%M',
                    level=logging.INFO)
console = logging.StreamHandler()  # Create console logging
console.setLevel(logging.DEBUG)  # Set console severity level
formatter = logging.Formatter('%(name)s->%(levelname)s:\t%(message)s')
console.setFormatter(formatter)  # Set console formatting
logging.getLogger('').addHandler(console)  # Attach console to the logger
events = logging.getLogger('bot.events')  # Logger for events
