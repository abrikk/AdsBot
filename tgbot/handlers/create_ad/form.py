import copy
from typing import Dict, Any

from aiogram import types
from aiogram.utils.markdown import hlink
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Form, ConfirmAd
from tgbot.services.db_commands import DBCommands

create_actions: dict = {
    "buy": "Куплю",
    "sell": "Продам",
    "occupy": "Сниму",
    "rent": "Сдам",
    "exchange": "Обменяю",
}


async def change_stage(_call: types.CallbackQuery | types.Message, _button: ManagedWidgetAdapter[Select] | TextInput,
                       manager: DialogManager, stage: Any | str):
    to_stage: dict = {
        "description": Form.description,
        "photo": Form.photo,
        "price": Form.price,
        "contact": Form.contact
    }

    if to_stage.get(stage):
        await manager.switch_to(to_stage.get(stage))
    else:
        await manager.dialog().next()
        stage = manager.current_context().state.state.split(":")[-1]
        await manager.dialog().find('stage').set_checked(event="", item_id=stage)


async def set_default(_, dialog_manager: DialogManager):
    widget_data = dialog_manager.current_context().widget_data
    db: DBCommands = dialog_manager.data.get("db_commands")

    contact, pic, post, max_active = await db.get_values_of_restrictions()
    limits: dict = {
        "contact_limit": contact,
        "pic_limit": pic,
        "post_limit": post
    }

    widget_data.update(limits)

    await dialog_manager.dialog().find('stage').set_checked(event="", item_id="description")
    await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id="UAH")


async def get_currency_data(**_kwargs):
    currencies = [
        ('дол.', 'USD'),
        ('евро', 'EUR'),
        ('руб.', 'RUB'),
        ('грн.', 'UAH')
    ]
    return {'currencies': currencies}


def contact_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    contacts: list = manager.current_context().widget_data.get('contacts')
    return contacts is not None and len(contacts) > 0


def pic_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    photos_id: dict = manager.current_context().widget_data.get('photos')
    return photos_id is not None and len(photos_id) > 0


def fixed_size_1024(text: str):
    if len(text) > 1024:
        raise ValueError


async def invalid_input(message: types.Message, _widget: TextInput, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT
    await message.answer("Максимальная длина описания товара или услуг 1024 символов."
                         " Попробуйте еще раз.")


async def pic_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
    pic_limit: int = manager.current_context().widget_data.get('pic_limit')
    if pic_limit == 0:
        return []

    match message.content_type:
        case types.ContentType.PHOTO:

            photo = message.photo[-1]
            photos = manager.current_context().widget_data.setdefault("photos", {})

            if photo.file_unique_id in photos.keys():
                manager.show_mode = ShowMode.EDIT
                await message.answer("Эта картинка уже имеется в объявление. Отправьте другое.")
                return

            if len(photos) < pic_limit:
                photos[photo.file_unique_id] = photo.file_id
                if len(photos) == pic_limit:
                    state_class = manager.current_context().start_data.get("heading")
                    if state_class == "exchange":
                        await manager.switch_to(Form.contact)
                        await manager.dialog().find('stage').set_checked(event="", item_id="contact")
                    else:
                        await manager.dialog().next()
                        await manager.dialog().find('stage').set_checked(event="", item_id="price")
            else:
                photos.pop(list(photos.keys())[-1], None)
                photos[photo.file_unique_id] = photo.file_id

        case _:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")


async def delete_pic(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    photos_id: dict = widget_data.get('photos', {})
    photos_id.pop(list(photos_id.keys())[-1], None)


async def price_validator(message: types.Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    try:
        text = message.text.replace(" ", "")
        price: int = int(float(text))

        if not (1 <= price <= 999_999_999):
            raise ValueError

        manager.current_context().widget_data["price"] = price
        await dialog.next()
        await manager.dialog().find('stage').set_checked(event="", item_id="contact")
    except ValueError:
        manager.show_mode = ShowMode.EDIT
        await message.answer("Цена должна быть числом и быть в промежутке от <code>1</code> до "
                             "<code>999999999</code>. Попробуйте еще раз.")


async def currency_selected(_call: types.CallbackQuery, _widget: Any, manager: DialogManager, item_id: str):
    currencies = {'USD': 'дол.', 'EUR': 'евро', 'RUB': 'руб.', 'UAH': 'грн.'}
    manager.current_context().widget_data['currency'] = currencies[item_id]


async def contact_validator(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
    contact_limit: int = manager.current_context().widget_data.get('contact_limit')

    phone_number = message.text
    contact_data = manager.current_context().widget_data.setdefault('contacts', [])

    if phone_number in contact_data:
        manager.show_mode = ShowMode.EDIT
        await message.answer("Вы уже ввели этот номер.")
        return

    if len(contact_data) < contact_limit:
        contact_data.append(phone_number)
    else:
        contact_data[-1] = phone_number


async def delete_contact(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.get("contacts").pop()


async def request_confirmation(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data: dict = manager.current_context().widget_data
    data: dict = copy.deepcopy(widget_data)
    data.pop('sg_tag_names', None)
    data.pop('stage', None)
    data.update({"state_class": manager.current_context().start_data.get("heading")})
    await manager.start(ConfirmAd.confirm, data=data)


async def on_back(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    start_data = manager.current_context().start_data
    items_to_pop = ['state_class', 'current_page', 'photos_len']
    for item in items_to_pop:
        start_data.pop(item, None)

    await manager.done(start_data)


async def switch_to_description(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    await manager.dialog().find('stage').set_checked(event="", item_id="description")


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


def get_current_file_id(photos: list[str] = None, page: int | None = None) -> None | str:
    if not all([photos, page]):
        return None
    else:
        return photos[page - 1]


def make_link_to_post(channel_username: str, post_id: int):
    return f"https://t.me/{channel_username}/{post_id}"


def when_not(key: str):
    def f(data, _whenable, _manager):
        return not data.get(key)

    return f


def get_user_mention(id: int, full_name: str, last_name: str = None, username: str = None) -> str:
    name = last_name and " ".join([full_name, last_name]) or full_name
    if username:
        return hlink(name, f"t.me/{username}")
    else:
        return hlink(name, f"tg://user?id={id}")
