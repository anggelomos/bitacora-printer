from datetime import datetime, timedelta

from config import DEFAULT_TASK_DELTA_DAYS, DEFAULT_LOGS_DELTA_DAYS, CURRENT_DATE


def get_pages_dates() -> tuple[datetime, datetime]:
    """Gets the dates for which to generate pages.

    Returns:
        List[datetime]: A list of datetime objects representing the dates for which to generate pages.
    """
    tasks_delta_days = DEFAULT_TASK_DELTA_DAYS
    logs_delta_days = DEFAULT_LOGS_DELTA_DAYS

    user_tasks_delta_days = input(f"Enter the number of days to get tasks from today [{tasks_delta_days}]: ")
    user_logs_delta_days = input(f"Enter the number of days to get logs from today [{logs_delta_days}]: ")

    if user_tasks_delta_days:
        tasks_delta_days = int(user_tasks_delta_days)

    if user_logs_delta_days:
        logs_delta_days = int(user_logs_delta_days)

    tasks_date: datetime = CURRENT_DATE + timedelta(days=tasks_delta_days)
    logs_date: datetime = CURRENT_DATE + timedelta(days=logs_delta_days)

    return tasks_date, logs_date
