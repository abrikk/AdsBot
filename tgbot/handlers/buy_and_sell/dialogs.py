import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, \
    Start, Radio, Select, ScrollingGroup, Group
from aiogram_dialog.widgets.text import Const, Format

from tgbot.handlers.buy_and_sell.form import price_validator, get_currency_data, currency_selected, contact_validator, \
    delete_tag, invalid_input, change_page, fixed_size_1024, fixed_size_64, pic_validator, change_photo, \
    set_default, to_state, add_tag, tag_exist, on_back, process_result, get_widgets, contact_exist, pic_exist, \
    delete_contact, delete_pic
from tgbot.handlers.buy_and_sell.getters import get_final_text, on_confirm, get_form_text, get_tags_data
from tgbot.misc.media_widget import DynamicMediaFileId
from tgbot.misc.states import Main, Preview, ConfirmAd, Form

# getting dialog
from tgbot.misc.temp_checkbox import Checkbox

form_dialog = Dialog(
    Window(
        Radio(
            checked_text=Format("✔️ {item[0]}"),
            unchecked_text=Format("{item[0]}"),
            id="ad_types",
            item_id_getter=operator.itemgetter(1),
            items="ad_types",
            on_click=switch_to_tags
        ),
        Start(
            text=Format("{back_btn}", when="back_btn"),
            id="to_previous",
            state=Main.make_ad
        ),
        state=Form.type,
        getter=get_ad_types
    )
)


def get_dialog(where: str) -> Dialog:
    dialog = Dialog(
        Window(
            ScrollingGroup(
                Select(
                    Format("{item[0]}"),
                    id="s_tags",
                    item_id_getter=operator.itemgetter(0),
                    items="tags_data",
                    on_click=add_tag,
                ),
                id="sg_tags",
                width=2,
                height=4,
                when="show_scroll"
            ),
            Group(
                Select(
                    Format("{item[0]}"),
                    id="s_tags",
                    item_id_getter=operator.itemgetter(0),
                    items="tags_data",
                    on_click=add_tag,
                ),
                id="g_tags",
                width=2,
                when="show_tags"
            ),
            Button(
                text=Const("Удалить тег"),
                id="delete_tag",
                when=tag_exist,
                on_click=delete_tag
            ),
            *get_widgets(),
            state=to_state.get(where).tags,
            getter=[get_form_text, get_tags_data]
        ),
        Window(
            *get_widgets(),
            TextInput(
                id="title",
                type_factory=fixed_size_64,
                on_error=invalid_input,
                on_success=change_page),
            state=to_state.get(where).title,
            getter=[get_form_text]
        ),
        Window(
            *get_widgets(),
            TextInput(
                id="description",
                type_factory=fixed_size_1024,
                on_error=invalid_input,
                on_success=change_page
            ),
            state=to_state.get(where).description,
            getter=[get_form_text]
        ),

        Window(
            Button(
                text=Const("Удалить фото"),
                id="delete_pic",
                when=pic_exist,
                on_click=delete_pic
            ),
            *get_widgets(),
            MessageInput(
                pic_validator,
                content_types=[types.ContentType.ANY]
            ),
            state=to_state.get(where).photo,
            getter=[get_form_text]
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
            state=to_state.get(where).price,
            getter=[get_form_text, get_currency_data]
        ),
        Window(
            Button(
                text=Const("Удалить контакт"),
                id="delete_contact",
                when=contact_exist,
                on_click=delete_contact
            ),
            *get_widgets(),
            MessageInput(
                func=contact_validator,
                content_types=types.ContentType.TEXT
            ),
            state=to_state.get(where).contact,
            getter=[get_form_text]
        ),

        on_start=set_default,
        on_process_result=process_result
    )

    return dialog


preview_dialog = Dialog(
    Window(
        Format(text="{final_text}", when="final_text"),
        DynamicMediaFileId(
            file_id=Format(text='{file_id}'),
            when="file_id"),
        Row(
            Button(Const("<<"), id="left_photo", on_click=change_photo),
            Button(Format(text="{photo_text}", when="photo_text"), id="photo_pos"),
            Button(Const(">>"), id="right_photo", on_click=change_photo),
            when="show_scroll"
        ),
        Button(
            text=Const("Назад"),
            id="back_to_edit",
            on_click=on_back
        ),
        state=Preview.preview,
        getter=[get_final_text]
    )
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
            Button(
                text=Const("Назад"),
                id="back_to_edit",
                on_click=on_back
            ),
            Start(
                text=Const("В главное меню"),
                id="to_main",
                state=Main.main,
                mode=StartMode.RESET_STACK),
        ),
        state=ConfirmAd.confirm,
        getter=[get_final_text]
    )
)

# making dialog
sell_dialog: Dialog = get_dialog(where="sell")
buy_dialog: Dialog = get_dialog(where="buy")
