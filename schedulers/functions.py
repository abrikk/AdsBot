import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from schedulers.jobs import ask_if_active, check_if_active


def create_jobs(scheduler: AsyncIOScheduler, user_id: int, post_id: int, channel_id: int, private_group_id: int,
                channel_username: str):
    time_to_ask = datetime.datetime.now() + datetime.timedelta(seconds=10)

    time_to_check = datetime.datetime.now() + datetime.timedelta(seconds=20)

    scheduler.add_job(
        ask_if_active,
        trigger=DateTrigger(time_to_ask),
        kwargs=dict(user_id=user_id, post_id=post_id, channel_username=channel_username,
                    channel_id=channel_id, private_group_id=private_group_id),
        id=f"ask_{post_id}"
    )
    # scheduler.add_job(
    #     check_if_active,
    #     trigger=DateTrigger(time_to_check),
    #     kwargs=dict(user_id=user_id, post_id=post_id, channel_id=channel_id, private_group_id=private_group_id),
    #     id=f"check_{post_id}"
    # )
