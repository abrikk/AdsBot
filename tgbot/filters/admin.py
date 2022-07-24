from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data


class AdminFilter(BoundFilter):
    async def check(self, obj: types.Message | types.InlineQuery) -> bool:
        data = ctx_data.get()
        user = data["user"]
        return user.role in ("admin", "owner")
