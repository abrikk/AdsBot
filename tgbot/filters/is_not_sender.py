from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsNotSender(BoundFilter):
    async def check(self, query: types.InlineQuery) -> bool:
        return query.chat_type != "sender"
