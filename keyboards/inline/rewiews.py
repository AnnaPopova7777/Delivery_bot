from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db

rewiews_cb: CallbackData = CallbackData('rewiew', 'id', 'action')


def rewiews_markup():
    global rewiews_cb

    markup = InlineKeyboardMarkup()
    for idx, title in db.fetchall('SELECT * FROM rewiews_users'):
        markup.add(InlineKeyboardButton(title, callback_data=rewiews_cb.new(id=idx, action='view')))

    return markup
