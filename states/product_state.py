from aiogram.dispatcher.filters.state import StatesGroup, State


class ProductState(StatesGroup):
    title = State()
    body = State()
    image = State()
    price = State()
    confirm = State()


class CategoryState(StatesGroup):
    title = State()


class AnnouncementState(StatesGroup):
    title = State()


class DelPriceState(StatesGroup):
    title = State()


class ReviewsState(StatesGroup):
    title_r = State()
