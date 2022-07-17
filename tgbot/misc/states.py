from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()


class AdminPanel(StatesGroup):
    admin = State()
    restriction = State()
    tag = State()
    add_tag = State()
    del_tag = State()


class Buy(StatesGroup):
    tags = State()
    title = State()
    description = State()
    photo = State()
    price = State()
    contact = State()


class Sell(StatesGroup):
    tags = State()
    title = State()
    description = State()
    photo = State()
    price = State()
    contact = State()


class Preview(StatesGroup):
    preview = State()


class ConfirmAd(StatesGroup):
    confirm = State()


class ShowUser(StatesGroup):
    true = State()


class MyAds(StatesGroup):
    show = State()


class ShowMyAd(StatesGroup):
    true = State()
    confirm_delete = State()


class EditSell(StatesGroup):
    tags = State()
    title = State()
    description = State()
    photo = State()
    price = State()
    contact = State()


class EditBuy(StatesGroup):
    tags = State()
    title = State()
    description = State()
    photo = State()
    price = State()
    contact = State()
