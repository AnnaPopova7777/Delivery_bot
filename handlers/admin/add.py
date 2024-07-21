import types

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import *
from keyboards.inline.products_from_catalog import rewiews_rating_del_admin, reviews_cb

from states import ProductState, CategoryState
from aiogram.types.chat import ChatActions
# from handlers.user.menu import settings
from loader import dp, db, bot
from filters import IsAdmin
from hashlib import md5

from states.product_state import AnnouncementState, DelPriceState

category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

add_product = '➕ Добавить товар'
delete_category = '🗑️ Удалить категорию'
back_list_category = 'Вернуться к списку категорий'


@dp.message_handler(commands='settings')
async def process_settings(message: Message):
    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category', ))

    markup.add(InlineKeyboardButton(
        '+Сделать объявление', callback_data='add_announcement', ))
    markup.add(InlineKeyboardButton(
        '-Удалить объявления', callback_data='del_announcement', ))
    markup.add(InlineKeyboardButton(
        'Изменить стоимость доставки', callback_data='change_del_price', ))
    rkb = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    rkb.add('Посмотреть отзывы')

    await message.answer('Настройки:', reply_markup=markup)
    await message.answer('Настройки:', reply_markup=rkb)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    category_idx = callback_data['id']

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (category_idx,))

    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


@dp.callback_query_handler(IsAdmin(), text='change_del_price')
async def change_del_price_handler(query: CallbackQuery):
    db.query('DELETE FROM changeprice')
    await query.message.answer('Введите новую стоимость доставки')
    await DelPriceState.title.set()


@dp.message_handler(IsAdmin(), state=DelPriceState.title)
async def set_announcement_title_handler(message: Message, state: FSMContext):
    change_price = message.text
    idx = md5(change_price.encode('utf-8')).hexdigest()
    db.query('INSERT INTO changeprice VALUES (?, ?)', (idx, change_price))

    await message.answer('Цена изменена!')
    await state.finish()
    await process_settings(message)


# category


@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await CategoryState.title.set()
    markup_back = ReplyKeyboardMarkup(resize_keyboard=True)
    markup_back.add('Назад')
    await query.message.answer('Название категории?', reply_markup=markup_back)


@dp.message_handler(IsAdmin(), text='Назад', state=CategoryState.title)
async def process_cancel_category(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):
    category = message.text
    idx = md5(category.encode('utf-8')).hexdigest()
    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))

    await state.finish()
    await process_settings(message)


@dp.callback_query_handler(IsAdmin(), text='add_announcement')
async def add_announcement_callback_handler(query: CallbackQuery):
    await query.message.answer('Напишите объявление (будет отображаться у администратора'
                               ' и у пользователя при нажатии команды start)')
    await AnnouncementState.title.set()


@dp.message_handler(IsAdmin(), state=AnnouncementState.title)
async def sets_announcement_title_handler(message: Message, state: FSMContext):
    announ_t = message.text
    idx = md5(announ_t.encode('utf-8')).hexdigest()
    db.query('INSERT INTO announcement VALUES (?, ?)', (idx, announ_t))

    await message.answer('Объявление создано!')
    await state.finish()
    await process_settings(message)


@dp.callback_query_handler(IsAdmin(), text='del_announcement')
async def del_announcement_callback_handler(query: CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        'Да', callback_data='delete_announ', ))
    markup.add(InlineKeyboardButton(
        'Нет', callback_data='del_back', ))
    text = db.fetchall(
        'SELECT title FROM announcement')
    await query.message.answer(f'Вот все ваши объявления. Желаете удалить?\n'
                               f'{text}', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), text='delete_announ')
async def del_announcements_callback(query: CallbackQuery):
    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category', ))
    markup.add(InlineKeyboardButton(
        '+Сделать объявление', callback_data='add_announcement', ))
    markup.add(InlineKeyboardButton(
        '-Удалить объявления', callback_data='del_announcement', ))
    db.query('DELETE FROM announcement')
    await query.message.answer('Готово!', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), text='del_back')
async def back_announcement_callback_handler(query: CallbackQuery):
    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category', ))
    markup.add(InlineKeyboardButton(
        '+Сделать объявление', callback_data='add_announcement', ))
    markup.add(InlineKeyboardButton(
        '-Удалить объявления', callback_data='del_announcement', ))
    await query.message.answer('Отменено', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if 'category_index' in data.keys():
            idx = data['category_index']

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=?)', (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)


# add product


@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer('Название?', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    await process_add_product(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await ProductState.next()
    await message.answer('Описание?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):
    await ProductState.title.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить название с <b>{data['title']}</b>? (Введите новое название)",
                             reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['body'] = message.text

    await ProductState.next()
    await message.answer('Фото?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):
    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()

    async with state.proxy() as data:
        data['image'] = downloaded_file

    await ProductState.next()
    await message.answer('Цена?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text == back_message:

        await ProductState.body.set()

        async with state.proxy() as data:

            await message.answer(f"Изменить описание с <b>{data['body']}</b>? (Введите новое описание)",
                                 reply_markup=back_markup())

    else:

        await message.answer('Вам нужно прислать фото товара.')


@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):
    if message.text == back_message:

        await ProductState.image.set()

        async with state.proxy() as data:

            await message.answer("Другое изображение? (Отправьте новое изображение)", reply_markup=back_markup())

    else:

        await message.answer('Укажите цену в виде числа!')


@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

        title = data['title']
        body = data['body']
        price = data['price']

        await ProductState.next()
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = check_markup()

        await message.answer_photo(photo=data['image'],
                                   caption=text,
                                   reply_markup=markup)


@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message, all_right_message],
                    state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('Такого варианта не было.')


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    await ProductState.price.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>? (Введите новую цену)",
                             reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm_fin(message: Message, state: FSMContext):
    async with state.proxy() as data:
        title = data['title']
        body = data['body']
        image = data['image']
        price = data['price']

        tag = db.fetchone(
            'SELECT title FROM categories WHERE idx=?', (data['category_index'],))[0]
        idx = md5(' '.join([title, body, price, tag]
                           ).encode('utf-8')).hexdigest()

        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                 (idx, title, body, image, int(price), tag))

    await state.finish()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


# delete product


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict):
    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Удалено!')
    await query.message.delete()


async def show_products(m, products, category_idx):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, image, price, tag in products:
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            '🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete')))

        await m.answer_photo(photo=image,
                             caption=text,
                             reply_markup=markup)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(add_product)
    markup.add(delete_category)

    await m.answer('Хотите что-нибудь добавить или удалить?', reply_markup=markup)


async def show_all_rewiews_admin(m, rewiews) -> None:
    for rewiew in rewiews:
        await m.answer(text=f'<b>{rewiew[1]}</b>',
                       reply_markup=rewiews_rating_del_admin(rewiew[0]))


@dp.message_handler(IsAdmin(), text='Посмотреть отзывы')
async def rewiews_user_admin(query: CallbackQuery):
    rewiew = db.fetchall("SELECT * FROM rewiews_users")

    if not rewiew:
        await query.answer('Пока что отзывов нет')

    await show_all_rewiews_admin(query, rewiew)


@dp.callback_query_handler(IsAdmin(), reviews_cb.filter(action='delete_rew'))
async def rewiews_user_del(query: CallbackQuery, callback_data: dict):
    review_idx = callback_data['id']
    db.query('DELETE FROM rewiews_users WHERE idx=?', (review_idx,))
    await query.answer('Отзыв удален')
    await query.message.delete()


