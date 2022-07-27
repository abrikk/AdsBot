from aiogram import Dispatcher
from aiogram.types import Update
from aiogram.utils.markdown import hcode

from tgbot.config import Config


async def errors_handler(update: Update, exception, config: Config):
    text = f"An exception of type {hcode(type(exception).__name__)} occurred.\n\n" \
           f"⚠️ Error: {hcode(exception)}"
    await update.bot.send_message(
        chat_id=config.chats.errors_channel_id,
        text=text
    )


def register_error_handler(dp: Dispatcher):
    dp.register_errors_handler(errors_handler)
