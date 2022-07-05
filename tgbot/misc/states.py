from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()
    sell = State()
    buy = State()


class Buy(StatesGroup):
    tags = State()
    name = State()
    description = State()
    price = State()
    photo = State()
    contact = State()


class Sell(StatesGroup):
    tags = State()
    name = State()
    description = State()
    price = State()
    photo = State()
    contact = State()

    done = State()
