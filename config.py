from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TASK_DELTA_DAYS = 1
DEFAULT_LOGS_DELTA_DAYS = 0
OLD_PAGES_FOLDER = "old_pages/"

CURRENT_TIMEZONE = ZoneInfo("America/Toronto")
CURRENT_DATE = datetime.now(CURRENT_TIMEZONE)
