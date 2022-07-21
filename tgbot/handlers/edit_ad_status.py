from aiogram import types, Dispatcher
from aiogram.types import MediaGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.keyboards.inline import conf_cb
# from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage


async def catch_ad_status(call: types.CallbackQuery, callback_data: dict,
                          config: Config, session):
    scheduler: AsyncIOScheduler = call.bot.get('scheduler')
    post_id = int(callback_data.get('post_id'))
    status = callback_data.get('status')
    post_ad: PostAd = await session.get(PostAd, post_id)

    if status == INACTIVE:
        post_ad.status = INACTIVE
        await call.bot.delete_message(chat_id=config.tg_bot.channel_id, message_id=post_id)
        await session.commit()
    else:
        scheduler.remove_job("check_" + str(post_id))
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
        await call.answer(text="Объявление было успешно обновлено!")
    scheduler.remove_job(job_id=f"check_{post_id}")


def register_ad_status_handler(dp: Dispatcher):
    dp.register_callback_query_handler(catch_ad_status, conf_cb.filter())
