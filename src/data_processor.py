import logging
import os
from datetime import datetime

from typing import List

from nothion import NotionClient, PersonalStats
from nothion._config import NT_NOTES_DB_ID
from nothion._notion_table_headers import NotesHeaders
from tickthon import TicktickClient, Task


class DataProcessor:
    def __init__(self):
        self.ticktick_client = TicktickClient(os.getenv("TT_USER"), os.getenv("TT_PASS"))
        self.notion_client = NotionClient(os.getenv("NT_AUTH"))

    def _process_task_title(self, task: Task) -> str:
        """Extract and process task titles.

        The task titles will be processed in the following way:

        * The task title starts with a character that indicates the task type.
        ^: Work task
        -: Personal task
        ~: Project task

        * Important tasks will have an exclamation mark before the type character, for example ^!.

        * The task titles will have a maximum length, if the title is longer it will be truncated with
        an ellipsis.

        Args:
            task: Task to process.

        Returns:
            Processed tasks title.
        """
        task_type = ""
        if "work" in task.tags:
            task_type = "^"

        important_task = ""
        if "main-task" in task.tags:
            important_task = "!"

        task_title = task.title.strip()
        max_char_length = 52
        if len(task_title) >= max_char_length:
            task_title = task_title[:max_char_length].strip() + "..."

        return f"{important_task}{task_type}{task_title}"

    def get_day_active_task_titles(self, date: str) -> list[tuple[str, str]]:
        """Get active tasks for a given date.

        Args:
            date: Date for which to get tasks in the format YYYY-MMM-DD.

        Returns:
            List of processed tasks titles for given date ordered chronologically with the following format:
            (task_title, task_date)
        """
        logging.info(f"Getting active tasks for date {date}")

        active_tasks = self.ticktick_client.get_active_tasks()
        day_tasks = [task for task in active_tasks if task.due_date.startswith(date)]
        sorted_tasks = sorted(day_tasks, key=lambda task: task.due_date)

        max_amount_tasks = 23
        raw_tasks = sorted_tasks[:max_amount_tasks]

        processed_task_titles = [(self._process_task_title(task),
                                  datetime.fromisoformat(task.due_date).strftime("%I:%M%p").lower())
                                 for task in raw_tasks]

        return processed_task_titles

    def _process_log_titles(self, logs: List[Task]) -> List[str]:
        max_amount_logs = 20
        logs = logs[:max_amount_logs]

        processed_logs = []
        for log in logs:
            log_title = f"{datetime.fromisoformat(log.created_date).strftime('%I:%M %p').lower()} {log.title}"
            log_title = log_title.strip()

            if "highlight" in log.tags:
                log_title = f" щ {log_title}"

            max_char_length = 62
            if len(log_title) >= max_char_length:
                log_title = log_title[:max_char_length] + "..."

            processed_logs.append(log_title)

        return processed_logs

    def get_day_logs(self, date: str) -> List[str]:
        logging.info(f"Getting active tasks for date {date}")

        all_logs = self.ticktick_client.get_day_logs()

        day_logs = [task for task in all_logs if task.created_date.startswith(date)]
        sorted_logs = sorted(day_logs, key=lambda task: task.created_date)
        log_titles = self._process_log_titles(sorted_logs)

        return log_titles

    def get_day_stats(self, date: datetime) -> PersonalStats:
        logging.info(f"Getting stats for date {date}")
        return self.notion_client.get_stats_between_dates(date, date)[0]

    def get_day_journal_url(self, date: datetime) -> str:
        logging.info(f"Getting journal url for date {date}")

        payload = {"filter": {"and": [
            {"property": NotesHeaders.TYPE.value, "select": {"equals": "journal"}},
            {"property": NotesHeaders.SUBTYPE.value, "multi_select": {"contains": "daily"}},
            {"property": NotesHeaders.DUE_DATE.value, "date": {"equals": date.strftime("%Y-%m-%d")}}
        ]},
            "page_size": 1
        }
        return self.notion_client.notion_api.query_table(NT_NOTES_DB_ID, payload)[0].get("url", "")
