import copy

from aiogram import Bot, types
from aiogram.types import MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from schedulers.functions import create_jobs
from tgbot.config import Config
from tgbot.handlers.create_ad.form_2 import get_active_section, get_current_file_id
# from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.misc.ad import Ad
from tgbot.misc.states import Main
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage
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
    data.pop('currency', None)

    state: list[str] = dialog_manager.current_context().state.state.split(":")
    ad: Ad = Ad(
        state_class=state[0],
        state=state[1],
        **data
    )

    return {
        "form_text": ad.to_text(),
        "page": get_active_section(state[-1]),
        "show_checkbox": state[0] in ("Sell", "EditSell")
    }


async def get_final_text(dialog_manager: DialogManager, **_kwargs):
    start_data: dict = dialog_manager.current_context().start_data
    current_state: str = dialog_manager.current_context().state.state.split(":")[-1]
    state_class: str = start_data.get("state_class")
    if post_id := start_data.get("post_id"):
        session = dialog_manager.data.get("session")
        post_ad: PostAd = await session.get(PostAd, post_id)

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
        data.update(start_data)
        data.pop("post_id", None)
    else:
        data: dict = copy.deepcopy(start_data)

    data.pop("state_class", None)
    data.pop('current_page', None)
    data.pop('photos_len', None)
    data.pop('currency', None)

    ad: Ad = Ad(
        state_class=state_class,
        state=current_state,
        **data
    )
    print(ad.photos_ids)

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
    scheduler = call.bot.get("scheduler")
    obj = manager.event
    bot: Bot = obj.bot
    session = manager.data.get("session")
    db: DBCommands = manager.data.get("db_commands")
    start_data = manager.current_context().start_data

    state_class: str = start_data.get("state_class")
    config: Config = manager.data.get("config")

    data = copy.deepcopy(start_data)
    items_to_pop = ['state_class', 'current_page', 'photos_len', 'currency']
    for item in items_to_pop:
        data.pop(item, None)

    data.update({"mention": obj.from_user.get_mention()})

    ad: Ad = Ad(
        state_class=state_class,
        **data
    )

    if len(ad.photos_ids) > 1:
        print("more?")
        album = MediaGroup()

        for file_id in ad.photos_ids[:-1]:
            album.attach_photo(photo=file_id)

        album.attach_photo(
            photo=ad.photos_ids[-1],
            caption=ad.post()
        )
        print(album)

        sent_post = await bot.send_media_group(
            chat_id=config.tg_bot.channel_id,
            media=album
        )
        print("the end?")

    elif ad.photos_ids:
        sent_post = await bot.send_photo(
            chat_id=config.tg_bot.channel_id,
            photo=ad.photos_ids[0],
            caption=ad.post()
        )

    else:
        sent_post = await bot.send_message(
            chat_id=config.tg_bot.channel_id,
            text=ad.post()
        )

    if isinstance(sent_post, list):
        post_id = sent_post[-1].message_id
        print("post id ", post_id)
        message_ids = [
            RelatedMessage(
                post_id=post_id,
                message_id=message.message_id,
                photo_file_id=message.photo[-1].file_id,
                photo_file_unique_id=message.photo[-1].file_unique_id
            ) for message in sent_post
        ]

    elif sent_post.photo:
        post_id = sent_post.message_id
        message_ids = [RelatedMessage(
            post_id=post_id,
            message_id=sent_post.message_id,
            photo_file_id=sent_post.photo[-1].file_id,
            photo_file_unique_id=sent_post.photo[-1].file_unique_id
        )]

    else:
        post_id = sent_post.message_id
        message_ids = []

    post_ad: PostAd = PostAd(
        post_id=post_id,
        post_type=state_class.lower(),
        user_id=obj.from_user.id,
        tags=await db.get_tags_by_name(start_data.get("tags")),
        title=ad.title,
        description=ad.description,
        price=ad.price,
        contacts=",".join(ad.contacts),
        currency_code=ad.currency_code,
        negotiable=ad.negotiable,
        related_messages=message_ids
    )

    session.add(post_ad)
    await session.commit()

    create_jobs(scheduler, obj.from_user.id, post_ad.post_id, config.tg_bot.channel_id)

    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)


async def get_tags_data(dialog_manager: DialogManager, **_kwargs):
    user_tags: list[str] = dialog_manager.current_context().widget_data.get('tags', [])

    db: DBCommands = dialog_manager.data.get("db_commands")
    restriction: Restriction = await db.get_restriction("tag")

    tags: list[str] = await db.get_tags()

    for tag in user_tags:
        tags.remove(tag.removeprefix("#️⃣"))

    tag_dict: dict = {
        "tags_data": [("#️⃣" + tag,) for tag in tags],
        "show_scroll": len(user_tags) < restriction.number and len(tags) > 8,
        "show_tags": len(user_tags) < restriction.number and len(tags) <= 8,
    }

    return tag_dict
