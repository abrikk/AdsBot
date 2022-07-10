import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo, \
    Start, Checkbox, Radio
from aiogram_dialog.widgets.text import Const, Format

from tgbot.handlers.buy_and_sell.form import price_validator, get_currency_data, currency_selected, contact_validator, \
    delete_tag, tag_exist, invalid_input, change_page, fixed_size_1024, fixed_size_64, pic_validator, change_photo, \
    clear_photo_pagination_data, set_default, tag_buttons, check_required_fields, to_state
from tgbot.handlers.buy_and_sell.getters import get_final_text, on_confirm, get_form_text
from tgbot.misc.media_widget import DynamicMediaFileId
from tgbot.misc.states import Main


# getting dialog
def get_dialog(where: str) -> Dialog:
    def get_widgets():
        buttons = (
            Format(text="{" + f"{where}" + "_text}", when=f"{where}" + "_text"),
            Row(
                Button(text=Const("<<"), id="left", on_click=change_page),
                Button(text=Format(text="{page}"), id="page"),
                Button(text=Const(">>"), id="right", on_click=change_page)
            ),
            Row(
                Start(text=Const("🔚 Назад"), id="back_to_main", state=Main.main,
                      mode=StartMode.RESET_STACK),
                SwitchTo(text=Const("👁"), id="preview", state=to_state.get(where).preview),
                Button(text=Const("Опубликовать"), id="post", on_click=check_required_fields)
            )
        )
        return buttons

    if where == "sell":
        price_window = Window(
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
            state=to_state.get(where).price,
            getter=[get_form_text, get_currency_data]
        )
    else:
        price_window = Window(
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
        )
    order_windows: list = [
        price_window,
        Window(
            *get_widgets(),
            MessageInput(
                func=contact_validator,
                content_types=types.ContentType.TEXT
            ),
            state=to_state.get(where).contact,
            getter=[get_form_text]
        ),
    ]

    if where == "buy":
        order_windows = order_windows[::-1]

    dialog = Dialog(
        Window(
            tag_buttons(),
            Button(
                text=Const("Удалить тег"),
                id="delete_tag",
                when=tag_exist,
                on_click=delete_tag
            ),
            *get_widgets(),
            state=to_state.get(where).tags,
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
        *order_windows,
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
            MessageInput(
                pic_validator,
                content_types=[types.ContentType.ANY]
            ),
            state=to_state.get(where).photo,
            getter=[get_form_text]
        ),
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
            SwitchTo(
                text=Const("Назад"),
                id="back_to_edit",
                state=to_state.get(where).tags,
                on_click=clear_photo_pagination_data),
            state=to_state.get(where).preview,
            getter=[get_final_text]
        ),
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
                SwitchTo(
                    text=Const("Назад"),
                    id="back_to_edit",
                    state=to_state.get(where).tags,
                    on_click=clear_photo_pagination_data),
                Start(text=Const("В главное меню"), id="to_main", state=Main.main, mode=StartMode.RESET_STACK),
            ),
            state=to_state.get(where).confirm,
            getter=[get_final_text]
        ),
        on_start=set_default
    )

    return dialog


# making dialog
sell_dialog: Dialog = get_dialog(where="sell")
buy_dialog: Dialog = get_dialog(where="buy")
