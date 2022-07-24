from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.models.user import User


class IsUser(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        user_id = message.text.split(":")[-1].strip()
        if not user_id.isdigit():
            return False
        data = ctx_data.get()
        session = data.get("session")
        user: User = await session.get(User, int(user_id))
        return user is not None
