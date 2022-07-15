import copy
from typing import Union, Dict, Any

import phonenumbers
from aiogram import types
from aiogram_dialog import DialogManager, ShowMode, Data, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, Start
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Sell, Buy, Preview, ConfirmAd, Main
from tgbot.models.post_ad import PostAd
from tgbot.services.db_commands import DBCommands

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


def when_not(key: str):
    def f(data, _whenable, _manager):
        return not data.get(key)

    return f


def get_current_file_id(photos: list[str] = None, page: int | None = None) -> None | str:
    if not all([photos, page]):
        return None
    else:
        return photos[page - 1]


async def on_back(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    start_data = manager.current_context().start_data
    print(1, 1, start_data)
    start_data.pop("state_class", None)
    start_data.pop('current_page', None)
    start_data.pop('photos_len', None)
    print(0, 0, start_data)

    await manager.done(start_data)


async def change_photo(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    data = manager.current_context().start_data
    current_page: int = data.get('current_page')
    photos_len: int = data.get('photos_len')

    action: str = button.widget_id

    if action == 'left_photo':
        current_page -= 1
        if current_page < 1:
            current_page = photos_len
    elif action == 'right_photo':
        current_page += 1
        if current_page > photos_len:
            current_page = 1

    data['current_page'] = current_page


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


async def add_tag(_call: types.CallbackQuery, _widget: ManagedWidgetAdapter[Select], manager: DialogManager,
                  tag: str):
    tag_limit: int = manager.current_context().widget_data.get('tag_limit')
    tags_data = manager.current_context().widget_data.setdefault("tags", [])
    tags_data.append(tag.removeprefix('#️⃣'))
    if tag_limit == len(tags_data):
        await manager.dialog().next()


async def currency_selected(_call: types.CallbackQuery, _widget: Any, manager: DialogManager, item_id: str):
    currencies = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}
    manager.current_context().widget_data['currency'] = currencies[item_id]


async def delete_tag(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.get("tags").pop()


def tag_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    tags: list = manager.current_context().widget_data.get('tags')
    return tags is not None and len(tags) > 0


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
    contact_limit: int = manager.current_context().widget_data.get('contact_limit')
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
                if len(contact_data) < contact_limit:
                    contact_data.append(phone_number.replace(" ", ""))
                else:
                    contact_data[-1] = phone_number.replace(" ", "")
                if len(contact_data) == contact_limit:
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
    pic_limit: int = manager.current_context().widget_data.get('pic_limit')
    match message.content_type:
        case types.ContentType.PHOTO:
            photo = message.photo[-1]
            photos_data = manager.current_context().widget_data.setdefault('photos_ids', [])
            if len(photos_data) < pic_limit:
                photos_data.append(photo.file_id)
            else:
                photos_data[-1] = photo.file_id
        case _:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")


# Buttons and dialogs
async def set_default(_, dialog_manager: DialogManager):
    await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id="UAH")
    dialog_manager.current_context().widget_data['currency'] = "₴"


async def set_edit_default(_, dialog_manager: DialogManager):
    session = dialog_manager.data.get('session')
    db: DBCommands = dialog_manager.data.get('db_commands')
    post_ad: PostAd = await session.get(PostAd, int(dialog_manager.current_context().start_data.get('post_id')))
    dialog_manager.current_context().widget_data['tags'] = [tag.tag_name for tag in post_ad.tags]
    await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id=post_ad.currency_code)
    tag, contact, pic, post = await db.get_values_of_restrictions()
    limits: dict = {
        "tag_limit": tag,
        "contact_limit": contact,
        "pic_limit": pic,
        "post_limit": post
    }

    dialog_manager.current_context().widget_data.update(limits)
    # ToDo deal with bug
    # await dialog_manager.dialog().find('negotiable').set_checked(event=dialog_manager.event, checked=post_ad.negotiable)


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
        state_class = manager.current_context().state.state.split(":")[0]
        widget_data: dict = manager.current_context().widget_data
        print("widget data", widget_data)
        data: dict = copy.deepcopy(widget_data)
        data.pop('sg_tags', None)
        data.update({"state_class": state_class})

        await manager.start(ConfirmAd.confirm, data=data)
    else:
        await call.answer("Вы не заполнили все обязательные поля.")


async def show_preview(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    state_class = manager.current_context().state.state.split(":")[0]
    widget_data: dict = manager.current_context().widget_data
    print(0, widget_data)

    data: dict = copy.deepcopy(widget_data)
    data.pop('currency_code', None)
    data.pop('sg_tags', None)
    data.update({"state_class": state_class})

    print(1, widget_data)

    await manager.start(state=Preview.preview, data=data)


async def process_result(_start_data: Data, result: Any, manager: DialogManager):
    if result:
        print(2, result)
        manager.current_context().widget_data.update(**result)


def get_widgets(where: str = None):
    if where == 'edit':
        btn = "Сохранить"
        btn_id = "save"
    else:
        btn = "Опубликовать"
        btn_id = "post"
    buttons = (
        Format(text="{form_text}", when="form_text"),
        Row(
            Button(text=Const("<<"), id="left", on_click=change_page),
            Button(text=Format(text="{page}"), id="page"),
            Button(text=Const(">>"), id="right", on_click=change_page)
        ),
        Row(
            Start(
                text=Const("🔚 Назад"),
                id="back_to_main",
                state=Main.main,
                mode=StartMode.RESET_STACK
            ),
            Button(
                text=Const("👁"),
                id="preview",
                on_click=show_preview
            ),
            Button(
                text=Const(btn),
                id=btn_id,
                on_click=check_required_fields
            )
        )
    )
    return buttons
