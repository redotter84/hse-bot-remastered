import asyncio
import base64
import database
import logging
import message_classifier
import re
import request_fuctions

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor, exceptions
from bot_config import dp
from send_message_function import send_message


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЧтобы посмотреть доступные команды - отправь /help :) ")
    # while True:
    #     if request_functions.flag_changed:
    #         await send_message(request_functions.userr_id, f'В таблице по подписке № {request_functions.sub_id} '
    #                            f'произошло изменение!\nСтарые данные:'
    #                            f'{request_functions.old_data}, \nНовые данные: {request_functions.neww_data}')
    #         request_functions.flag_changed = False


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("В этом боте на данный момент ты можешь выполнить следующие команды:\n"
                        "/info - показать количество отслеживаемых чатов и таблиц\n"
                        "/id - получить ID чата и пользователя\n"
                        "/chat CHAT_ID - настроить подписку на чат с указанным ID\n"
                        "/sheet URL RANGE - настроить подписку на ячейки таблицы по ссылке\n")


@dp.message_handler(commands=['info'])
async def process_info_command(message: types.Message):
    await message.reply(f"Всего отслеживаемых чатов: "
                        f"{len(database.get_tg_subscriptions_by_user(message.from_user.id))}\n"
                        f"Всего отслеживаемых таблиц: "
                        f"{len(database.get_sheet_subscriptions_by_user_id(message.from_user.id))}")


async def build_menu(message: types.Message, subscription, add_cmd, remove_cmd):
    buttons = []
    if not subscription:
        buttons.append(('🔔 Subscribe', add_cmd))
    else:
        buttons.append(('❌ Unsubscribe', remove_cmd))
    keyboard_buttons = [InlineKeyboardButton(name, callback_data=data) for name, data in buttons]
    markup = InlineKeyboardMarkup().add(*keyboard_buttons)
    return await message.reply(f'Что вы хотите сделать с этой подпиской?', reply_markup=markup)


# ----------------подписка на чат---------------------------


@dp.message_handler(commands=['get_id'])
async def process_get_id_command(message: types.Message):
    await message.reply(f"ID данного чата: {message.chat.id}\n"
                        f"ID пользователя: {message.from_user.id}")


@dp.callback_query_handler(text='add_chat')
async def process_add_chat(call, state):
    data = await state.get_data()
    chat_id = data['chat_id']
    database.create_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Вы успешно подписались на чат {chat_id}")


@dp.callback_query_handler(text='remove_chat')
async def process_remove_chat(call, state):
    data = await state.get_data()
    chat_id = data['chat_id']
    database.remove_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Вы успешно отписались от чата {chat_id}")


@dp.message_handler(commands=['chat'])
async def process_chat_command(message: types.Message, state):
    await message.reply(f"Узнать ID чата можно написав в нужной беседе команду /get_id ;)\n"
                        f"Или воспользуйтесь командой /help, чтобы увидеть все доступные команды.")

    chat_id = re.split(' ', message.text, maxsplit=3)
    try:
        chat_id = int(chat_id[1])
        await state.update_data(chat_id=chat_id)
    except ValueError:
        return await message.reply(f"Вы неверно ввели ID. Попробуйте еще раз :)")

    buttons = []
    subscription = database.get_tg_subscription(user_id=message.from_user.id, chat_id=chat_id)
    return await build_menu(message, subscription, 'add_chat', 'remove_chat')


# ------------------подписка на таблицы-------------------


@dp.callback_query_handler(text_contains='add_sheet')
async def process_add_sheet(call, state):
    data = await state.get_data()
    sheet_link = data['sheet_link']
    sheet_range = data['sheet_range']
    database.create_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Вы успешно подписались на обновления ячеек {sheet_range} таблицы {sheet_link}")


@dp.callback_query_handler(text_contains='remove_sheet')
async def process_remove_sheet(call, state):
    data = await state.get_data()
    sheet_link = data['sheet_link']
    sheet_range = data['sheet_range']
    database.delete_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Вы успешно отписались от обновления ячеек {sheet_range} таблицы {sheet_link}")


@dp.message_handler(commands=['sheet'])
async def process_sheet_command(message: types.Message, state):
    input_str = re.split(' ', message.text, maxsplit=3)
    try:
        _, sheet_link, sheet_range = input_str
        await state.update_data(sheet_link=sheet_link)
        await state.update_data(sheet_range=sheet_range)
    except ValueError:
        return await message.reply(f"Вы неверно ввели URL или ячейку. Попробуйте еще раз :)")

    subscription = database.get_sheet_subscription(user_id=message.from_user.id, sheet_link=sheet_link, sheet_range=sheet_range)
    return await build_menu(message, subscription, 'add_sheet', 'remove_sheet')


# --------------------------------------------------------


if __name__ == '__main__':
    #request_functions.req_sheets_for_update(time_between_requests=5, requests_count=10, troubleshoot_in_read_func=False,
    #                      troubleshoot_mode=False)
    executor.start_polling(dp)
