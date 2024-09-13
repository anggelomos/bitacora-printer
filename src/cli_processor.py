from datetime import datetime, timedelta

from config import DEFAULT_TASK_DELTA_DAYS, DEFAULT_LOGS_DELTA_DAYS, CURRENT_DATE


def get_pages_dates() -> tuple[datetime, datetime | None]:
    """Gets the dates for which to generate pages.

    Returns:
        List[datetime]: The dates for the pages.
    """
    day_delta_offset = DEFAULT_TASK_DELTA_DAYS
    week_delta_offset = DEFAULT_LOGS_DELTA_DAYS

    user_day_date_offset = input(f"Enter the number of days to get tasks from today [{day_delta_offset}]: ")
    user_week_date_offset = input(f"Enter the number of days to get logs from today [{week_delta_offset}]: ")
    user_print_week = input("Do you want to print the weekly page? [y/n]: ").lower() == "y"

    if user_day_date_offset:
        day_delta_offset = int(user_day_date_offset)

    if user_week_date_offset:
        week_delta_offset = int(user_week_date_offset)

    day_date: datetime = CURRENT_DATE + timedelta(days=day_delta_offset)

    week_start_date: datetime | None = None
    if user_print_week:
        week_date = CURRENT_DATE + timedelta(weeks=week_delta_offset)
        week_start_date: datetime = week_date - timedelta(days=week_date.weekday())

    return day_date, week_start_date
