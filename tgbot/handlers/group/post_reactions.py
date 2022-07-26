from aiogram import types, Dispatcher
from aiogram.utils.markdown import hlink

from tgbot.config import Config
from tgbot.filters.is_group import IsGroup
from tgbot.filters.is_reacted_to_post import IsReactedToPost
from tgbot.handlers.create_ad.form import make_link_to_post
from tgbot.models.post_ad import PostAd


async def catch_post_reaction(message: types.Message, session, config: Config):
    post_id: int = message.reply_to_message.forward_from_message_id
    post_ad: PostAd = await session.get(PostAd, post_id)
    channel = await message.bot.get_chat(config.tg_bot.channel_id)
    link_to_post: str = make_link_to_post(channel.username, post_ad.post_id)
    text = (f"На ваше {hlink('объявление', link_to_post)} отреагировал пользователь"
            f" {message.from_user.get_mention()}\n\n"
            f"«<i>{message.text}</i>»")

    await message.bot.send_message(
        chat_id=post_ad.user_id,
        text=text
    )


def register_post_reaction(dp: Dispatcher):
    dp.register_message_handler(catch_post_reaction, IsGroup(), IsReactedToPost())
