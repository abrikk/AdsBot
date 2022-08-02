from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsGroup(BoundFilter):
    async def check(self, obj: types.Message | types.ChatMemberUpdated) -> bool:
        return obj.chat.type in (types.ChatType.SUPERGROUP,)
