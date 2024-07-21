from hashlib import md5
from idlelib import query

import aiogram
import markup
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import callback_data

from keyboards.default.markups import cancel_message
from keyboards.inline.products_from_catalog import rewiews_rating
from loader import dp, db, bot
from states.product_state import ReviewsState

from .menu import reviews_us, user_menu
from filters import IsUser


async def show_all_rewiews(m, rewiews: list) -> None:
    for rewiew in rewiews:
        await m.answer(text=f'<b>{rewiew[1]}</b>',
                       reply_markup=rewiews_rating())


@dp.message_handler(IsUser(), text=reviews_us)
async def rewiews_user(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        'Оставить отзыв', callback_data='leave_feedback', ))

    rewiew = db.fetchall("SELECT * FROM rewiews_users")

    await show_all_rewiews(callback, rewiew)
    await callback.answer('Оставьте отзыв', reply_markup=markup)


###
@dp.callback_query_handler(IsUser(), text='leave_feedback')
async def rewiews_handler(query: CallbackQuery):
    await query.message.answer('Напишите свое мнение о нашей доставке')
    await ReviewsState.title_r.set()


@dp.message_handler(IsUser(), text=cancel_message, state=ReviewsState.title_r)
async def process_cancel_rew(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!')
    await state.finish()

    await user_menu(message)


@dp.message_handler(IsUser(), state=ReviewsState.title_r)
async def set_rewiews_handler(message: Message, state: FSMContext):
    rewiew = message.text
    idx = md5(rewiew.encode('utf-8')).hexdigest()
    db.query('INSERT INTO rewiews_users VALUES (?, ?)', (idx, rewiew))

    await message.answer('Ваш отзыв сохранен')
    await state.finish()
    await user_menu(message)
