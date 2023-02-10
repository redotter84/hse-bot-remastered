import asyncio
import base64
import logging
import re

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor, exceptions

from bot_config import dp
from send_message_function import send_message

import database
import message_classifier


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЧтобы посмотреть доступные команды - отправь /help :) ")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("В этом боте на данный момент ты можешь выполнить следующие команды:\n"
                        "/info - показать количество отслеживаемых чатов и таблиц\n"
                        "/get_id - получить ID чата и пользователя\n"
                        "/chat CHAT_ID - настроить подписку на чат с указанным ID\n"
                        "/sheet URL RANGE - настроить подписку на ячейки таблицы по ссылке\n")


@dp.message_handler(commands=['info'])
async def process_info_command(message: types.Message):
    await message.reply(f"Всего отслеживаемых чатов: "
                        f"{len(database.get_tg_subscriptions_by_user(message.from_user.id))}\n"
                        f"Всего отслеживаемых таблиц: "
                        f"{len(database.get_sheet_subscriptions_by_user_id(message.from_user.id))}")


async def build_menu(message: types.Message, subscription, suffix: str):
    buttons = []
    if not subscription:
        buttons.append(('🔔 Subscribe', f'add_{suffix}'))
    else:
        buttons.append(('❌ Unsubscribe', f'remove_{suffix}'))
        if not subscription.muted:
            buttons.append(('🔇 Mute', f'mute_{suffix}'))
        else:
            buttons.append(('🔊 Unmute', f'unmute_{suffix}'))
    keyboard_buttons = [InlineKeyboardButton(name, callback_data=data) for name, data in buttons]
    markup = InlineKeyboardMarkup().add(*keyboard_buttons)
    return await message.reply(f'Что вы хотите сделать с этой подпиской?', reply_markup=markup)


# ----------------подписка на чат---------------------------


@dp.message_handler(commands=['get_id'])
async def process_get_id_command(message: types.Message):
    await message.reply(f"ID данного чата: {message.chat.id}\n"
                        f"ID пользователя: {message.from_user.id}")


async def get_chat_data(state) -> str:
    data = await state.get_data()
    return data['chat_id']


@dp.callback_query_handler(text='add_chat')
async def process_add_chat(call, state):
    chat_id = await get_chat_data(state)
    database.create_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Вы успешно подписались на чат {chat_id}")


@dp.callback_query_handler(text='remove_chat')
async def process_remove_chat(call, state):
    chat_id = await get_chat_data(state)
    database.remove_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Вы успешно отписались от чата {chat_id}")


@dp.callback_query_handler(text='mute_chat')
async def process_mute_chat(call, state):
    chat_id = await get_chat_data(state)
    database.toggle_mute_for_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Включен тихий режим для чата {chat_id}")


@dp.callback_query_handler(text='unmute_chat')
async def process_unmute_chat(call, state):
    chat_id = await get_chat_data(state)
    database.toggle_mute_for_tg_subscription(call.from_user.id, chat_id)
    await call.message.edit_text(f"Выключен тихий режим для чата {chat_id}")


@dp.message_handler(commands=['chat'])
async def process_chat_command(message: types.Message, state):
    if ' ' not in message.text:
        await message.reply(f"Узнать ID чата можно, написав в нужной беседе команду /get_id ;)\n"
                        f"Или воспользуйтесь командой /help, чтобы увидеть все доступные команды.")
        return

    chat_id = re.split(' ', message.text, maxsplit=3)
    try:
        chat_id = int(chat_id[1])
        await state.update_data(chat_id=chat_id)
    except ValueError:
        return await message.reply(f"Вы неверно ввели ID. Попробуйте еще раз :)")

    buttons = []
    subscription = database.get_tg_subscription(user_id=message.from_user.id, chat_id=chat_id)
    return await build_menu(message, subscription, 'chat')


@dp.message_handler(lambda message: len(database.get_tg_subscriptions_by_chat(message.chat.id)))
async def process_chat_message(message: types.Message):
    should_notify = message_classifier.is_important(message.text)
    if should_notify:
        subscriptions = database.get_tg_subscriptions_by_chat(message.chat.id)
        for sub in subscriptions:
            await send_message(sub.user_id, f'В чат "{message.chat.title}" пришло новое сообщение:', disable_notification=sub.muted)
            await send_message(sub.user_id, message.text, disable_notification=sub.muted)
            if sub.muted:
                await send_message(
                    sub.user_id,
                    "Внимание: у данного чата включен тихий режим, поэтому уведомление было беззвучное",
                    disable_notification=sub.muted,
                )


# ------------------подписка на таблицы-------------------


async def get_sheet_data(state):
    data = await state.get_data()
    return data['sheet_link'], data['sheet_range']


@dp.callback_query_handler(text_contains='add_sheet')
async def process_add_sheet(call, state):
    sheet_link, sheet_range = await get_sheet_data(state)
    database.create_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Вы успешно подписались на обновления ячеек {sheet_range} таблицы {sheet_link}")


@dp.callback_query_handler(text_contains='remove_sheet')
async def process_remove_sheet(call, state):
    sheet_link, sheet_range = await get_sheet_data(state)
    database.delete_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Вы успешно отписались от обновления ячеек {sheet_range} таблицы {sheet_link}")


@dp.callback_query_handler(text='mute_sheet')
async def process_mute_sheet(call, state):
    sheet_link, sheet_range = await get_sheet_data(state)
    database.toggle_mute_for_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Включен тихий режим для чата ячеек {sheet_range} таблицы {sheet_link}")


@dp.callback_query_handler(text='unmute_sheet')
async def process_unmute_sheet(call, state):
    sheet_link, sheet_range = await get_sheet_data(state)
    database.toggle_mute_for_sheet_subscription(call.from_user.id, sheet_link, sheet_range)
    await call.message.edit_text(f"Выключен тихий режим для чата ячеек {sheet_range} таблицы {sheet_link}")


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
    return await build_menu(message, subscription, 'sheet')


# --------------------------------------------------------


if __name__ == '__main__':
    executor.start_polling(dp)
