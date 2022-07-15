import datetime

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters import Command
from aiogram.types import ChatMemberUpdated
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.orm import sessionmaker

from tgbot.config import Config
# 1566111340, 304536646
from tgbot.models.user import User


async def test_job(bot: Bot, session: sessionmaker, message, *args):
    print(args)
    print(session)
    await bot.send_message(message.get("from").get("id"), "is it works?")


async def test(message: types.Message, session, config: Config):
    await message.bot.g
    # scheduler: AsyncIOScheduler = message.bot.get("scheduler")
    # print(scheduler.get_jobs("default"))
    # trigger = IntervalTrigger(seconds=10, start_date=datetime.datetime.now())
    # print(message.to_python())
    # scheduler.add_job(test_job, trigger,
    #                   id='123', replace_existing=True,
    #                   kwargs=dict(message=message.to_python()))


async def show_jobs(message: types.Message, session, config: Config):
    scheduler: ContextSchedulerDecorator = message.bot.get("scheduler")
    await message.answer(str(scheduler.get_jobs("default")))


async def delete_all_jobs(message: types.Message):
    scheduler: AsyncIOScheduler = message.bot.get("scheduler")
    scheduler.remove_all_jobs()
    await message.answer("All jobs have been deleted.\n\n"
                         f"The jobstore is: {scheduler.get_jobs()}")


def register_test(dp: Dispatcher):
    dp.register_message_handler(test, Command("test"))
    dp.register_message_handler(show_jobs, Command("show_jobs"))
    dp.register_message_handler(delete_all_jobs, Command("delete_all_jobs"))
