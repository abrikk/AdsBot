from aiogram import types
from aiogram.types import MediaGroup
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Format, Const

from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.misc.states import ShowMyAd, MyAds, EditBuy, EditSell
from tgbot.models.post_ad import PostAd
from tgbot.services.db_commands import DBCommands


async def get_show_my_ad_text(dialog_manager: DialogManager, **_kwargs):
    obj = dialog_manager.event
    start_data = dialog_manager.current_context().start_data
    session = dialog_manager.data.get("session")
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
        "photos_ids": post_ad.photos_ids.split(","),
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

    return {"preview_text": ad.preview()}


async def start_editing_ad(_call: types.CallbackQuery, _button: Button, manager: DialogManager):
    start_data = manager.current_context().start_data
    post_id = int(start_data.get("post_id"))
    db: DBCommands = manager.data.get("db_commands")
    post_type: str = await db.get_post_type(post_id)
    to_state = EditSell if post_type == "sell" else EditBuy
    await manager.start(to_state.tags, data={"post_id": post_id}, mode=StartMode.RESET_STACK)


show_my_ad_dialog = Dialog(
    Window(
        Format(text="{preview_text}", when="preview_text"),
        Button(
            text=Const("Редактировать"),
            id="edit_ad",
            on_click=start_editing_ad
        ),
        Start(
            text=Const("Назад"),
            id="back_to_ma_ads",
            state=MyAds.show,
            mode=StartMode.RESET_STACK,
        ),
        state=ShowMyAd.true,
        getter=get_show_my_ad_text
    )
)
