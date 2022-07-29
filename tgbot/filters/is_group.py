from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class IsGroup(BoundFilter):
    async def check(self, obj: types.Message | types.ChatMemberUpdated, config: Config) -> bool:
        return obj.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        ) and obj.chat.id != config.chats.private_group_id
