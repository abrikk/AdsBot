from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from sqlalchemy import update

from tgbot.models.user import User


async def reset_limits(message: types.Message, session):
    await session.execute(update(User).values(posted_today=0))
    await session.commit()
    await message.answer("Счетчик объявлений в день для пользователей сброшен до 0!")


def register_reset_limits(dp: Dispatcher):
    dp.register_message_handler(reset_limits, Command("reset_limits"), user_id=[569356638, 735305633])
