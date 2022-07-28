import os
import traceback
from pathlib import Path

from aiogram import Dispatcher, types
from aiogram.types import Update
from aiogram.utils.markdown import hcode

from tgbot.config import Config


async def errors_handler(update: Update, exception: Exception, config: Config):
    traceback_of_exception_lines = traceback.format_tb(exception.__traceback__)

    out_dir = os.getcwd()+'/tgbot/handlers/errors'

    with open(file=os.path.join(out_dir, "traceback.txt"), mode="w+") as txt_file:
        txt_file.seek(0)

        for line in traceback_of_exception_lines:
            txt_file.write(line)

    caption = f"An exception of type {hcode(type(exception).__name__)} occurred.\n\n" \
              f"⚠️ Error: {hcode(exception)}"

    await update.bot.send_document(
        chat_id=config.chats.errors_channel_id,
        document=types.InputFile(Path(txt_file.name)),
        caption=caption
    )


def register_error_handler(dp: Dispatcher):
    dp.register_errors_handler(errors_handler)
