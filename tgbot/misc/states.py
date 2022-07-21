from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()
    make_ad = State()


class AdminPanel(StatesGroup):
    admin = State()


class ManageRestrictions(StatesGroup):
    main = State()


class ManageTags(StatesGroup):
    main = State()
    add_category = State()
    delete_categories = State()
    tags = State()
    add_del_tags = State()
    confirm_tags = State()


class Form(StatesGroup):
    category = State()
    tag = State()
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
    show_edit = State()
    edit = State()
    confirm_delete = State()
