from aiogram import types, Dispatcher
from aiogram.utils.markdown import hlink

from tgbot.config import Config
from tgbot.filters.is_group import IsGroup
from tgbot.filters.is_reacted_to_post import IsReactedToPost
from tgbot.handlers.buy_and_sell.form import make_link_to_post
from tgbot.models.post_ad import PostAd


async def catch_post_reaction(message: types.Message, session, config: Config):
    print(message.chat.id)
    print("catch_post_reaction")
    post_id: int = message.reply_to_message.forward_from_message_id
    post_ad: PostAd = await session.get(PostAd, post_id)
    link_to_post: str = make_link_to_post(config.tg_bot.channel_id, post_ad.post_id)
    text = (f"На ваше {hlink('объявление', link_to_post)} отреагировал пользователь"
            f" {message.from_user.get_mention()}\n\n"
            f"«<i>{message.text}</i>»")
    print(post_ad.user_id)
    await message.bot.send_message(
        chat_id=post_ad.user_id,
        text=text
    )


def register_post_reaction(dp: Dispatcher):
    dp.register_message_handler(catch_post_reaction, IsGroup(), IsReactedToPost())
