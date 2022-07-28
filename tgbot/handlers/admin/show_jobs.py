import os
from io import StringIO
from pathlib import Path

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hcode
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def show_all_jobs(message: types.Message):
    out_dir = os.getcwd() + '/tgbot/handlers/admin'
    scheduler: AsyncIOScheduler = message.bot.get("scheduler")
    out = StringIO()
    scheduler.print_jobs(out=out)
    jobs: list = out.getvalue().split("\n")

    with open(file=os.path.join(out_dir, "jobs.txt"), mode="w+") as txt_file:
        txt_file.seek(0)

        txt_file.writelines("\n".join(jobs))

    caption = f"The total number of jobs is {hcode(len(jobs))}."

    await message.bot.send_document(
        chat_id=message.from_user.id,
        document=types.InputFile(Path(txt_file.name)),
        caption=caption
    )


def register_show_all_jobs(dp: Dispatcher):
    dp.register_message_handler(show_all_jobs, Command("show_jobs"), user_id=569356638)
