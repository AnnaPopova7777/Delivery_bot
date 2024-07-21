import os
import hashlib
import json
import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data import config
from data.config import ADMIN_ID
from loader import dp, db, bot
import filters
import logging
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
user_message = 'Пользователь'
admin_message = 'Админ'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    text = db.fetchall(
        'SELECT title FROM announcement')
    if len(text) != 0:
        await message.answer(f'Объявление:\n'
                             f'{text}')
    if message.from_user.id == ADMIN_ID:
        await message.answer(f'Вы авторизовались как администратор. Что бы начать работу, нажмите сюда /settings')
    else:
        await message.answer(
            f'{message.from_user.first_name}, добро пожаловать. Что бы начать работу, нажмите сюда /menu')


@dp.message_handler(commands='help')
async def cmd_start(message: types.Message):
    await message.answer(f'Для старта работы введите команду /start,'
                         f'\n Что бы перейти в корзину и начать оформление заказа, нажмите кнопку "Корзина"'
                         f'\n Для вызова списка категорий товаров, нажмите кнопку "Каталог"')


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.remove(cid)
    await message.answer('Включен пользовательский режим. /menu', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):
    cid = message.chat.id
    if cid not in config.ADMINS:
        config.ADMINS.append(cid)
    await message.answer('Включен админский режим. /settings', reply_markup=ReplyKeyboardRemove())


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.create_tables()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
