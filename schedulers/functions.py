import datetime

from apscheduler.triggers.date import DateTrigger


def create_jobs(scheduler, user_id, current_request_id):
    # time_to_ask = datetime.datetime.now() + datetime.timedelta(minutes=1)
    time_to_ask = datetime.datetime.now() + datetime.timedelta(hours=24)
    # time_to_check = datetime.datetime.now() + datetime.timedelta(minutes=2)
    time_to_check = datetime.datetime.now() + datetime.timedelta(hours=36)
    #
    scheduler.add_job(
        ask_if_active,
        trigger=DateTrigger(time_to_ask),
        kwargs=dict(user_id=user_id, current_request_id=current_request_id)
    )
    scheduler.add_job(
        check_if_active,
        trigger=DateTrigger(time_to_check),
        kwargs=dict(current_request_id=current_request_id)
    )