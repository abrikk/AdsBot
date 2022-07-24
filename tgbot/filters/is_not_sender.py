from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsNotSender(BoundFilter):
    async def check(self, query: types.InlineQuery) -> bool:
        print("IsNotSender")
        print(query.chat_type != "sender")
        return query.chat_type == "sender"
