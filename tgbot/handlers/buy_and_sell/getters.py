import copy

from aiogram import Bot, types
from aiogram.types import MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from tgbot.config import Config
from tgbot.handlers.buy_and_sell.form import get_active_section, get_current_file_id
from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.misc.states import Main
from tgbot.models.post_ad import PostAd
from tgbot.models.restriction import Restriction
from tgbot.services.db_commands import DBCommands


async def get_form_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    db: DBCommands = dialog_manager.data.get("db_commands")
    tag, contact, pic, post = await db.get_values_of_restrictions()
    limits: dict = {
        "tag_limit": tag,
        "contact_limit": contact,
        "pic_limit": pic,
        "post_limit": post
    }

    widget_data.update(limits)

    data = copy.deepcopy(widget_data)
    data.pop('sg_tags', None)

    state: list[str] = dialog_manager.current_context().state.state.split(":")
    if state[0] == "Sell":
        ad = SalesAd(state=state[-1], **data)
    else:
        ad = PurchaseAd(state=state[-1], **data)

    return {"form_text": ad.to_text(), "page": get_active_section(state[-1])}


async def get_final_text(dialog_manager: DialogManager, **_kwargs):
    start_data: dict = dialog_manager.current_context().start_data
    current_state: str = dialog_manager.current_context().state.state.split(":")[-1]
    state_class: str = start_data.get("state_class")

    data: dict = copy.deepcopy(start_data)
    data.pop("state_class", None)
    data.pop('current_page', None)
    data.pop('photos_len', None)

    ad = SalesAd(**data) if state_class == "Sell" else PurchaseAd(**data)
    if ad.photos_ids:
        current_page = start_data.setdefault('current_page', 1)
    else:
        current_page = None

    if len(ad.photos_ids) > 1:
        start_data['photos_len'] = len(ad.photos_ids)

    return {
        "final_text": ad.preview() if current_state == "preview" else ad.confirm(),
        "file_id": get_current_file_id(ad.photos_ids, current_page),
        "show_scroll": len(ad.photos_ids) > 1,
        "photo_text": len(ad.photos_ids) > 1 and current_page and f"{current_page}/{len(ad.photos_ids)}"
    }


async def on_confirm(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    obj = manager.event
    bot: Bot = obj.bot
    session = manager.data.get("session")
    db: DBCommands = manager.data.get("db_commands")
    start_data = manager.current_context().start_data

    state_class: str = start_data.get("state_class")
    config: Config = manager.data.get("config")

    data = copy.deepcopy(start_data)
    data.pop("state_class", None)
    data.pop('current_page', None)
    data.pop('photos_len', None)
    data.update({"mention": obj.from_user.get_mention()})

    ad = SalesAd(**data) if state_class == "Sell" else PurchaseAd(**data)

    album = MediaGroup()

    if ad.photos_ids:
        for file_id in ad.photos_ids[:-1]:
            album.attach_photo(photo=file_id)

        album.attach_photo(photo=ad.photos_ids[-1], caption=ad.post())

        post = await bot.send_media_group(chat_id=config.tg_bot.channel_id,
                                          media=album)
    else:
        post = await bot.send_message(chat_id=config.tg_bot.channel_id,
                                      text=ad.post())

    post_ad: PostAd = PostAd(
        post_id=post[0].message_id,
        post_type=state_class.lower(),
        user_id=obj.from_user.id,
        description=ad.description,
        contacts=",".join(ad.contacts),
        price=ad.price,
        tags=await db.get_tags_by_name(start_data.get("tags")),
        currency_code=ad.currency_code,
        negotiable=ad.negotiable,
        title=ad.title,
        photos_ids=",".join(ad.photos_ids),
    )
    print("post_ad", post_ad)

    session.add(post_ad)
    await session.commit()

    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)


async def get_tags_data(dialog_manager: DialogManager, **_kwargs):
    print(dialog_manager.current_context().start_data)

    state = dialog_manager.current_context().state.state.split(":")[0]
    user_tags: list[str] = dialog_manager.current_context().widget_data.get('tags', [])

    db: DBCommands = dialog_manager.data.get("db_commands")
    restriction: Restriction = await db.get_restriction("tag")
    # if start_data := dialog_manager.current_context().start_data:
    #     session = dialog_manager.data.get("session")
    #     post_id = int(start_data.get("post_id"))
    #     post_ad: PostAd = await session.get(PostAd, post_id)
    #     user_tags.extend([tag.name for tag in post_ad.tags])
    tags: list[str] = await db.get_tags()

    if state == "Sell":
        tags.remove("куплю")
    elif state == "Buy":
        tags.remove("продам")

    for tag in user_tags:
        tags.remove(tag.removeprefix("#️⃣"))

    tag_dict: dict = {
        "tags_data": [("#️⃣" + tag,) for tag in tags],
        "show_scroll": len(user_tags) < restriction.number and len(tags) > 8,
        "show_tags": len(user_tags) < restriction.number and len(tags) <= 8,
    }

    return tag_dict
