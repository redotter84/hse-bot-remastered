import logging
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
input_channels_entities = []
