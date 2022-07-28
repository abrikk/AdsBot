from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data


class IsUserExist(BoundFilter):
    async def check(self, obj: types.Message | types.InlineQuery) -> bool:
        data = ctx_data.get()
        user = data["user"]
        if not user:
            return False
        return True
