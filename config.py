from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TASK_DELTA_DAYS = 0
DEFAULT_LOGS_DELTA_DAYS = 0
OLD_PAGES_FOLDER = "old_pages"
NEW_PAGES_FOLDER = "C:/Users/angel/My Drive/bitacora-prints"

CURRENT_TIMEZONE = ZoneInfo("America/Bogota")
CURRENT_DATE = datetime.now(CURRENT_TIMEZONE)
