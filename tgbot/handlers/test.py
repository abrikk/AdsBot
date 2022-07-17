import asyncio
import datetime

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters import Command
from aiogram.types import ChatMemberUpdated, MediaGroup, InputMedia, InputFile
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


# 152 153 154


async def test_1(message: types.Message):
    await message.answer(message.message_id)
    await message.bot.delete_message(message.chat.id, message.message_id)


# AgACAgIAAxkBAAIXJ2LSgO_PFQXv3h0fqrXMQWavWqfTAALLvDEbjj2ZStu7MGbidBzDAQADAgADeQADKQQ
async def test_2(message: types.Message, config: Config):
    # await message.answer(message.message_id)
    # await message.bot.delete_message(message.chat.id, message.message_id)

    # m = await message.bot.send_message(chat_id=config.tg_bot.channel_id,
    #                                    text="Какой-то текст")
    # print(m.message_id)

    # album = MediaGroup()
    # album.attach_photo(photo="AgACAgIAAxkBAAIVBmLRUwHKZekXiyGyGM4YRTyVxqRFAAJXvzEbF0aISkcWyJnF_7kmAQADAgADeAADKQQ")
    # album.attach_photo(photo="AgACAgIAAxkBAAIVCGLRUwZC35cG8T4Y-u1po9sSzFLRAAJYvzEbF0aISr2wEHmArZHWAQADAgADbQADKQQ")
    # album.attach_photo(
    #     photo="AgACAgIAAxkBAAIVCmLRUwvCPSr3s2j-UFyICS0-X-EgAAJZvzEbF0aISngOcG2LDTaVAQADAgADbQADKQQ",
    #     caption="Какое то описание"
    # )
    x = "AgACAgIAAxkBAAIXJ2LSgO_PFQXv3h0fqrXMQWavWqfTAALLvDEbjj2ZStu7MGbidBzDAQADAgADeQADKQQ"
    await message.bot.edit_message_media(chat_id=config.tg_bot.channel_id,
                                         message_id=153,
                                         media=InputMedia(
                                             media=x))
    # await message.bot.edit_message_caption(chat_id=config.tg_bot.channel_id,
    #                                        message_id=154,
    #                                        caption=None)

    # post = await message.bot.send_media_group(chat_id=config.tg_bot.channel_id,
    #                                           media=album)
    # for p in post:
    #     print(p.message_id)


async def delete_all_jobs(message: types.Message):
    scheduler: AsyncIOScheduler = message.bot.get("scheduler")
    scheduler.remove_all_jobs()
    await message.answer("All jobs have been deleted.\n\n"
                         f"The jobstore is: {scheduler.get_jobs()}")


def register_test(dp: Dispatcher):
    dp.register_message_handler(test_1, Command("delete_me"))
    # dp.register_message_handler(test_2, content_types="photo")
    dp.register_message_handler(test_2, Command("sent_m"))
    dp.register_message_handler(test, Command("test"))
    dp.register_message_handler(show_jobs, Command("show_jobs"))
    dp.register_message_handler(delete_all_jobs, Command("delete_all_jobs"))
