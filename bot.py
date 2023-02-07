import re

from aiogram import types
from aiogram.utils import executor

import database
import message_classifier
from bot_config import dp
from send_message_function import send_message


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЧтобы посмотреть доступные команды - отправь /help :) ")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("В этом боте на данный момент ты можешь выполнить следующие команды:\n"
                        "/get_id - получить ID чата и пользователя\n"
                        "/sub CHAT_ID - оформить подписку на чат с указанным ID\n"
                        "/cancel_sub CHAT_ID - отменить подписку на чат с указанным ID\n"
                        "/info - показать количество отслеживаемых чатов\n"
                        "/sub_sheet URL RANGE - оформить подписку на ячейки таблицы по ссылке\n"
                        "/unsub_sheet URL RANGE - отменить подписку на ячейки таблицы по ссылке")


@dp.message_handler(commands=['info'])
async def process_info_command(message: types.Message):
    await message.reply(f"Всего отслеживаемых чатов: "
                        f"{len(database.get_tg_subscriptions_by_user(message.from_user.id))}\n"
                        f"Всего отслеживаемых таблиц: "
                        f"{len(database.get_sheet_subscriptions_by_user_id(message.from_user.id))}")


# ----------------подписка на чат---------------------------

@dp.message_handler(commands=['get_id'])
async def process_get_id_command(message: types.Message):
    await message.reply(f"ID данного чата: {message.chat.id}\n"
                        f"Пользовательский ID: {message.from_user.id}")


@dp.message_handler(commands=['sub'])
async def process_subscribe_command(message: types.Message):
    await message.reply(f"Для того, чтобы подписаться на обновления беседы, пригласите в нее бота, "
                        f"если он еще в ней не состоит.\n"
                        f"Узнать ID чата можно написав в нужной беседе команду /get_id ;)\n"
                        f"Или воспользуйтесь командой /help, чтобы увидеть все доступные команды.")
    input_id = re.split(' ', message.text, maxsplit=3)
    try:
        input_id = int(input_id[1])
    except ValueError:
        return await message.reply(f"Вы неверно ввели ID. Попробуйте еще раз :)")

    # check if suitable
    database.create_tg_subscription(message.from_user.id, input_id)
    await message.reply(f"Вы успешно подписались на чат со следующим ID: {input_id}")


@dp.message_handler(commands=['cancel_sub'])
async def process_cancel_subscription_command(message: types.Message):
    await message.reply(f"Узнать ID чата можно написав в нужной беседе команду /get_id ;)\n"
                        f"Или воспользуйтесь командой /help, чтобы увидеть все доступные команды.")
    input_id = re.split(' ', message.text, maxsplit=3)
    try:
        input_id = int(input_id[1])
    except ValueError:
        return await message.reply(f"Вы неверно ввели ID. Попробуйте еще раз :)")

    # check if suitable
    database.remove_tg_subscription(message.from_user.id, input_id)
    await message.reply(f"Вы успешно отписались от чата со следующим ID: {input_id}")


@dp.message_handler(lambda message: len(database.get_tg_subscriptions_by_chat(message.chat.id)))
async def process_forward_command(message: types.Message):
    subscriptions = database.get_tg_subscriptions_by_chat(message.chat.id)
    print(subscriptions)
    if message_classifier.is_important(message.text):
        for user in subscriptions:
            await send_message(user.user_id, message.text)


# ------------------подписка на таблицы-------------------


@dp.message_handler(commands=['sub_sheet'])
async def process_subscription_sheet_command(message: types.Message):
    input_str = re.split(' ', message.text, maxsplit=3)
    try:
        input_url = input_str[1]
        input_range = input_str[2]
    except ValueError:
        return await message.reply(f"Вы неверно ввели URL или ячейку. Попробуйте еще раз :)")

    # check if suitable
    database.create_sheet_subscription(message.from_user.id, input_url, input_range)

    await message.reply(f"Вы успешно подписались на обновления таблицы со следующей ячекой: {input_range}")


@dp.message_handler(commands=['unsub_sheet'])
async def process_subscription_sheet_command(message: types.Message):
    input_str = re.split(' ', message.text, maxsplit=3)
    try:
        input_url = input_str[1]
        input_range = input_str[2]
    except ValueError:
        return await message.reply(f"Вы неверно ввели URL или ячейку. Попробуйте еще раз :)")

    # check if suitable
    database.delete_sheet_subscription(message.from_user.id, input_url, input_range)
    await message.reply(f"Вы успешно отписались от обновлений таблицы со следующей ячекой: {input_range}")


@dp.message_handler(commands=['try'])
async def process_spam_command(message: types.Message):
    await send_message(message.from_user.id, 'for testing')


if __name__ == '__main__':
    #request_fuctions.req_sheets_for_update(time_between_requests=5, requests_count=100, troubleshoot_in_read_func=False,
    #                         troubleshoot_mode=True)
    executor.start_polling(dp)
