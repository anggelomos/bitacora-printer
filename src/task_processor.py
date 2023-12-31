import logging
from datetime import datetime

from dateutil import parser, tz
from typing import List, Optional

from tickthon import TicktickClient, Task
from src.data.task_ticktick_parameters import TaskTicktickParameters as ttp


class TaskProcessor:
    active_tasks = {}
    notion_ids = {}
    BASE_URL = "/api/v2"
    get_state_path = BASE_URL + "/batch/check/0"

    def __init__(self, ticktick_username: str, ticktick_password: str):
        self.ticktick_client = TicktickClient(ticktick_username, ticktick_password)

    @staticmethod
    def _get_task_date(task: dict, return_date_object: bool = False) -> Optional[str | datetime]:
        """Get date for a given task.

        Args:
            task: Task for which to get date.
            return_date_object: Whether to return a date object or a string.

        Returns:
            Date for given task, if it is a string it will be in format YYYY-MM-DD.
        """
        if ttp.START_DATE not in task:
            return None

        task_timezone = tz.gettz(task[ttp.TIMEZONE])
        task_raw_date = parser.parse(task[ttp.START_DATE])

        localized_task_date = task_raw_date.astimezone(task_timezone)

        if return_date_object:
            return localized_task_date
        return localized_task_date.strftime("%Y-%m-%d")

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
            max_char_length = 43
            if len(task_title) >= max_char_length:
                task_title = task_title[:max_char_length].strip() + "..."

            processed_task_titles.append(f"{task_type}{important_task}{task_title}")

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
