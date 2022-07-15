from aiogram import Bot
from sqlalchemy.orm import sessionmaker

from schedulers.functions import make_link_to_post
from tgbot.constants import ACTIVE, INACTIVE
from tgbot.keyboards.inline import confirm_post
from tgbot.models.post_ad import PostAd


async def ask_if_active(user_id: int, post_id: int, channel_id: int, bot: Bot):
    await bot.send_message(
        user_id,
        f'Ваше объявление {make_link_to_post(channel_id, post_id)} еще актуальное?',
        reply_markup=confirm_post(post_id)
    )


async def check_if_active(user_id: int, post_id: int, channel_id: int, bot: Bot, session: sessionmaker):
    async with session() as session:
        post_ad: PostAd = await session.get(PostAd, post_id)

        if post_ad.status == ACTIVE:
            post_ad.status = INACTIVE
            await session.commit()
            await bot.delete_message(chat_id=channel_id, message_id=post_id)
            await bot.send_message(
                chat_id=user_id,
                text=f"Ваше объявление было удалено из канала, поскольку вы "
                     f"не подтвердили его актуальность."
            )
