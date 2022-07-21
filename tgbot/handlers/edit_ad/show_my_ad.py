import operator

from aiogram import types
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start, Button, Row, Back, SwitchTo, Select, Next, Column, Radio, Group
from aiogram_dialog.widgets.text import Format, Const

# from tgbot.handlers.create_ad.form_2 import make_link_to_post
from tgbot.handlers.create_ad.form import currency_selected, get_currency_data
from tgbot.handlers.edit_ad.edit import edit_input, delete_item, delete_post_ad, save_edit_option, clear_data, \
    save_edit, set_edit_default
from tgbot.handlers.edit_ad.getters import get_edit_options, get_edit_text, get_show_my_ad_text, get_post_link, \
    get_can_save_edit
from tgbot.misc.states import ShowMyAd, MyAds

# async def start_editing_ad(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
#     start_data = manager.current_context().start_data
#     post_id = int(start_data.get("post_id"))
#     db: DBCommands = manager.data.get("db_commands")
#     post_type: str = await db.get_post_type(post_id)
#     to_state = EditSell if post_type == "sell" else EditBuy
#     await manager.start(to_state.tags, data={"post_id": post_id}, mode=StartMode.RESET_STACK)
#


#
#
# async def change_post_status(call: types.CallbackQuery, widget: ManagedCheckboxAdapter, manager: DialogManager):
#     activated: bool = widget.is_checked()
#     start_data = manager.current_context().start_data
#     session = manager.data.get("session")
#     config: Config = manager.data.get("config")
#     post_id = int(start_data.get("post_id"))
#     post_ad: PostAd = await session.get(PostAd, post_id)
#
#     if not activated:
#         post_ad.status = INACTIVE
#         if post_ad.related_messages:
#             for message in post_ad.related_messages:
#                 await call.bot.delete_message(
#                     chat_id=config.tg_bot.channel_id,
#                     message_id=message.message_id
#                 )
#         await call.bot.delete_message(
#             chat_id=config.tg_bot.channel_id,
#             message_id=post_ad.post_id
#         )
#         await session.commit()
#     else:
#         post_ad.status = ACTIVE
#         data: dict = {
#             "tags": [tag.tag_name for tag in post_ad.tags],
#             "description": post_ad.description,
#             "contacts": post_ad.contacts.split(","),
#             "price": post_ad.price,
#             "currency_code": post_ad.currency_code,
#             "negotiable": post_ad.negotiable,
#             "title": post_ad.title,
#             "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else [],
#         }
#
#         ad: Ad = Ad(
#             state_class=post_ad.post_type.capitalize(),
#             **data
#         )
#
#         if ad.photos_ids:
#             album = MediaGroup()
#             for file_id in ad.photos_ids[:-1]:
#                 album.attach_photo(photo=file_id)
#
#             album.attach_photo(photo=ad.photos_ids[-1], caption=ad.post())
#
#             sent_post = await call.bot.send_media_group(chat_id=config.tg_bot.channel_id,
#                                                         media=album)
#         else:
#             sent_post = await call.bot.send_message(chat_id=config.tg_bot.channel_id,
#                                                     text=ad.post())
#
#         if isinstance(sent_post, list):
#             post_id = sent_post[-1].message_id
#             message_ids = [
#                 RelatedMessage(
#                     post_id=post_id,
#                     message_id=p.message_id
#                 ) for p in sent_post[:-1]
#             ]
#         else:
#             post_id = sent_post.message_id
#             message_ids = []
#         post_ad.post_id = post_id
#         post_ad.related_messages = message_ids
#         await session.commit()
#         await call.answer(text="Объявление было успешно активировано!")
from tgbot.misc.temp_checkbox import Checkbox

show_my_ad_dialog = Dialog(
    Window(
        Format(text="{preview_text}", when="preview_text"),
        Button(
            text=Const("Редактировать"),
            id="edit_ad",
            on_click=Next()
        ),
        SwitchTo(
            text=Const("Удалить"),
            id="delete_post",
            state=ShowMyAd.confirm_delete
        ),
        Start(
            text=Const("Назад"),
            id="back_to_ma_ads",
            state=MyAds.show,
            mode=StartMode.RESET_STACK,
        ),
        state=ShowMyAd.true,
        getter=get_show_my_ad_text
    ),

    Window(
        Const("Выберите раздел который хотите отредактировать:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="edit",
                item_id_getter=operator.itemgetter(0),
                items="edit_options",
                on_click=save_edit_option,
            )
        ),
        Back(text=Const("Назад")),
        state=ShowMyAd.show_edit,
        getter=get_edit_options
    ),
    Window(
        Format(text="{edit_text}", when="edit_text"),
        Button(
            text=Const("Удалить контакт"),
            id="delete_contact",
            on_click=delete_item,
            when="delete_contact"
        ),
        Button(
            text=Const("Удалить фото"),
            id="delete_photo",
            on_click=delete_item,
            when="delete_photo"
        ),
        Group(
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
            when="show_currency"
        ),
        Row(
            Back(
                text=Const("Отмена"),
                on_click=clear_data
            ),
            Button(
                text=Const("Сохранить"),
                id="save_edit",
                on_click=save_edit,
                when="can_save_edit"
            )
        ),
        MessageInput(
            func=edit_input,
            content_types=[types.ContentType.TEXT, types.ContentType.PHOTO]
        ),
        state=ShowMyAd.edit,
        getter=[get_can_save_edit, get_currency_data, get_edit_text]
    ),
    Window(
        Format("{post_link}\n"
               "Вы уверены, что хотите удалить объявление?"),
        Row(
            Back(Const("Нет ❌")),
            Button(
                Const("Да ✅"),
                id="yes_delete",
                on_click=delete_post_ad
            )
        ),
        state=ShowMyAd.confirm_delete,
        getter=get_post_link
    ),
    on_start=set_edit_default
)
