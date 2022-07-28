import logging
import datetime

import pytz
from aiogram import Bot
from aiogram.utils.exceptions import MessageToDeleteNotFound
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from tgbot.constants import TIMEZONE
from tgbot.handlers.create_ad.form import make_link_to_post
from tgbot.keyboards.inline import confirm_post, manage_post
from tgbot.models.post_ad import PostAd
from tgbot.models.user import User


async def ask_if_active(user_id: int, post_id: int, channel_username: str, channel_id: int,
                        private_group_id: int, bot: Bot, scheduler: BaseScheduler):
    ask_message = await bot.send_message(
        user_id,
        f'Ваше объявление {make_link_to_post(channel_username, post_id)} еще актуальное?',
        reply_markup=confirm_post(post_id),
        disable_web_page_preview=False
    )

    time_to_check = datetime.datetime.now(tz=pytz.timezone(TIMEZONE)) + datetime.timedelta(hours=12)
    scheduler.add_job(
        check_if_active,
        trigger=DateTrigger(time_to_check, timezone=TIMEZONE),
        kwargs=dict(user_id=user_id, post_id=post_id, channel_id=channel_id, private_group_id=private_group_id,
                    ask_message_id=ask_message.message_id),
        id=f"check_{post_id}"
    )


async def check_if_active(user_id: int, post_id: int, channel_id: int, private_group_id: int,
                          ask_message_id: int, bot: Bot, session: sessionmaker):
    async with session() as session:
        post_ad: PostAd = await session.get(PostAd, post_id)

        try:
            if post_ad.related_messages:
                for message in post_ad.related_messages:
                    await bot.delete_message(
                        chat_id=channel_id,
                        message_id=message.message_id
                    )
            else:
                await bot.delete_message(
                    chat_id=channel_id,
                    message_id=post_ad.post_id
                )
        except MessageToDeleteNotFound:
            logging.warning("Message to delete not found")

        await session.delete(post_ad)
        await session.commit()

        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=ask_message_id,
            reply_markup=None
        )

        await bot.send_message(
            chat_id=user_id,
            text=f"Ваше объявление было удалено из канала, поскольку вы "
                 f"не подтвердили его актуальность.",
            reply_to_message_id=ask_message_id
        )

        await bot.edit_message_text(
            text=f"#УдаленоВременем\n\n"
                 f"Объявление пользователя c идентификатором <code>{user_id}</code> было удалено с канала, "
                 f"так как пользователь не подтвердил актуальность объявления ‼️",
            chat_id=private_group_id,
            message_id=post_ad.admin_group_message_id,
            reply_markup=manage_post(user_id, argument="only_search_user")
        )


async def reset_for_all_users(session: sessionmaker):
    async with session() as session:
        await session.execute(update(User).values(posted_today=0))
        await session.commit()
