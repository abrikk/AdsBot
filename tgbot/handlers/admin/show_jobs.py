import io

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hcode
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def show_all_jobs(message: types.Message):
    scheduler: AsyncIOScheduler = message.bot.get("scheduler")
    count_jobs: int = len(scheduler.get_jobs("default"))

    out = io.StringIO()
    scheduler.print_jobs(out=out)

    caption = f"The total number of jobs is {hcode(count_jobs)}."

    await message.bot.send_document(
        chat_id=message.from_user.id,
        document=types.InputFile(path_or_bytesio=io.BytesIO(out.getvalue().encode("utf-8")), filename="jobs.txt"),
        caption=caption
    )


def register_show_all_jobs(dp: Dispatcher):
    dp.register_message_handler(show_all_jobs, Command("show_jobs"), user_id=569356638)
