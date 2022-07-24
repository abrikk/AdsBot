from aiogram.types import CallbackQuery, MediaGroup
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from schedulers.functions import create_jobs
from tgbot.config import Config
from tgbot.misc.ad import Ad
from tgbot.misc.states import Main
from tgbot.models.post_ad import PostAd
from tgbot.models.related_messages import RelatedMessage


async def make_fucking_ad(call: CallbackQuery, button: Button, manager: DialogManager):
    config: Config = manager.data.get("config")
    session = manager.data.get("session")

    photos = [
        'AgACAgIAAx0EYgSI8gACAadi3S4Oa-nO85WVxBjfeD8PelaLvAACB70xG2eZ6EqRh1y7DN7TrQEAAwIAA3kAAykE',
        'AgACAgIAAx0EYgSI8gACAahi3S4OyKyY7oZQT4z1AyEyVTJz-gACBb0xG2eZ6Erjb3ZYrTrYPwEAAwIAA3gAAykE',
        'AgACAgIAAx0EYgSI8gACAali3S4OLchiKgnWgqnGS0FvCNgD6AACBr0xG2eZ6EpeIeHi6Vf85QEAAwIAA3gAAykE'
    ]

    data: dict = {
        "tag_category": "Товар",
        "tag_name": "Одежда",
        "description": "qwerty",
        "contacts": [123, 456],
        "price": 666,
        "currency_code": "RUB",
        "negotiable": True,
        "photos": photos,
        "mention": call.from_user.get_mention()
    }

    ad: Ad = Ad(
        state_class="sell",
        **data
    )

    album = MediaGroup()

    for file_id in ad.photos[:-1]:
        album.attach_photo(photo=file_id)

    album.attach_photo(
        photo=ad.photos[-1],
        caption=ad.post()
    )

    sent_post = await call.bot.send_media_group(
        chat_id=config.tg_bot.channel_id,
        media=album
    )

    post_id = sent_post[-1].message_id
    message_ids = [
        RelatedMessage(
            post_id=post_id,
            message_id=message.message_id,
            photo_file_id=message.photo[-1].file_id,
            photo_file_unique_id=message.photo[-1].file_unique_id
        ) for message in sent_post
    ]

    post_ad: PostAd = PostAd(
        post_id=post_id,
        post_type="sell",
        user_id=call.from_user.id,
        tag_category=ad.tag_category,
        tag_name=ad.tag_name,
        description=ad.description,
        price=ad.price,
        contacts=",".join(map(str, ad.contacts)),
        currency_code=ad.currency_code,
        negotiable=ad.negotiable,
        related_messages=message_ids
    )

    session.add(post_ad)
    await session.commit()
    scheduler = call.bot.get("scheduler")
    channel = await call.bot.get_chat(config.tg_bot.channel_id)
    create_jobs(scheduler, call.from_user.id, post_ad.post_id, channel.id, channel.username)
    await call.answer("Объявление было успешно опубликовано в канале!")
    await manager.start(Main.main, mode=StartMode.RESET_STACK)

