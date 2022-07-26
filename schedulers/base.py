from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config, Config


def setup_scheduler(bot: Bot = None, config: Config = None, storage: RedisStorage2 = None, session=None):
    if not config:
        config = load_config()

    job_stores = {
        "default": RedisJobStore(
            db=config.redis_config.db,
            host=config.redis_config.host,
            port=config.redis_config.port,
            jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running"
        )
    }

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(jobstores=job_stores, timezone='Europe/Kiev')
    )
    if not bot:
        bot = Bot(config.tg_bot.token)
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(scheduler, declared_class=BaseScheduler)
    scheduler.ctx.add_instance(storage, declared_class=RedisStorage2)
    scheduler.ctx.add_instance(session, declared_class=sessionmaker)

    return scheduler
