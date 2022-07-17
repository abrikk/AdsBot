import logging

from aiogram import types
from aiogram.types import MediaGroup
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Start, Button, Row, Back, ManagedCheckboxAdapter, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from tgbot.config import Config
from tgbot.constants import INACTIVE, ACTIVE
from tgbot.handlers.buy_and_sell.form import make_link_to_post
from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.misc.states import ShowMyAd, MyAds, EditBuy, EditSell
from tgbot.misc.temp_checkbox import Checkbox
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage
from tgbot.services.db_commands import DBCommands


async def get_show_my_ad_text(dialog_manager: DialogManager, **_kwargs):
    obj = dialog_manager.event
    start_data = dialog_manager.current_context().start_data
    session = dialog_manager.data.get("session")
    config: Config = dialog_manager.data.get("config")
    db: DBCommands = dialog_manager.data.get("db_commands")
    post_id = int(start_data.get("post_id"))
    post_ad: PostAd = await session.get(PostAd, post_id)

    tag, contact, pic, post = await db.get_values_of_restrictions()
    limits: dict = {
        "tag_limit": tag,
        "contact_limit": contact,
        "pic_limit": pic,
        "post_limit": post
    }

    data: dict = {
        "tags": [tag.tag_name for tag in post_ad.tags],
        "description": post_ad.description,
        "contacts": post_ad.contacts.split(","),
        "price": post_ad.price,
        "currency_code": post_ad.currency_code,
        "negotiable": post_ad.negotiable,
        "title": post_ad.title,
        "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else [],
        "status": post_ad.status,
        "post_link": make_link_to_post(channel_id=config.tg_bot.channel_id, post_id=post_ad.post_id),
        "updated_at": post_ad.updated_at,
        "created_at": post_ad.created_at
    }
    data.update(limits)

    if post_ad.photos_ids:
        album = MediaGroup()
        for photo_id in post_ad.photos_ids.split(","):
            album.attach_photo(photo=photo_id)
        await obj.bot.send_media_group(chat_id=obj.from_user.id, media=album)

    if post_ad.post_type == "sell":
        ad = SalesAd(**data)
    else:
        ad = PurchaseAd(**data)

    dialog_manager.show_mode = ShowMode.SEND

    return {"preview_text": ad.preview(where="edit")}


async def get_post_link(dialog_manager: DialogManager, **_kwargs):
    config: Config = dialog_manager.data.get("config")
    start_data = dialog_manager.current_context().start_data
    post_id = int(start_data.get("post_id"))
    return {"post_link": make_link_to_post(channel_id=config.tg_bot.channel_id, post_id=post_id)}


async def start_editing_ad(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    start_data = manager.current_context().start_data
    post_id = int(start_data.get("post_id"))
    db: DBCommands = manager.data.get("db_commands")
    post_type: str = await db.get_post_type(post_id)
    to_state = EditSell if post_type == "sell" else EditBuy
    await manager.start(to_state.tags, data={"post_id": post_id}, mode=StartMode.RESET_STACK)


async def delete_post_ad(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    start_data = manager.current_context().start_data
    session = manager.data.get("session")
    config: Config = manager.data.get("config")
    post_id = int(start_data.get("post_id"))
    post_ad: PostAd = await session.get(PostAd, post_id)

    try:
        if post_ad.related_messages:
            for message in post_ad.related_messages:
                await call.bot.delete_message(
                    chat_id=config.tg_bot.channel_id,
                    message_id=message.message_id
                )

        await call.bot.delete_message(
            chat_id=config.tg_bot.channel_id,
            message_id=post_ad.post_id
        )
    except Exception as e:
        logging.info(e)
    await session.delete(post_ad)
    await session.commit()

    await call.answer(text="Объявление было успешно удалено!")

    await manager.start(MyAds.show, mode=StartMode.RESET_STACK)


async def change_post_status(call: types.CallbackQuery, widget: ManagedCheckboxAdapter, manager: DialogManager):
    activated: bool = widget.is_checked()
    start_data = manager.current_context().start_data
    session = manager.data.get("session")
    config: Config = manager.data.get("config")
    post_id = int(start_data.get("post_id"))
    post_ad: PostAd = await session.get(PostAd, post_id)

    if not activated:
        post_ad.status = INACTIVE
        if post_ad.related_messages:
            for message in post_ad.related_messages:
                await call.bot.delete_message(
                    chat_id=config.tg_bot.channel_id,
                    message_id=message.message_id
                )
        await call.bot.delete_message(
            chat_id=config.tg_bot.channel_id,
            message_id=post_ad.post_id
        )
        await session.commit()
    else:
        post_ad.status = ACTIVE
        data: dict = {
            "tags": [tag.tag_name for tag in post_ad.tags],
            "description": post_ad.description,
            "contacts": post_ad.contacts.split(","),
            "price": post_ad.price,
            "currency_code": post_ad.currency_code,
            "negotiable": post_ad.negotiable,
            "title": post_ad.title,
            "photos_ids": post_ad.photos_ids.split(",") if post_ad.photos_ids else [],
        }

        ad = SalesAd(**data) if post_ad.post_type == "sell" else PurchaseAd(**data)

        if ad.photos_ids:
            album = MediaGroup()
            for file_id in ad.photos_ids[:-1]:
                album.attach_photo(photo=file_id)

            album.attach_photo(photo=ad.photos_ids[-1], caption=ad.post())

            sent_post = await call.bot.send_media_group(chat_id=config.tg_bot.channel_id,
                                                        media=album)
        else:
            sent_post = await call.bot.send_message(chat_id=config.tg_bot.channel_id,
                                                    text=ad.post())

        if isinstance(sent_post, list):
            post_id = sent_post[-1].message_id
            message_ids = [
                RelatedMessage(
                    post_id=post_id,
                    message_id=p.message_id
                ) for p in sent_post[:-1]
            ]
        else:
            post_id = sent_post.message_id
            message_ids = []
        post_ad.post_id = post_id
        post_ad.related_messages = message_ids
        await session.commit()
        await call.answer(text="Объявление было успешно активировано!")

show_my_ad_dialog = Dialog(
    Window(
        Format(text="{preview_text}", when="preview_text"),
        Button(
            text=Const("Редактировать"),
            id="edit_ad",
            on_click=start_editing_ad
        ),
        Checkbox(
            checked_text=Const("Деактивировать"),
            unchecked_text=Const("Активировать"),
            id="post_status",
            on_state_changed=change_post_status,
            default=True
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
        Format("{post_link}\n"
               "Вы уверены, что хотите удалить объявление?"),
        Row(
            Back(
                Const("Нет ❌")
            ),
            Button(
                Const("Да ✅"),
                id="yes_delete",
                on_click=delete_post_ad
            )
        ),
        state=ShowMyAd.confirm_delete,
        getter=get_post_link
    )
)
