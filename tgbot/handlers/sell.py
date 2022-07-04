import operator
from typing import Any

from aiogram import types
from aiogram.utils.markdown import hunderline, hbold, hcode, hitalic
from aiogram_dialog import Dialog, Window, DialogManager, ChatEvent
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Radio, Select, Group, Checkbox, ManagedCheckboxAdapter
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.states import Sell


async def get_sell_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    state = dialog_manager.current_context().state.state.split(":")[-1]

    # entered data from user
    tags = data.get('tags') if data.get('tags') else '➖'
    name = hbold(data.get('name')) if data.get('name') else '➖'
    description = hitalic(data.get('description')) if data.get('description') else '➖'
    price = hcode(data.get('price')) if data.get('price') else '➖'
    photo = data.get('photo') if data.get('photo') else '➖'
    contact = hcode(data.get('contact')) if data.get('contact') else '➖'

    # identifying the active section
    ttags = state == 'tags' and hunderline('Теги') or 'Теги'
    tname = state == 'name' and hunderline('Название товара или услуг') or 'Название товара или услуг'
    tdescription = state == 'description' and hunderline('Описание товара или услуг') or 'Описание товара или услуг'
    tprice = state == 'price' and hunderline('Цена') or 'Цена'
    tnegotiable = state == 'negotiable' and hunderline('Торг уместен') or 'Торг уместен'
    tphoto = state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'
    tcontact = state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'

    text = (f"1. {ttags}: \n"
            f"2. {tname}: \n"
            f"3. {tdescription}: \n"
            f"4. {tprice}: \n"
            f"5. {tnegotiable}: \n"
            f"6. {tphoto}: \n"
            f"7. {tcontact}: \n")

    return {"sell_text": text}


async def set_default(_, dialog_manager: DialogManager):
    await dialog_manager.dialog().find('sections').set_checked(event="", item_id="1")


async def switch_to_next(_message: types.Message, _widget: TextInput, manager: DialogManager,
                         _data: Any):
    sections = {
        'name': '1',
        'description': '2',
        'price': '3',
        'photo': '4',
        'contact': '5'
    }

    if manager.current_context().state.state.split(":")[-1] != 'contact':
        await manager.dialog().next()

    section = sections.get(manager.current_context().state.state.split(":")[-1])
    await manager.dialog().find('sections').set_checked(event="", item_id=section)


async def get_sections(**_kwargs):
    sections = [
        ("Название", '1'),
        ("Описание", '2'),
        ("Цена", '3'),
        ("Картинка", '4'),
        ("Контакт", '5'),
    ]
    return {"sections": sections}


async def change_section_sell(_call: types.CallbackQuery, _button: ManagedWidgetAdapter[Select], manager: DialogManager,
                              item_id: str):
    if item_id == '1':
        section = Sell.name
    elif item_id == '2':
        section = Sell.description
    elif item_id == '3':
        section = Sell.price
    elif item_id == '4':
        section = Sell.photo
    else:
        section = Sell.contact
    await manager.dialog().switch_to(section)


async def change_bargain(event: ChatEvent, checkbox: ManagedCheckboxAdapter, manager: DialogManager):
    print(checkbox.is_checked())
    print(manager.dialog().find("negotiable").is_checked())
    manager.current_context().widget_data['negotiable'] = checkbox.is_checked()
    print(event)
    print(checkbox)


def get_radio_buttons():
    buttons = Group(
        Radio(
            Format("🔘 {item[0]}"),
            Format("⚪️ {item[0]}"),
            id="sections",
            item_id_getter=operator.itemgetter(1),
            items="sections",
            on_click=change_section_sell
        ),
        Checkbox(
            checked_text=Const("✓ Договорная"),
            unchecked_text=Const("Договорная"),
            id="negotiable",
            on_state_changed=change_bargain,
            default=False
        ),
        width=2)
    return buttons


sell_dialog = Dialog(
    Window(
        Format(text="{sell_text}", when="sell_text"),
        get_radio_buttons(),
        TextInput(id="name", on_success=switch_to_next),
        state=Sell.name,
        getter=[get_sell_text, get_sections]
    ),
    Window(
        Format(text="123"),
        get_radio_buttons(),
        TextInput(id="description", on_success=switch_to_next),
        state=Sell.description,
        getter=[get_sections]
    ),
    Window(
        Format(text="123"),
        get_radio_buttons(),
        TextInput(id="price", on_success=switch_to_next),
        state=Sell.price,
        getter=[get_sections]
    ),
    Window(
        Format(text="123"),
        get_radio_buttons(),
        TextInput(id="photo", on_success=switch_to_next),
        state=Sell.photo,
        getter=[get_sections]
    ),
    Window(
        Format(text="123"),
        get_radio_buttons(),
        TextInput(id="contact", on_success=switch_to_next),
        state=Sell.contact,
        getter=[get_sections]
    ),
    on_start=set_default
)
