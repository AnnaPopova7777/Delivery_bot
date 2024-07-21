from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup

from loader import dp, db
from filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Корзина'
about_Us = '🧑🏼‍🍳 О нас'
connect_us = '📞Связаться с нами'
reviews_us = 'Отзывы'


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    text = db.fetchall(
        'SELECT title FROM changeprice')
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(cart)
    markup.add(about_Us)
    markup.add(connect_us)
    markup.add(reviews_us)

    await message.answer(f'Меню. Если нужна помощь в пользовании ботом введите команду /help'
                         f'\n Оплата заказа производится картой или наличными при получении.'
                         f'\nДоставка курьером стоит {text} рублей', reply_markup=markup)
