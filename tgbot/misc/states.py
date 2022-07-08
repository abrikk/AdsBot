from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()
    sell = State()
    buy = State()


class Buy(StatesGroup):
    title = State()
    description = State()
    price = State()
    contact = State()
    photo = State()
    tags = State()

    preview = State()
    confirm = State()
    done = State()


class Sell(StatesGroup):
    title = State()
    description = State()
    price = State()
    contact = State()
    photo = State()
    tags = State()

    preview = State()
    confirm = State()
    done = State()
