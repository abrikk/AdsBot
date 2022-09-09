import datetime

import pytz
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tgbot.constants import BANNED
from tgbot.models.user import User


class UserDB(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update", "channel_post", "edited_channel_post"]

    async def pre_process(self, obj, data, *args):
        if obj.from_user.id == 777000:
            raise CancelHandler()

        session = data.get("session")
        user = await session.get(User, obj.from_user.id)

        if user and user.role == BANNED:
            raise CancelHandler()

        if user:
            if user.restricted_till and user.restricted_till < datetime.datetime.now(tz=pytz.timezone("utc")):
                user.restricted_till = None

            if user.first_name != obj.from_user.first_name:
                user.first_name = obj.from_user.first_name
            if user.last_name != obj.from_user.last_name:
                user.last_name = obj.from_user.last_name
            if user.username != obj.from_user.username:
                user.username = obj.from_user.username
            await session.commit()

        data["user"] = user if user else None

    async def post_process(self, obj, data, *args):
        del data["user"]
