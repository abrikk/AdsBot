import logging

from aiogram import types
from aiogram.types import InputMedia
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select, Back
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter

from tgbot.config import Config
from tgbot.handlers.create_ad.form import RepeatedNumberError, make_link_to_post
from tgbot.misc.ad import Ad
from tgbot.misc.states import MyAds, ShowMyAd

from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage
from tgbot.models.restriction import Restriction


async def edit_input(message: types.Message, _dialog: ManagedDialogAdapterProto, manager: DialogManager):
    widget_data = manager.current_context().widget_data
    edit: str = manager.current_context().widget_data.get("edit")
    text = message.text
    start_data = manager.current_context().start_data
    session = manager.data.get("session")
    post_id = start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)

    if edit == "description":
        if len(text) > 1024:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Максимальная длина описания товара или услуг 1024 символов."
                                 " Попробуйте еще раз.")
        else:
            widget_data["description"] = text

    elif edit == "photos":
        pic_limit = len(post_ad.related_messages)
        match message.content_type:
            case types.ContentType.PHOTO:

                photo = message.photo[-1]
                photos: dict = widget_data.setdefault("photos", {})

                if photo.file_unique_id in photos.keys():
                    manager.show_mode = ShowMode.EDIT
                    await message.answer("Эта картинка уже имеется в объявление. Отправьте другое.")
                    return
                if len(photos) < pic_limit:
                    photos[photo.file_unique_id] = photo.file_id
                else:
                    photos.pop(list(photos.keys())[-1], None)
                    photos[photo.file_unique_id] = photo.file_id

            case _:
                manager.show_mode = ShowMode.EDIT
                await message.answer("Вы ввели не валидную картинку! Попробуйте еще раз.")

    elif edit == "price":
        try:
            price: float = (float(message.text).is_integer() and int(message.text)) or round(float(message.text), 2)

            if not (price > 0.01):
                raise ValueError

            widget_data["price"] = price
        except ValueError:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Цена должна быть числом и быть больше 0.01. Попробуйте еще раз.")

    elif edit == "contacts":
        contact_limit: Restriction = await session.get(Restriction, "contact")
        try:
            phone_number = message.text.replace(' ', '')

            if phone_number.startswith('+'):
                phone_number = phone_number.removeprefix('+')
            if not phone_number.isdigit():
                raise ValueError

            phone_number = '+' + phone_number
            contact_data = widget_data.setdefault('contacts', post_ad.contacts.split(","))

            if phone_number in contact_data:
                raise RepeatedNumberError
            if len(contact_data) < contact_limit.number:
                contact_data.append(phone_number)
            else:
                contact_data[-1] = phone_number
        except ValueError:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Вы ввели неверный формат номера телефона. Попробуйте еще раз.")
        except RepeatedNumberError:
            manager.show_mode = ShowMode.EDIT
            await message.answer("Этот номер уже имеется в объявлении.")


async def delete_item(_call: types.CallbackQuery, button: Button, manager: DialogManager):
    item_to_delete = button.widget_id
    widget_data = manager.current_context().widget_data

    if item_to_delete == "delete_contact":
        contacts: list = widget_data.get("contacts")
        contacts.pop()
    elif item_to_delete == "delete_photo":
        photos: dict = widget_data.get("photos")
        photos_post_id: list = widget_data.get("photos_post_id")
        photos.pop(list(photos.keys())[0], None)
        photos_post_id.pop(0)


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


async def save_edit_option(_call: types.CallbackQuery, _widget: ManagedWidgetAdapter[Select], manager: DialogManager,
                           option: str):
    manager.current_context().widget_data["edit"] = option
    await manager.dialog().next()


async def clear_data(_call: types.CallbackQuery, _button: Button | Back, manager: DialogManager):
    manager.current_context().widget_data.clear()


async def save_edit(call: types.CallbackQuery, _button: Button, manager: DialogManager):
    widget_data: dict = manager.current_context().widget_data
    obj = manager.event
    edit: str = widget_data.get("edit")
    session = manager.data.get("session")
    config: Config = manager.data.get("config")
    post_id = manager.current_context().start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)
    current_photos = post_ad.related_messages

    updated_field = widget_data.get(edit)
    photos_post_id: list = widget_data.get("photos_post_id")

    if edit == "description":
        post_ad.description = updated_field
    elif edit == "photos":
        message_ids: list = list()
        for photo, photo_id in zip(updated_field.items(), photos_post_id):
            message_ids.append(
                RelatedMessage(
                    post_id=post_id,
                    message_id=photo_id,
                    photo_file_id=photo[-1],
                    photo_file_unique_id=photo[0]
                )
            )

        post_ad.related_messages = message_ids

    elif edit == "price":
        if widget_data.get("negotiable") != post_ad.negotiable:
            post_ad.negotiable = widget_data.get("negotiable")
        if widget_data.get("currency_code") != post_ad.currency_code:
            post_ad.currency_code = widget_data.get("currency_code")
        post_ad.price = updated_field
    elif edit == "contacts":
        post_ad.contacts = ",".join(updated_field)

    data: dict = {
        "tag_category": post_ad.tag_category,
        "tag_name": post_ad.tag_name,
        "description": post_ad.description,
        "contacts": post_ad.contacts.split(","),
        "price": post_ad.price,
        "currency_code": post_ad.currency_code,
        "negotiable": post_ad.negotiable,
        "photos": [m.photo_file_id for m in post_ad.related_messages] if post_ad.related_messages else [],
        "post_link": make_link_to_post(channel_id=config.tg_bot.channel_id, post_id=post_ad.post_id),
        "mention": obj.from_user.get_mention(),
        "updated_at": post_ad.updated_at,
        "created_at": post_ad.created_at
    }

    if len(current_photos) != len(post_ad.related_messages):
        start_from = len(current_photos) - len(post_ad.related_messages)
        for m in current_photos[:start_from]:
            await call.bot.delete_message(
                chat_id=config.tg_bot.channel_id,
                message_id=m.message_id
            )
    ad: Ad = Ad(
        state_class=post_ad.post_type,
        **data
    )

    if edit == "photos" and post_ad.related_messages:
        for m in post_ad.related_messages:
            await call.bot.edit_message_media(
                media=InputMedia(media=m.photo_file_id),
                chat_id=config.tg_bot.channel_id,
                message_id=m.message_id
            )
            if m.message_id == post_id:
                await call.bot.edit_message_caption(
                    chat_id=config.tg_bot.channel_id,
                    message_id=m.message_id,
                    caption=ad.post()
                )
    elif post_ad.related_messages:
        await call.bot.edit_message_caption(
            chat_id=config.tg_bot.channel_id,
            message_id=post_ad.post_id,
            caption=ad.post()
        )
    else:
        await call.bot.edit_message_text(
            chat_id=config.tg_bot.channel_id,
            message_id=post_ad.post_id,
            text=ad.post()
        )
    await session.commit()
    await call.answer(text="Объявление было успешно обновлено!")
    widget_data.clear()
    await manager.switch_to(ShowMyAd.true)


async def set_edit_default(_, dialog_manager: DialogManager):
    session = dialog_manager.data.get("session")
    post_id = dialog_manager.current_context().start_data.get("post_id")
    post_ad: PostAd = await session.get(PostAd, post_id)
    if post_ad.post_type in ("sell", "rent"):
        await dialog_manager.dialog().find('negotiable').set_checked(event=dialog_manager.event,
                                                                     checked=post_ad.negotiable)
        await dialog_manager.dialog().find('currency_code').set_checked(event="", item_id=post_ad.currency_code)
