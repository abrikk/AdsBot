from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsGroup(BoundFilter):
    async def check(self, obj: types.Message | types.ChatMemberUpdated) -> bool:
        print("smth")
        return obj.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
        )
