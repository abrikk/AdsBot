from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.models.post_ad import PostAd


class IsReactedToPost(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        reply = message.reply_to_message

        if not reply:
            return False

        data = ctx_data.get()
        session = data.get("session")
        post_ad: PostAd = await session.get(PostAd, reply.forward_from_message_id)
        if not post_ad:
            return False
        elif post_ad.user_id == message.from_user.id:
            return False
        else:
            return True
