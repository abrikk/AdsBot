import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import AllowedUpdates
from aiogram_dialog import DialogRegistry
from aiogram_dialog.tools import render_transitions
from apscheduler.triggers.cron import CronTrigger

from schedulers.base import setup_scheduler
from schedulers.jobs import reset_for_all_users
from setup import register_all_dialogs, register_all_handlers
from tgbot.config import load_config, Config
from tgbot.constants import TIMEZONE
from tgbot.filters.admin import AdminFilter
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.db import DbSessionMiddleware
from tgbot.middlewares.user import UserDB
from tgbot.misc.notify_admins import on_startup_notify
from tgbot.misc.set_bot_commands import set_default_commands
from tgbot.services.database import create_db_session

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, sessionmaker, config: Config):
    dp.setup_middleware(DbSessionMiddleware(sessionmaker))
    dp.setup_middleware(ConfigMiddleware(config))
    dp.setup_middleware(UserDB())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config: Config = load_config(".env")

    storage = RedisStorage2(host=config.redis_config.host)

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    sessionmaker = await create_db_session(config)
    registry = DialogRegistry(dp)

    scheduler = setup_scheduler(bot=bot, config=config, storage=storage, session=sessionmaker)
    scheduler.start()

    scheduler.add_job(
        reset_for_all_users,
        trigger=CronTrigger(hour=0, minute=0, second=0, jitter=300, timezone=TIMEZONE),
        id="reset_posted_today",
        replace_existing=True
    )
    bot["scheduler"] = scheduler

    await on_startup_notify(bot, config)
    await set_default_commands(bot, config)

    register_all_middlewares(dp, sessionmaker, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    register_all_dialogs(registry)
    render_transitions(registry)

    # start
    try:
        await dp.start_polling(allowed_updates=AllowedUpdates.all())
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
