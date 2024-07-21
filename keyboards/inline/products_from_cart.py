from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

product_cb = CallbackData('product', 'id', 'action')
reviews_pag_cb = CallbackData('review', 'id', 'action')


def product_markup(idx, count):
    global product_cb

    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton('⬅️', callback_data=product_cb.new(id=idx, action='decrease'))
    count_btn = InlineKeyboardButton(count, callback_data=product_cb.new(id=idx, action='count'))
    next_btn = InlineKeyboardButton('➡️', callback_data=product_cb.new(id=idx, action='increase'))
    markup.row(back_btn, count_btn, next_btn)

    return markup


def reviews_pag_markup(idx, count):
    global reviews_pag_cb

    markup = InlineKeyboardMarkup()
    back_pag = InlineKeyboardButton('⬅️', callback_data=reviews_pag_cb.new(id=idx, action='back'))
    count_btn = InlineKeyboardButton(count, callback_data=reviews_pag_cb.new(id=idx, action='count_pag'))
    next_pag = InlineKeyboardButton('➡️', callback_data=reviews_pag_cb.new(id=idx, action='forward'))
    markup.row(back_pag, count_btn, next_pag)

    return markup
