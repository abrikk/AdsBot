from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from tgbot.models.user import User


class ManageUser(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        chosen_user_id = message.get_args()
        if not (message.is_command() and chosen_user_id and message.get_command() == "/start"):
            return False

        data = ctx_data.get()
        current_user: User = data["user"]

        if current_user.role not in ("owner", "admin"):
            return False

        session = data.get("session")
        if not chosen_user_id.isdigit():
            return False

        chosen_user: User = await session.get(User, int(chosen_user_id))
        print(chosen_user is not None)
        return chosen_user is not None
