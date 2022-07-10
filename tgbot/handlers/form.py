from typing import Union, Dict, Any

import phonenumbers
from aiogram import types
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Sell, Buy

REQUIRED_FIELDS = {
    "sell": {"description", "price", "contacts", "tags"},
    "buy": {"description", "contacts", "tags"},
}

to_state: dict = {
    "sell": Sell,
    "buy": Buy
}


def get_active_section(state: str):
    sections = {
        'title': 'Заголовок',
        'description': 'Описание',
        'price': 'Цена',
        'contact': 'Контакты',
        'photo': 'Картинка',
        'tags': 'Теги'
    }
    return sections.get(state)


def get_current_file_id(photos: list[str] = None, page: int | None = None) -> None | str:
    if not all([photos, page]):
        return None
    else:
        return photos[page-1]


async def clear_photo_pagination_data(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    widget_data.pop('current_page', None)
    widget_data.pop('photos_len', None)


async def change_photo(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    current_page: int = widget_data.get('current_page')
    photos_len: int = widget_data.get('photos_len')

    action: str = button.widget_id

    if action == 'left_photo':
        current_page -= 1
        if current_page < 1:
            current_page = photos_len
    elif action == 'right_photo':
        current_page += 1
        if current_page > photos_len:
            current_page = 1

    widget_data['current_page'] = current_page


async def change_page(_obj: Union[types.CallbackQuery, types.Message], button: Union[Button, TextInput],
                      manager: DialogManager, *_text):
    action: str = button.widget_id
    current_state = manager.current_context().state.state.split(":")[-1]
    states_group = manager.current_context().state.state.split(":")[0].lower()

    if action == 'left':
        if current_state == 'tags':
            await manager.dialog().switch_to(to_state.get(states_group).photo)
        else:
            await manager.dialog().back()
    elif action == 'right':
        if current_state == 'photo':
            await manager.dialog().switch_to(to_state.get(states_group).tags)
        else:
            await manager.dialog().next()
    elif current_state != 'photo':
        await manager.dialog().next()


async def add_tag(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    tag = button.widget_id

    tags = {
        "childs_world": "детский_мир",
        "real_estate": "недвижимость",
        "transport": "транспорт",
        "work": "работа",
        "animals": "животные",
        "house_garden": "дом_и_сад",
        "electronics": "электроника",
        "services": "услуги",
        "fashion_style": "мода_и_стиль",
        "sport": "спорт",
    }

    tags_data = manager.current_context().widget_data.setdefault("tags", [])
    tags_data.append(tags.get(tag))


async def currency_selected(_call: types.CallbackQuery, _widget: Any, manager: DialogManager, item_id: str):
    currencies = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}
    manager.current_context().widget_data['currency'] = currencies[item_id]


async def delete_tag(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.pop('tag', None)


def tag_is_empty(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is None


def tag_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is not None


# Restrictions
def fixed_size_64(text: str):
    if len(text) > 128:
        raise ValueError


def fixed_size_1024(text: str):
    if len(text) > 1024:
        raise ValueError


async def invalid_input(message: types.Message, _widget: TextInput, manager: DialogManager):
    state = manager.current_context().state
    manager.show_mode = ShowMode.EDIT
    match state:
        case Sell.title | Buy.title:
            await message.answer("Максимальная длина заголовка товара или услуг 64 символов."
                                 " Попробуйте еще раз.")
        case Sell.description | Buy.description:
            await message.answer("Максимальная длина описания товара или услуг 128 символов."
                                 " Попробуйте еще раз.")


async def price_validator(message: types.Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    try:
        price: float = (float(message.text).is_integer() and int(message.text)) or round(float(message.text), 2)

        if not (price > 0.01):
            raise ValueError

        manager.current_context().widget_data["price"] = price
        await dialog.next()
    except ValueError:
        manager.show_mode = ShowMode.EDIT
        await message.answer("Цена должна быть числом и быть больше 0.01. Попробуйте еще раз.")


class RepeatedNumberError(Exception):
    pass


async def contact_validator(message: types.Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    try:
        phone_number = message.text
        contact_data = manager.current_context().widget_data.setdefault('contacts', [])
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        parsed_number = phonenumbers.parse(phone_number)
        if phone_number in contact_data:
            raise RepeatedNumberError
        # shallow check whether the phone number is invalid
        if phonenumbers.is_possible_number(parsed_number):
            # deep check whether the phone number is invalid
            if phonenumbers.is_valid_number(parsed_number):
                contact_data.append(phone_number.replace(" ", ""))
                await dialog.next()
            else:
                raise ValueError
        else:
            raise ValueError

    except phonenumbers.NumberParseException:
        # the input is really gibberish
        manager.show_mode = ShowMode.EDIT
        await message.answer("Вы ввели не валидный номер! Попробуйте еще раз.")
    except ValueError:
        manager.show_mode = ShowMode.EDIT
        await message.answer("Вы ввели не валидный номер! Попробуйте еще раз.")
    except RepeatedNumberError:
        manager.show_mode = ShowMode.EDIT
        await message.answer("Вы уже ввели этот номер.")


async def pic_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
    match message.content_type:
        case types.ContentType.PHOTO:
            photo = message.photo[-1]
            photos_data = manager.current_context().widget_data.setdefault('photos_ids', [])
            photos_data.append(photo.file_id)
        case _:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")


# Buttons and dialogs
async def set_default(_, dialog_manager: DialogManager):
    await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id="UAH")
    dialog_manager.current_context().widget_data['currency'] = "₴"


async def get_currency_data(**_kwargs):
    currencies = [
        ('$', 'USD'),
        ('€', 'EUR'),
        ('₽', 'RUB'),
        ('₴', 'UAH')
    ]
    return {'currencies': currencies}


async def check_required_fields(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    state = manager.current_context().state.state.split(':')[0].lower()

    if REQUIRED_FIELDS.get(state).issubset(widget_data.keys()):
        await manager.switch_to(to_state.get(state).confirm)
    else:
        await call.answer("Вы не заполнили все обязательные поля.")


def tag_buttons():
    buttons = Group(
        Button(text=Const("#️⃣Детский мир"), id="childs_world", on_click=add_tag),
        Button(text=Const("#️⃣Недвижимость"), id="real_estate", on_click=add_tag),
        Button(text=Const("#️⃣Транспорт"), id="transport", on_click=add_tag),
        Button(text=Const("#️⃣Работа"), id="work", on_click=add_tag),
        Button(text=Const("#️⃣Животные"), id="animals", on_click=add_tag),
        Button(text=Const("#️⃣Дом и сад"), id="house_garden", on_click=add_tag),
        Button(text=Const("#️⃣Электроника"), id="electronics", on_click=add_tag),
        Button(text=Const("#️⃣Услуги"), id="services", on_click=add_tag),
        Button(text=Const("#️⃣Мода и стиль"), id="fashion_style", on_click=add_tag),
        Button(text=Const("#️⃣Спорт"), id="sport", on_click=add_tag),
        width=2,
        when=tag_is_empty
    )

    return buttons
