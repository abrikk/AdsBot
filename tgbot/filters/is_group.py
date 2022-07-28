from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsGroup(BoundFilter):
    async def check(self, obj: types.Message | types.ChatMemberUpdated) -> bool:
        return obj.chat.type == types.ChatType.SUPERGROUP and obj.chat.id != -1001721012737
