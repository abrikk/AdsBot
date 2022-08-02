from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.config import Config


class IsGroup(BoundFilter):
    async def check(self, obj: types.Message | types.ChatMemberUpdated) -> bool:
        data = ctx_data.get()
        config: Config = data["config"]
        await obj.bot.send_message(
            chat_id=config.chats.errors_channel_id,
            text=f"getting update in func check"
        )
        return obj.chat.type in (types.ChatType.SUPERGROUP,)
