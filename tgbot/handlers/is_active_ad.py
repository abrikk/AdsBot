import logging

from aiogram import types, Dispatcher
from aiogram.types import MediaGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from schedulers.functions import create_jobs
from tgbot.config import Config
from tgbot.handlers.create_ad.form import make_link_to_post
from tgbot.keyboards.inline import conf_cb, show_posted_ad, manage_post

from tgbot.misc.ad import Ad
from tgbot.models.post_ad import PostAd


async def update_ad(call: types.CallbackQuery, callback_data: dict,
                          config: Config, session):
    bot = call.bot
    scheduler: AsyncIOScheduler = call.bot.get('scheduler')
    post_id = int(callback_data.get('post_id'))
    scheduler.remove_job(job_id=f"check_{post_id}")

    action = callback_data.get('action')
    post_ad: PostAd = await session.get(PostAd, post_id)
    channel = await call.bot.get_chat(config.tg_bot.channel_id)

    try:
        if post_ad.related_messages:
            for message in post_ad.related_messages:
                await bot.delete_message(
                    chat_id=config.tg_bot.channel_id,
                    message_id=message.message_id
                )
        else:
            await bot.delete_message(
                chat_id=config.tg_bot.channel_id,
                message_id=post_ad.post_id
            )
    except MessageToDeleteNotFound:
        logging.warning("Message to delete not found")

    if action == "no":
        await session.delete(post_ad)
        await call.message.answer("Ваше объявление было удалено, поскольку оно больше не актуально.")
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        await bot.edit_message_text(
            text=call.message.text + "\n\nОбъявление было удалено в канале!⚠️",
            chat_id=call.from_user.id,
            message_id=call.message.message_id
        )

        await bot.edit_message_text(
            text=f"#НеАктуальноеОбъявление\n\n"
                 f"Объявление пользователя c идентификатором <code>{call.from_user.id}</code> было удалено с канала, "
                 f"так как пользователь посчитал что оно больше не актуально 📛",
            chat_id=config.tg_bot.private_group_id,
            message_id=post_ad.admin_group_message_id,
            reply_markup=manage_post(call.from_user.id, call.from_user.full_name, argument="only_search_user")
        )

    else:
        data: dict = {
            "tag_category": post_ad.tag_category,
            "tag_name": post_ad.tag_name,
            "description": post_ad.description,
            "price": post_ad.price,
            "contacts": post_ad.contacts.split(","),
            "currency_code": post_ad.currency_code,
            "negotiable": post_ad.negotiable,
            "photos": {m.photo_file_unique_id: m.photo_file_id for m in post_ad.related_messages} if post_ad.related_messages else {},
            "mention": call.from_user.get_mention(),
            "post_link": make_link_to_post(channel_username=channel.username, post_id=post_ad.post_id),
            "updated_at": post_ad.updated_at,
            "created_at": post_ad.created_at
        }

        ad: Ad = Ad(
            state_class=post_ad.post_type,
            **data
        )

        if len(ad.photos) > 1:
            album = MediaGroup()

            for file_id in list(ad.photos.values())[:-1]:
                album.attach_photo(photo=file_id)

            album.attach_photo(
                photo=list(ad.photos.values())[-1],
                caption=ad.post()
            )

            sent_post = await bot.send_media_group(
                chat_id=config.tg_bot.channel_id,
                media=album
            )

        elif ad.photos:
            sent_post = await bot.send_photo(
                chat_id=config.tg_bot.channel_id,
                photo=list(ad.photos.values())[0],
                caption=ad.post()
            )

        else:
            sent_post = await bot.send_message(
                chat_id=config.tg_bot.channel_id,
                text=ad.post()
            )

        if isinstance(sent_post, list):
            post_id = sent_post[-1].message_id
            for message, related_message in zip(sent_post, post_ad.related_messages):
                related_message.post_id = post_id
                related_message.message_id = message.message_id
                related_message.photo_file_id = message.photo[-1].file_id
                related_message.photo_file_unique_id = message.photo[-1].file_unique_id

        elif sent_post.photo:
            post_id = sent_post.message_id
            related_message = post_ad.related_messages[0]
            related_message.post_id = post_id
            related_message.message_id = sent_post.message_id
            related_message.photo_file_id = sent_post.photo[-1].file_id
            related_message.photo_file_unique_id = sent_post.photo[-1].file_unique_id

        else:
            post_id = sent_post.message_id

        post_ad.post_id = post_id
        await call.answer(text="Объявление было успешно обновлено в канале!")

        await bot.edit_message_text(
            text=call.message.text + "\n\nОбъявление было успешно обновлено в канале!✅",
            chat_id=call.from_user.id,
            message_id=call.message.message_id
        )
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=show_posted_ad(ad.post_link)
        )

        ad.post_link = make_link_to_post(channel_username=channel.username, post_id=post_ad.post_id)
        if not isinstance(sent_post, list) and sent_post.photo:
            await bot.edit_message_caption(
                chat_id=config.tg_bot.private_group_id,
                message_id=post_ad.admin_group_message_id,
                caption=ad.post(where="admin_group"),
                reply_markup=manage_post(post_id=post_id, user_id=call.from_user.id, full_name=call.from_user.full_name)
            )
        else:
            await bot.edit_message_text(
                chat_id=config.tg_bot.private_group_id,
                message_id=post_ad.admin_group_message_id,
                text=ad.post(where="admin_group"),
                reply_markup=manage_post(post_id=post_id, user_id=call.from_user.id, full_name=call.from_user.full_name)
            )

        channel = await call.bot.get_chat(config.tg_bot.channel_id)
        create_jobs(scheduler, call.from_user.id, post_ad.post_id, channel.id, config.tg_bot.private_group_id,
                    channel.username)

    await session.commit()


def register_ad_status_handler(dp: Dispatcher):
    dp.register_callback_query_handler(update_ad, conf_cb.filter())
