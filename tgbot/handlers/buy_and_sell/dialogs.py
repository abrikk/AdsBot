import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, \
    Start, Checkbox, Radio, Select, ScrollingGroup, Group
from aiogram_dialog.widgets.text import Const, Format

from tgbot.handlers.buy_and_sell.form import price_validator, get_currency_data, currency_selected, contact_validator, \
    delete_tag, invalid_input, change_page, fixed_size_1024, fixed_size_64, pic_validator, change_photo, \
    set_default, check_required_fields, to_state, add_tag, tag_exist, show_preview, on_back, process_result, get_widgets
from tgbot.handlers.buy_and_sell.getters import get_final_text, on_confirm, get_form_text, get_tags_data
from tgbot.misc.media_widget import DynamicMediaFileId
from tgbot.misc.states import Main, Preview, ConfirmAd


# getting dialog
def get_dialog(where: str) -> Dialog:
    # def get_widgets():
    #     buttons = (
    #         Format(text="{form_text}", when="form_text"),
    #         Row(
    #             Button(text=Const("<<"), id="left", on_click=change_page),
    #             Button(text=Format(text="{page}"), id="page"),
    #             Button(text=Const(">>"), id="right", on_click=change_page)
    #         ),
    #         Row(
    #             Start(
    #                 text=Const("🔚 Назад"),
    #                 id="back_to_main",
    #                 state=Main.main,
    #                 mode=StartMode.RESET_STACK
    #             ),
    #             Button(
    #                 text=Const("👁"),
    #                 id="preview",
    #                 on_click=show_preview
    #             ),
    #             Button(
    #                 text=Const("Опубликовать"),
    #                 id="post",
    #                 on_click=check_required_fields
    #             )
    #         )
    #     )
    #     return buttons

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
