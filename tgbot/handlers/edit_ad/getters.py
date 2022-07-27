from aiogram.types import MediaGroup
from aiogram.utils.markdown import hitalic, hcode
from aiogram_dialog import DialogManager, ShowMode

from tgbot.config import Config
from tgbot.handlers.create_ad.form import make_link_to_post
from tgbot.misc.ad import Ad
from tgbot.models.post_ad import PostAd


async def get_show_my_ad_text(dialog_manager: DialogManager, **_kwargs):
    obj = dialog_manager.event
    start_data = dialog_manager.current_context().start_data
    session = dialog_manager.data.get("session")
    config: Config = dialog_manager.data.get("config")
    post_id = start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)
    channel = await obj.bot.get_chat(config.chats.main_channel_id)

    ad: Ad = Ad(
        state_class=post_ad.post_type,
        tag_category=post_ad.tag_category,
        tag_name=post_ad.tag_name,
        description=post_ad.description,
        contacts=post_ad.contacts.split(","),
        price=post_ad.price,
        currency_code=post_ad.currency_code,
        negotiable=post_ad.negotiable,
        photos={m.photo_file_unique_id: m.photo_file_id for m in post_ad.related_messages} if post_ad.related_messages else {},
        post_link=make_link_to_post(channel_username=channel.username, post_id=post_ad.post_id),
        updated_at=post_ad.updated_at,
        created_at=post_ad.created_at
    )

    return {"preview_text": ad.preview(where="edit"), "url": ad.post_link}


async def get_edit_options(dialog_manager: DialogManager, **_kwargs):
    edit_options: list = [
        ("description", "Описание"),
        ("contacts", "Контакты"),
    ]
    session = dialog_manager.data.get("session")
    post_id = dialog_manager.current_context().start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)

    if post_ad.post_type != "exchange" and post_ad.price is not None:
        edit_options.insert(1, ("price", "Цена"))

    if post_ad.related_messages:
        edit_options.append(("photos", "Фото"))

    return {"edit_options": edit_options}


async def get_post_link(dialog_manager: DialogManager, **_kwargs):
    config: Config = dialog_manager.data.get("config")
    start_data = dialog_manager.current_context().start_data
    post_id = int(start_data.get("post_id"))
    channel = await dialog_manager.event.bot.get_chat(config.chats.main_channel_id)
    return {"post_link": make_link_to_post(channel_username=channel.username, post_id=post_id)}


async def get_edit_text(dialog_manager: DialogManager, **_kwargs):
    widget_data = dialog_manager.current_context().widget_data
    edit: str = widget_data.get("edit")
    text: dict = {
        "description": "Введите новое описание:\n\n",
        "price": "Введите новую цену:\n\n",
        "contacts": "Введите новые контактные данные:\n\n",
        "photos": "Отправьте новое фото:\n\n"
    }

    session = dialog_manager.data.get("session")
    post_id = dialog_manager.current_context().start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)

    if edit == "photos" and widget_data.setdefault("not_edited", True):
        widget_data["photos"] = {m.photo_file_unique_id: m.photo_file_id for m in post_ad.related_messages}
        widget_data["photos_post_id"] = [m.message_id for m in post_ad.related_messages]
        widget_data["not_edited"] = False
    elif edit == "contacts" and widget_data.setdefault("not_edited", True):
        widget_data["contacts"] = post_ad.contacts.split(",")
        widget_data["not_edited"] = False

    current_data: dict = {
        "description": widget_data.get("description") or post_ad.description,
        "price": widget_data.get("price") or post_ad.price,
        "contacts": widget_data.get("contacts") or [],
        "photos": widget_data.get("photos") or {}
    }

    widget_data[edit] = current_data[edit]

    if edit == "photos" and len(widget_data.get("photos")) > 0:
        obj = dialog_manager.event
        dialog_manager.show_mode = ShowMode.SEND
        album = MediaGroup()
        for photo_id in [m for m in widget_data.get("photos").values()]:
            album.attach_photo(photo=photo_id)
        await obj.bot.send_media_group(chat_id=obj.from_user.id, media=album)

    if edit == "photos":
        current_data_text = "Текущее количество картинок: " + str(len(current_data.get(edit))) + "шт"
    elif edit == "contacts":
        current_contact = current_data.get(edit) and ", ".join(map(hcode, current_data.get(edit))) or "➖"
        current_data_text = "Текущие контактные данные: " + current_contact
    elif edit == "price":
        currencies: dict = {'USD': '$', 'EUR': '€', 'RUB': '₽', 'UAH': '₴'}
        current_data_text = "Текущая цена: " + str(f'{current_data.get(edit):,}') + " " + currencies.get(post_ad.currency_code)
    else:
        current_data_text = "Текущее описание: " + hitalic(current_data.get(edit))

    return {
        "edit_text": text.get(edit) + current_data_text,
        "delete_contact": edit == "contacts" and len(widget_data.get("contacts")) > 0,
        "delete_photo": edit == "photos" and bool(widget_data.get("photos", {})),
        "show_currency": edit == "price",
        "show_checkbox": edit == "price" and post_ad.post_type in ("sell", "rent")
    }


async def get_can_save_edit(dialog_manager: DialogManager, **_kwargs) -> dict:

    widget_data = dialog_manager.current_context().widget_data
    edit: str = widget_data.get("edit")
    session = dialog_manager.data.get("session")
    post_id = dialog_manager.current_context().start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)
    edit_options: dict = {
        "description": post_ad.description,
        "price": post_ad.price,
        "contacts": post_ad.contacts.split(","),
        "photos": {m.photo_file_unique_id: m.photo_file_id for m in post_ad.related_messages},
        "negotiable": widget_data.get("negotiable"),
        "currency_code": widget_data.get("currency_code")
    }

    updated_field = widget_data.get(edit) or edit_options.get(edit)

    if edit == "contacts":
        if updated_field and len(updated_field) > 0 and set(post_ad.contacts.split(",")) == set(updated_field):
            return {"can_save_edit": False}
        else:
            return {"can_save_edit": widget_data.get("not_edited") is not None and not widget_data.get("not_edited")}
    elif edit == "price":
        if updated_field != post_ad.price or edit_options["negotiable"] != post_ad.negotiable or edit_options["currency_code"] != post_ad.currency_code:
            return {"can_save_edit": True}
        else:
            return {"can_save_edit": False}

    return {"can_save_edit": edit_options[edit] != updated_field}
