from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()

    my_ads = State()

    admin = State()
    restriction = State()




class Buy(StatesGroup):
    tags = State()
    description = State()
    price = State()
    contact = State()

    title = State()
    photo = State()

    preview = State()
    confirm = State()
    done = State()


class Sell(StatesGroup):
    tags = State()
    description = State()
    price = State()
    contact = State()

    title = State()
    photo = State()

    preview = State()
    confirm = State()
    done = State()
