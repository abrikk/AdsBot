# import operator
#
# from aiogram import types
# from aiogram_dialog import Window, Dialog
# from aiogram_dialog.widgets.input import MessageInput, TextInput
# from aiogram_dialog.widgets.kbd import Select, ScrollingGroup, Group, Button, Radio
# from aiogram_dialog.widgets.text import Format, Const
#
# from tgbot.handlers.create_ad.form_2 import price_validator, change_page, currency_selected, \
#     get_currency_data, contact_validator, add_tag, tag_exist, delete_tag, fixed_size_1024, \
#     invalid_input, fixed_size_64, pic_validator, set_edit_default, get_widgets, pic_exist, delete_pic, contact_exist, \
#     delete_contact
# from tgbot.handlers.create_ad.getters import get_tags_data
# from tgbot.handlers.edit_ad.edit_ad import get_edit_text
# from tgbot.misc.states import EditBuy, EditSell
# from tgbot.misc.temp_checkbox import Checkbox
#
# to_state: dict = {
#     "sell": EditSell,
#     "buy": EditBuy,
# }
#
#
# def get_edit_dialog(where: str) -> Dialog:
#     dialog = Dialog(
#         Window(
#             ScrollingGroup(
#                 Select(
#                     Format("{item[0]}"),
#                     id="s_tags",
#                     item_id_getter=operator.itemgetter(0),
#                     items="tags_data",
#                     on_click=add_tag,
#                 ),
#                 id="sg_tags",
#                 width=2,
#                 height=4,
#                 when="show_scroll"
#             ),
#             Group(
#                 Select(
#                     Format("{item[0]}"),
#                     id="s_tags",
#                     item_id_getter=operator.itemgetter(0),
#                     items="tags_data",
#                     on_click=add_tag,
#                 ),
#                 id="g_tags",
#                 width=2,
#                 when="show_tags"
#             ),
#             Button(
#                 text=Const("Удалить тег"),
#                 id="delete_tag",
#                 when=tag_exist,
#                 on_click=delete_tag
#             ),
#             *get_widgets(where='edit'),
#             state=to_state.get(where).tags,
#             getter=[get_edit_text, get_tags_data]
#         ),
#         Window(
#             *get_widgets(where='edit'),
#             TextInput(
#                 id="title",
#                 type_factory=fixed_size_64,
#                 on_error=invalid_input,
#                 on_success=change_page),
#             state=to_state.get(where).title,
#             getter=[get_edit_text]
#         ),
#         Window(
#             *get_widgets(where='edit'),
#             TextInput(
#                 id="description",
#                 type_factory=fixed_size_1024,
#                 on_error=invalid_input,
#                 on_success=change_page
#             ),
#             state=to_state.get(where).description,
#             getter=[get_edit_text]
#         ),
#         Window(
#             Button(
#                 text=Const("Удалить фото"),
#                 id="delete_pic",
#                 when=pic_exist,
#                 on_click=delete_pic
#             ),
#             *get_widgets(where='edit'),
#             MessageInput(
#                 pic_validator,
#                 content_types=[types.ContentType.ANY]
#             ),
#             state=to_state.get(where).photo,
#             getter=[get_edit_text]
#         ),
#         Window(
#             Checkbox(
#                 checked_text=Const("Торг уместен: Да ✅"),
#                 unchecked_text=Const("Торг уместен: Нет ❌"),
#                 id="negotiable",
#                 default=False,
#                 when="show_checkbox"
#             ),
#             Radio(
#                 checked_text=Format("✔️ {item[0]}"),
#                 unchecked_text=Format("{item[0]}"),
#                 id="currency_code",
#                 item_id_getter=operator.itemgetter(1),
#                 items="currencies",
#                 on_click=currency_selected
#             ),
#             *get_widgets(where='edit'),
#             MessageInput(
#                 func=price_validator,
#                 content_types=types.ContentType.TEXT
#             ),
#             state=to_state.get(where).price,
#             getter=[get_edit_text, get_currency_data]
#         ),
#         Window(
#             Button(
#                 text=Const("Удалить контакт"),
#                 id="delete_contact",
#                 when=contact_exist,
#                 on_click=delete_contact
#             ),
#             *get_widgets(where='edit'),
#             MessageInput(
#                 func=contact_validator,
#                 content_types=types.ContentType.TEXT
#             ),
#             state=to_state.get(where).contact,
#             getter=[get_edit_text]
#         ),
#
#         on_start=set_edit_default
#     )
#
#     return dialog
#
#
# edit_sell_ad_dialog = get_edit_dialog(where='sell')
# edit_buy_ad_dialog = get_edit_dialog(where='buy')
