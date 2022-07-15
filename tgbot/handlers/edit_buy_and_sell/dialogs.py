import operator

from aiogram import types
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup, Group, Button, Radio, Checkbox
from aiogram_dialog.widgets.text import Format, Const

from tgbot.handlers.buy_and_sell.form import price_validator, change_page, currency_selected, \
    get_currency_data, contact_validator, add_tag, tag_exist, delete_tag, fixed_size_1024, \
    invalid_input, fixed_size_64, pic_validator, set_edit_default, get_widgets
from tgbot.handlers.buy_and_sell.getters import get_tags_data
from tgbot.handlers.edit_buy_and_sell.edit_ad import get_edit_text
from tgbot.misc.states import Edit


def get_edit_dialog() -> Dialog:
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
    #                 text=Const("Сохранить"),
    #                 id="save",
    #                 on_click=check_required_fields
    #             )
    #         )
    #     )
    #     return buttons

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
            *get_widgets(where='edit'),
            state=Edit.tags,
            getter=[get_edit_text, get_tags_data]
        ),
        Window(
            *get_widgets(where='edit'),
            TextInput(
                id="description",
                type_factory=fixed_size_1024,
                on_error=invalid_input,
                on_success=change_page
            ),
            state=Edit.description,
            getter=[get_edit_text]
        ),
        Window(
            *get_widgets(where='edit'),
            MessageInput(
                func=contact_validator,
                content_types=types.ContentType.TEXT
            ),
            state=Edit.contact,
            getter=[get_edit_text]
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
            *get_widgets(where='edit'),
            MessageInput(
                func=price_validator,
                content_types=types.ContentType.TEXT
            ),
            state=Edit.price,
            getter=[get_edit_text, get_currency_data]
        ),
        Window(
            *get_widgets(where='edit'),
            TextInput(
                id="title",
                type_factory=fixed_size_64,
                on_error=invalid_input,
                on_success=change_page),
            state=Edit.title,
            getter=[get_edit_text]
        ),
        Window(
            *get_widgets(where='edit'),
            MessageInput(
                pic_validator,
                content_types=[types.ContentType.ANY]
            ),
            state=Edit.photo,
            getter=[get_edit_text]
        ),

        on_start=set_edit_default
    )

    return dialog


edit_ad_dialog = get_edit_dialog()
