import logging
import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

token_var = 'TG_BOT_TOKEN'
TOKEN = os.environ.get(token_var)
if TOKEN is None:
    print(f'You need to specify {token_var}')
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
input_channels_entities = []
