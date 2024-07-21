from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db

product_cb = CallbackData('product', 'id', 'action')
reviews_cb = CallbackData('review', 'id', 'action')


def product_markup(idx='', price=0):
    global product_cb

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(f'Добавить в корзину - {price}₽', callback_data=product_cb.new(id=idx, action='add')))

    return markup


def rewiews_rating():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('👍', callback_data='plus_rating'),
               InlineKeyboardButton('👎', callback_data='minus_rating'))

    return markup


def rewiews_rating_del_admin(idx: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Удалить', callback_data=reviews_cb.new(id=idx, action='delete_rew')))

    return markup



