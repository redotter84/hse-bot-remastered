import asyncio
import logging
from aiogram.utils import executor, exceptions
from random import randrange

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, exceptions
from bot_config import bot, dp, log, input_channels_entities


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(f"ID чата: {message.chat.id}, MAIN_ID: {message.from_user.id}")
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Тут могло бы быть что-то полезное, но пока что этого нет.")


@dp.message_handler(commands=['info'])
async def process_info_command(message: types.Message):
    await message.reply(f"Отслеживаю {len(input_channels_entities)} чатов.")


@dp.message_handler(commands=['subscribe'])
async def process_help_command(message: types.Message):
    await message.reply("Пришли мне ссылку на таблицу пожалуйста")


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.CantInitiateConversation:
        log.error(f"Target [ID:{user_id}]: bot can't initiate conversation with a user")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


@dp.message_handler(lambda message: message.chat.id != message.from_user.id)
async def process_spam_command(message: types.Message):
    # if randrange(10) % 2 == 0:
    await send_message(message.from_user.id, message.text)


@dp.message_handler(commands=['try'])
async def process_try_command(message: types.Message):
    await send_message(message.from_user.id, 'что-то делаю')


if __name__ == '__main__':
    executor.start_polling(dp)
