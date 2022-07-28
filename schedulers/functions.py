import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from schedulers.jobs import ask_if_active
from tgbot.constants import TIMEZONE


def create_jobs(scheduler: AsyncIOScheduler, user_id: int, post_id: int, channel_id: int, private_group_id: int,
                channel_username: str):
    time_to_ask = datetime.datetime.now(tz=pytz.timezone(TIMEZONE)) + datetime.timedelta(seconds=10)

    scheduler.add_job(
        ask_if_active,
        trigger=DateTrigger(time_to_ask, timezone=TIMEZONE),
        kwargs=dict(user_id=user_id, post_id=post_id, channel_username=channel_username,
                    channel_id=channel_id, private_group_id=private_group_id),
        id=f"ask_{post_id}"
    )
