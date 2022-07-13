from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()
    my_ads = State()


class AdminPanel(StatesGroup):
    admin = State()
    restriction = State()
    tag = State()
    add_tag = State()
    del_tag = State()


class Buy(StatesGroup):
    tags = State()
    description = State()
    contact = State()

    price = State()
    title = State()
    photo = State()


class Sell(StatesGroup):
    tags = State()
    description = State()
    price = State()
    contact = State()

    title = State()
    photo = State()


class Preview(StatesGroup):
    preview = State()


class ConfirmAd(StatesGroup):
    confirm = State()


class ShowUser(StatesGroup):
    true = State()
