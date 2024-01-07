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

    def _process_task_titles(self, tasks: List[Task]) -> List[str]:
        """Extract and process task titles.

        The task titles will be processed in the following way:

        * The task title starts with a character that indicates the task type.
        ^: Work task
        -: Personal task
        ~: Project task

        * Important tasks will have an exclamation mark after the type character, for example ^!.

        * The task titles will have a maximum length of 33 characters, if the title is longer it will be truncated with
        an ellipsis.

        Args:
            tasks: List of tasks to process.

        Returns:
            List of processed tasks titles ordered chronologically.
        """
        max_amount_tasks = 11
        tasks = tasks[:max_amount_tasks]

        processed_task_titles = []
        for task in tasks:
            task_type = ""
            if not task.tags:
                task_type = ""
            elif "work" in task.tags:
                task_type = "^"

            important_task = ""
            if "main-task" in task.tags:
                important_task = "!"

            task_title = task.title.strip()
            max_char_length = 46
            if len(task_title) >= max_char_length:
                task_title = task_title[:max_char_length].strip() + "..."

            processed_task_titles.append(f"{important_task}{task_type}{task_title}")

        return processed_task_titles

    def get_day_active_task_titles(self, date: str) -> List[str]:
        """Get active tasks for a given date.

        Args:
            date: Date for which to get tasks in the format YYYY-MMM-DD.

        Returns:
            List of processed tasks titles for given date ordered chronologically.
        """
        logging.info(f"Getting active tasks for date {date}")

        active_tasks = self.ticktick_client.get_active_tasks()
        day_tasks = [task for task in active_tasks if task.due_date.startswith(date)]
        filtered_tasks = [task for task in day_tasks if all(tag not in task.tags for tag in ["routine", "habit"])]
        sorted_tasks = sorted(filtered_tasks, key=lambda task: task.due_date)
        task_titles = self._process_task_titles(sorted_tasks)

        return task_titles

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
