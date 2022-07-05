from typing import Union, Dict

from aiogram import types
from aiogram.utils.markdown import hunderline, hbold, hcode, hitalic
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Group, Row, Button, SwitchTo, \
    Start
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.when import Whenable

from tgbot.misc.states import Sell, Main


def get_active_section(state: str):
    sections = {
        'tags': 'Теги',
        'name': 'Название',
        'description': 'Описание',
        'price': 'Цена',
        'photo': 'Картинка',
        'contact': 'Контакты'
    }
    return sections.get(state)


def make_tags(tag: str, where: str) -> str:
    tags = {
        "sell": "#продам",
        "buy": "#куплю",
        "extra": tag and "#" + tag
    }
    if tag:
        return f"{tags.get(where)}, {tags.get('extra')}"
    else:
        return tags.get(where)


async def get_sell_text(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.current_context().widget_data
    print(data)
    state = dialog_manager.current_context().state.state.split(":")[-1]

    # entered data from user
    tags: str = make_tags(tag=data.get('tag'), where="sell")
    name: str = data.get('name') or '➖'
    description: str = data.get('description') or '➖'
    price = data.get('price') or '➖'
    photo = data.get('photo') or '➖'
    contact = data.get('contact') or '➖'

    # identifying the active section
    ttags = state == 'tags' and hunderline('Теги') or 'Теги'
    tname = state == 'name' and hunderline('Название товара или услуг') or 'Название товара или услуг'
    tdescription = state == 'description' and hunderline('Описание товара или услуг') or 'Описание товара или услуг'
    tprice = state == 'price' and hunderline('Цена') or 'Цена'
    tphoto = state == 'photo' and hunderline('Фото (опционально)') or 'Фото (опционально)'
    tcontact = state == 'contact' and hunderline('Контактные данные') or 'Контактные данные'

    text = (f"1. {ttags}: {tags}\n"
            f"2. {tname}: {hbold(name)}\n"
            f"3. {tdescription}: {hitalic(description)}\n"
            f"4. {tprice}: {hcode(price)}\n"
            f"5. {tphoto}: {photo}\n"
            f"6. {tcontact}: {hcode(contact)}\n")

    match state:
        case 'tags':
            if not data.get('tag'):
                text = '#️⃣  Выберите тег своего товара или услуг нажав по кнопке ' \
                       'ниже:\n\n' + text
            else:
                text = '#️⃣  Чтобы изменить тег товара или услуг, сначала удалите текущий ' \
                       'тег, затем установите новый.\n\n' + text
        case 'name':
            if not data.get('name'):
                text = '🔡 Введите название товара или услуг:\n\n' + text
            else:
                text = '🔡 Чтобы изменить название товара или услуг, просто отправьте' \
                       'новое название.\n\n' + text
        case 'description':
            if not data.get('description'):
                text = '📝 Введите описание товара или услуг:\n\n' + text
            else:
                text = '📝 Чтобы изменить описание товара или услуг, просто отправьте' \
                       'новое описание.\n\n' + text
        case 'price':
            if not data.get('price'):
                text = '💸 Введите цену товара или услуг:\n\n' + text
            else:
                text = '💸 Чтобы изменить цену товара или услуг, просто отправьте' \
                       'новую цену.\n\n' + text
        case 'photo':
            if not data.get('quantity'):
                text = '🖼 Отправьте картинки товара или услуг по одному ' \
                       '(этот раздел можно пропустить).\n' \
                       'P.s. Максимальное количество картинок - <code>5</code>:\n\n' + text
            else:
                text = '🖼 Чтобы изменить картинку товара или услуг, просто отправьте' \
                       'новую картинку, а чтобы удалить картинку нажми на ' \
                       'кнопку ниже.\n\n' + text
        case _:
            if not data.get('contact'):
                text = '📞 Введите номер телефона который будет отображаться в объявлении' \
                       ' или нажмите на кнопку ' \
                       '\"Отправить контакт\":\n\n' + text
            else:
                text = '📞 Чтобы изменить номер телефона, просто отправьте' \
                       'отправьте новый номер.\n\n' + text

    return {"sell_text": text, "page": get_active_section(state)}


async def change_page(_obj: Union[types.CallbackQuery, types.Message], button: Union[Button, TextInput],
                      manager: DialogManager, *_text):
    action: str = button.widget_id
    current_state = manager.current_context().state.state.split(":")[-1]

    if action == 'left':
        if current_state == 'tags':
            await manager.dialog().switch_to(Sell.contact)
        else:
            await manager.dialog().back()
    elif action == 'right':
        if current_state == 'contact':
            await manager.dialog().switch_to(Sell.tags)
        else:
            await manager.dialog().next()
    elif current_state != 'contact':
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

    manager.current_context().widget_data['tag'] = tags.get(tag)


async def delete_tag(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    manager.current_context().widget_data.pop('tag', None)


def tag_is_empty(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is None


def tag_exist(_data: Dict, _widget: Whenable, manager: DialogManager):
    return manager.current_context().widget_data.get('tag') is not None


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
            SwitchTo(text=Const("Готово"), id="done", state=Sell.done)
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
        TextInput(id="name", on_success=change_page),
        state=Sell.name,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(id="description", on_success=change_page),
        state=Sell.description,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(id="price", on_success=change_page),
        state=Sell.price,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(id="photo", on_success=change_page),
        state=Sell.photo,
        getter=[get_sell_text]
    ),
    Window(
        *get_widgets(),
        TextInput(id="contact", on_success=change_page),
        state=Sell.contact,
        getter=[get_sell_text]
    ),
    Window(
        state=Sell.done,
        getter=[get_sell_text]
    )
)
