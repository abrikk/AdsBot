import copy
import operator
from typing import Union, Dict, Any

import flag
import phonenumbers
from aiogram import types, Bot
from aiogram.types import MediaGroup
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Group, Row, Button, SwitchTo, \
    Start, Checkbox, Radio
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.config import Config
from tgbot.misc.ad import SalesAd
from tgbot.misc.media_widget import DynamicMediaFileId
from tgbot.misc.states import Sell, Main

REQUIRED_FIELDS = {"description", "price", "contacts", "tags"}


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


async def get_sell_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    sell_data = copy.deepcopy(data)
    sell_data.pop('currency_code', None)

    state = dialog_manager.current_context().state.state.split(":")[-1]

    sell_ad = SalesAd(state=state, **sell_data)

    return {"sell_text": sell_ad.to_text(), "page": get_active_section(state)}


async def get_preview_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    sell_data = copy.deepcopy(widget_data)

    sell_data.pop('currency_code', None)
    sell_data.pop('current_page', None)
    sell_data.pop('photos_len', None)

    sell_ad = SalesAd(**sell_data)

    if sell_ad.photos_ids:
        current_page = widget_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(sell_ad.photos_ids) > 1:
        widget_data['photos_len'] = len(sell_ad.photos_ids)

    return {"preview_text": sell_ad.preview(), "file_id": get_current_file_id(sell_ad.photos_ids, current_page),
            "show_scroll": len(sell_ad.photos_ids) > 1,
            "photo_text": len(sell_ad.photos_ids) > 1 and current_page and f"{current_page}/{len(sell_ad.photos_ids)}"}


async def get_confirm_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data

    sell_data = copy.deepcopy(widget_data)
    sell_data.pop('currency_code', None)
    sell_data.pop('current_page', None)
    sell_data.pop('photos_len', None)

    state = dialog_manager.current_context().state.state.split(":")[-1]

    sell_ad = SalesAd(state=state, **sell_data)

    if sell_ad.photos_ids:
        current_page = widget_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(sell_ad.photos_ids) > 1:
        widget_data['photos_len'] = len(sell_ad.photos_ids)

    return {"confirm_text": sell_ad.confirm(), "file_id": get_current_file_id(sell_ad.photos_ids, current_page),
            "show_scroll": len(sell_ad.photos_ids) > 1,
            "photo_text": len(sell_ad.photos_ids) > 1 and current_page and f"{current_page}/{len(sell_ad.photos_ids)}"}


async def on_confirm(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    obj = manager.event
    bot: Bot = obj.bot
    widget_data = manager.current_context().widget_data
    config: Config = manager.data.get("config")

    sell_data = copy.deepcopy(widget_data)
    sell_data.pop('currency_code', None)
    sell_data.pop('current_page', None)
    sell_data.pop('photos_len', None)

    sell_ad = SalesAd(**sell_data)

    album = MediaGroup()

    for file_id in sell_ad.photos_ids[:-1]:
        album.attach_photo(photo=file_id)

    album.attach_photo(photo=sell_ad.photos_ids[-1], caption=sell_ad.post())

    await bot.send_media_group(chat_id=config.tg_bot.channel_id,
                               media=album)


async def check_required_fields(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data = manager.current_context().widget_data

    if REQUIRED_FIELDS.issubset(widget_data.keys()):
        await manager.switch_to(Sell.confirm)
    else:
        await call.answer("Вы не заполнили все обязательные поля.")


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

    if action == 'left':
        if current_state == 'tags':
            await manager.dialog().switch_to(Sell.photo)
        else:
            await manager.dialog().back()
    elif action == 'right':
        if current_state == 'photo':
            await manager.dialog().switch_to(Sell.tags)
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
        case Sell.title:
            await message.answer("Максимальная длина заголовка товара или услуг 64 символов."
                                 " Попробуйте еще раз.")
        case Sell.description:
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


def get_widgets():
    buttons = (
        Format(text="{sell_text}", when="sell_text"),
        Row(
            Button(text=Const("<<"), id="left", on_click=change_page),
            Button(text=Format(text="{page}"), id="page"),
            Button(text=Const(">>"), id="right", on_click=change_page)
        ),
        Row(
            Start(text=Const("🔚 Назад"), id="back_to_main", state=Main.main,
                  mode=StartMode.RESET_STACK),
            SwitchTo(text=Const("👁"), id="preview", state=Sell.preview),
            Button(text=Const("Опубликовать"), id="post", on_click=check_required_fields)
        )
    )
    return buttons


sell_dialog = Dialog(
    Window(
        Button(
            text=Const("Удалить тег"),
            id="delete_tag",
            when=tag_exist,
            on_click=delete_tag
        ),
        tag_buttons(),
        *get_widgets(),
        state=Sell.tags,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(
            id="description",
            type_factory=fixed_size_1024,
            on_error=invalid_input,
            on_success=change_page
        ),
        state=Sell.description,
        getter=[get_sell_text]
    ),
    Window(
        Checkbox(
            checked_text=Const("Торг уместен: Да ✅"),
            unchecked_text=Const("Торг уместен: Нет ❌"),
            id="negotiable",
            default=False
        ),
        Radio(
            checked_text=Format("✔️ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="currency_code",
            item_id_getter=operator.itemgetter(1),
            items="currencies",
            on_click=currency_selected
        ),
        *get_widgets(),
        MessageInput(
            func=price_validator,
            content_types=types.ContentType.TEXT
        ),
        state=Sell.price,
        getter=[get_sell_text, get_currency_data]
    ),
    Window(
        *get_widgets(),
        MessageInput(
            func=contact_validator,
            content_types=types.ContentType.TEXT
        ),
        state=Sell.contact,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(
            id="title",
            type_factory=fixed_size_64,
            on_error=invalid_input,
            on_success=change_page),
        state=Sell.title,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        MessageInput(
            pic_validator,
            content_types=[types.ContentType.ANY]
        ),
        state=Sell.photo,
        getter=[get_sell_text]
    ),
    Window(
        Format(
            text="{preview_text}",
            when="preview_text"),
        Row(
            Button(Const("<<"), id="left_photo", on_click=change_photo),
            Button(Format(text="{photo_text}", when="photo_text"), id="photo_pos"),
            Button(Const(">>"), id="right_photo", on_click=change_photo),
            when="show_scroll"
        ),
        DynamicMediaFileId(
            file_id=Format(text='{file_id}'),
            when="file_id"),
        SwitchTo(
            text=Const("Назад"),
            id="back_to_edit",
            state=Sell.tags,
            on_click=clear_photo_pagination_data),
        state=Sell.preview,
        getter=[get_preview_text]
    ),
    Window(
        Format(text="{confirm_text}", when="confirm_text"),
        Row(
            Button(Const("<<"), id="left_photo", on_click=change_photo),
            Button(Format(text="{photo_text}", when="photo_text"), id="photo_pos"),
            Button(Const(">>"), id="right_photo", on_click=change_photo),
            when="show_scroll"
        ),
        DynamicMediaFileId(
            file_id=Format(text='{file_id}'),
            when="file_id"),
        Button(
            text=Const("✅ Да"),
            id="yes",
            on_click=on_confirm
        ),
        Row(
          SwitchTo(
              text=Const("Назад"),
              id="back_to_edit",
              state=Sell.tags,
              on_click=clear_photo_pagination_data),
          Start(text=Const("В главное меню"), id="to_main", state=Main.main, mode=StartMode.RESET_STACK),
        ),
        state=Sell.confirm,
        getter=[get_confirm_text]
    ),
    on_start=set_default
)
