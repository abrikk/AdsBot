from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.models.post_ad import PostAd


class IsReactedToPost(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        print(message.reply_to_message)
        if not message.reply_to_message:
            return False
        data = ctx_data.get()
        session = data.get("session")
        print(1)
        post_ad: PostAd = await session.get(PostAd, message.reply_to_message.forward_from_message_id)
        print(post_ad)
        print(2)
        if not post_ad:
            print("really???")
            return False
        else:
            return True
