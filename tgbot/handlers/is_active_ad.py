import logging

from aiogram import types, Dispatcher
from aiogram.types import MediaGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.handlers.create_ad.form import make_link_to_post
from tgbot.keyboards.inline import conf_cb

from tgbot.misc.ad import Ad
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage


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

    else:
        data: dict = {
            "tag_category": post_ad.tag_category,
            "tag_name": post_ad.tag_name,
            "description": post_ad.description,
            "price": post_ad.price,
            "contacts": post_ad.contacts.split(","),
            "currency_code": post_ad.currency_code,
            "negotiable": post_ad.negotiable,
            "photos": [m.photo_file_id for m in post_ad.related_messages] if post_ad.related_messages else [],
            "post_link": make_link_to_post(channel_username=channel.username, post_id=post_ad.post_id),
            "mention": call.from_user.get_mention(),
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

        post_ad.post_id = post_id
        post_ad.related_messages = message_ids
        await call.answer(text="Объявление было успешно обновлено в канале!")

    await session.commit()

    print(scheduler.get_jobs("default"))


def register_ad_status_handler(dp: Dispatcher):
    dp.register_callback_query_handler(update_ad, conf_cb.filter())
