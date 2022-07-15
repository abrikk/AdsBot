from aiogram import types, Dispatcher
from aiogram.types import MediaGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.constants import INACTIVE
from tgbot.keyboards.inline import conf_cb
from tgbot.misc.ad import SalesAd, PurchaseAd
from tgbot.models.post_ad import PostAd


async def catch_ad_status(call: types.CallbackQuery, callback_data: dict,
                          config: Config, session):
    scheduler: AsyncIOScheduler = call.bot.get('scheduler')
    post_id = callback_data.get('post_id')
    status = callback_data.get('status')
    post_ad: PostAd = await session.get(PostAd, post_id)
    if status == INACTIVE:
        post_ad.status = INACTIVE
        await session.commit()
    else:
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

        ad = SalesAd(**data) if post_ad.post_type == "sell" else PurchaseAd(**data)

        if ad.photos_ids:
            album = MediaGroup()
            for file_id in ad.photos_ids[:-1]:
                album.attach_photo(photo=file_id)

            album.attach_photo(photo=ad.photos_ids[-1], caption=ad.post())

            post = await call.bot.send_media_group(chat_id=config.tg_bot.channel_id,
                                                   media=album)
        else:
            post = await call.bot.send_message(chat_id=config.tg_bot.channel_id,
                                               text=ad.post())

        post_ad.post_id = post[0].message_id
        await session.commit()
        await call.answer(text="Объявление было успешно обновлено!")
    scheduler.remove_job(job_id=f"check_{post_id}")


def register_ad_status_handler(dp: Dispatcher):
    dp.register_callback_query_handler(catch_ad_status, conf_cb.filter())
