import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, \
    Start, Radio, ScrollingGroup, Group, Back, Next, Column, SwitchTo, Checkbox
from aiogram_dialog.widgets.text import Const, Format

from tgbot.handlers.create_ad.form import change_stage, set_default, get_currency_data, contact_exist, \
    pic_exist, fixed_size_1024, invalid_input, pic_validator, price_validator, currency_selected, delete_contact, \
    contact_validator, request_confirmation, delete_pic, on_back, change_photo, switch_to_description
from tgbot.handlers.create_ad.getters import get_form_text, get_tag_categories, \
    get_tag_names, get_stages, get_show_next, get_can_post, get_confirm_text, on_confirm
from tgbot.misc.media_widget import DynamicMediaFileId
from tgbot.misc.states import Main, ConfirmAd, Form


def get_widgets() -> tuple:
    buttons = (
        Format("{form_text}", when="form_text"),
        Column(
            Radio(
                checked_text=Format("🔘️ {item[1]}"),
                unchecked_text=Format("⚪️ {item[1]}"),
                id="stage",
                item_id_getter=operator.itemgetter(0),
                items="stages",
                on_click=change_stage,
            )
        ),
        Row(
            Start(
                text=Const("🔚 В главное меню"),
                id="to_main",
                state=Main.main
            ),
            SwitchTo(
                text=Const("⬅️ Назад"),
                id="to_previous",
                state=Form.tag,
                on_click=switch_to_description
            )
        ),
        Button(
            text=Const("✅ Опубликовать"),
            id="post",
            on_click=request_confirmation,
            when="can_post"
        )
    )
    return buttons


form_dialog = Dialog(
    Window(
        Const("🔶 Выберите категорию вашего объявления:\n\n"
              "Нет нужной категории? Пишите сюда: @BlackBeard637"),
        Group(
            Radio(
                checked_text=Format("✔️ {item[1]}"),
                unchecked_text=Format("{item[1]}"),
                id="tag_category",
                item_id_getter=operator.itemgetter(0),
                items="tag_categories",
                on_click=Next(),
            ),
            width=2
        ),
        Row(
            Start(
                text=Format("⬅️ {back_btn}", when="back_btn"),
                id="to_previous",
                state=Main.make_ad
            ),
            Next(
                text=Const("Дальше ➡️"),
                when="show_next"
            )
        ),
        state=Form.category,
        getter=get_tag_categories
    ),

    Window(
        Const("🔷 Выберите тип вашего объявления:\n\n"
              "Нет нужной категории? Пишите сюда: @BlackBeard637"),
        ScrollingGroup(
            Radio(
                checked_text=Format("✔️ {item[1]}"),
                unchecked_text=Format("{item[1]}"),
                id="tag_name",
                item_id_getter=operator.itemgetter(0),
                items="tag_names",
                on_click=Next(),
            ),
            id="sg_tag_names",
            width=2,
            height=5,
            when="show_scroll"
        ),
        Group(
            Radio(
                checked_text=Format("✔️ {item[1]}"),
                unchecked_text=Format("{item[1]}"),
                id="tag_name",
                item_id_getter=operator.itemgetter(0),
                items="tag_names",
                on_click=Next(),
            ),
            width=2,
            when="show_group"
        ),
        Row(
            Back(text=Format("⬅️ Назад")),
            Next(text=Const("Дальше ➡️"), when="show_next")
        ),
        state=Form.tag,
        getter=get_tag_names
    ),

    Window(
        *get_widgets(),
        TextInput(
            id="description",
            type_factory=fixed_size_1024,
            on_error=invalid_input,
            on_success=change_stage
        ),
        state=Form.description,
        preview_add_transitions=[Back(), Next(), SwitchTo(Const(""), "hint", Form.price),
                                 SwitchTo(Const(""), "hint", Form.contact)]
    ),

    Window(
        Button(
            text=Const("❌ Удалить фото"),
            id="delete_pic",
            when=pic_exist,
            on_click=delete_pic
        ),
        *get_widgets(),
        MessageInput(
            pic_validator,
            content_types=[types.ContentType.ANY]
        ),
        state=Form.photo,
        preview_add_transitions=[Back(), Next(), SwitchTo(Const(""), "hint", Form.contact),
                                 SwitchTo(Const(""), "hint", Form.tag)]
    ),

    Window(
        Checkbox(
            checked_text=Const("Торг уместен: Да ✅"),
            unchecked_text=Const("Торг уместен: Нет ❌"),
            id="negotiable",
            default=False,
            when="show_checkbox"
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
        state=Form.price,
        getter=get_currency_data,
        preview_add_transitions=[Back(), Next(), SwitchTo(Const(""), "hint", Form.description),
                                 SwitchTo(Const(""), "hint", Form.tag)]
    ),

    Window(
        Button(
            text=Const("❌ Удалить контакт"),
            id="delete_contact",
            when=contact_exist,
            on_click=delete_contact
        ),
        *get_widgets(),
        MessageInput(
            func=contact_validator,
            content_types=types.ContentType.TEXT
        ),
        state=Form.contact,
        preview_add_transitions=[Back(), SwitchTo(Const(""), "hint", Form.description),
                                 SwitchTo(Const(""), "hint", Form.price), SwitchTo(Const(""), "hint", Form.tag)]
    ),
    on_start=set_default,
    getter=[get_stages, get_show_next, get_can_post, get_form_text]
)

confirm_dialog = Dialog(
    Window(
        Format(text="{final_text}", when="final_text"),
        DynamicMediaFileId(
            file_id=Format(text='{file_id}'),
            when="file_id"),
        Button(
            text=Const("✅ Да"),
            id="yes",
            on_click=on_confirm
        ),
        Row(
            Button(Const("<<"), id="left_photo", on_click=change_photo),
            Button(Format(text="{photo_text}", when="photo_text"), id="photo_pos"),
            Button(Const(">>"), id="right_photo", on_click=change_photo),
            when="show_scroll"
        ),
        Row(
            Start(
                text=Const("🔚 В главное меню"),
                id="to_main",
                state=Main.main,
                mode=StartMode.RESET_STACK
            ),
            Button(
                text=Const("⬅️ Назад"),
                id="back_to_edit",
                on_click=on_back
            )
        ),
        state=ConfirmAd.confirm,
        getter=get_confirm_text,
        preview_add_transitions=[Start(Const(""), "hint", Main.main), Start(Const(""), "hint", Form.description),
                                 Start(Const(""), "hint", Form.photo), Start(Const(""), "hint", Form.price),
                                 Start(Const(""), "hint", Form.contact)]
    )
)
