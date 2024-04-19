import json
import logging
import os
from datetime import datetime, timezone, timedelta

from typing import List, Any

from nothion._config import NT_LOGS_DB_ID
from openai import OpenAI

from nothion import NotionClient, PersonalStats
from tickthon import TicktickClient, Task

from src.ai_prompts import AIPrompts
from src.data.active_task_model import ActiveTaskModel


class DataProcessor:
    def __init__(self):
        self.ticktick_client = TicktickClient(os.getenv("TT_USER"), os.getenv("TT_PASS"))
        self.notion_client = NotionClient(os.getenv("NT_AUTH"))
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def _process_task_title(self, task: Task) -> str:
        """Extract and process task titles.

        The task titles will have a maximum length, if the title is longer it will be truncated with
        an ellipsis.

        Args:
            task: Task to process.

        Returns:
            Processed tasks title.
        """
        task_title = task.title.strip()
        max_char_length = 54
        if len(task_title) >= max_char_length:
            task_title = task_title[:max_char_length].strip() + "..."

        return task_title

    @staticmethod
    def _get_tag_color(task: Task) -> str:
        """Get tag color for task.

        Args:
            task: Task to get tag color for.

        Returns:
            Tag color code.
        """
        tag_color = "#98b0fc"
        for tag in task.tags:
            match tag:
                case "task-active":
                    tag_color = "#d6e9ce"
                    break
                case "work":
                    tag_color = "#99cdf6"
                    break
                case "habit":
                    tag_color = "#ffeaa9"
                    break
                case "routine" | "task-routine":
                    tag_color = "#f7dd8b"
                    break
                case "scrum-ceremony":
                    tag_color = "#7b96c5"
                    break
                case "task-pasive":
                    tag_color = "#addba5"
                    break
                case "event":
                    tag_color = "#c595f4"
                    break
                case "reminder":
                    tag_color = "#ccd2e0"
                    break

        return tag_color

    def get_day_active_task_data(self, date: str) -> list[ActiveTaskModel]:
        """Get active tasks for a given date.

        Args:
            date: Date for which to get tasks in the format YYYY-MMM-DD.

        Returns:
            List of processed tasks titles for given date ordered chronologically with the following format:
            (task_title, task_date, task_tag_color_code, column_id)
        """
        logging.info(f"Getting active tasks for date {date}")

        active_tasks = self.ticktick_client.get_active_tasks()
        sorted_tasks = sorted(active_tasks, key=lambda task: task.due_date)

        processed_task_titles = [ActiveTaskModel(self._process_task_title(task),
                                                 datetime.fromisoformat(task.due_date).strftime("%I:%M%p").lower()
                                                 if task.due_date else "",
                                                 self._get_tag_color(task),
                                                 task.column_id)
                                 for task in sorted_tasks]

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
        return self.notion_client.get_daily_journal_data(date).get("url", "")

    def _find_value_recursively(self, raw_list: list, key: str) -> list:
        """Find a value in a list of lists recursively.

        Args:
            raw_list: List of lists to search for value.
            key: Key to search for.

        Returns:
            List of values found.
        """
        found_values = []
        for item in raw_list:
            if isinstance(item, list):
                found_values.extend(self._find_value_recursively(item, key))
            elif isinstance(item, str) and key in item.lower():
                return raw_list
        return found_values

    def _flatten_list_recursively(self, nested_list: list) -> list[Any]:
        """Flatten a list of lists recursively.

        Args:
            nested_list: List of lists to flatten.

        Returns:
            List with one level of nesting.
        """
        flattened_list = []
        for item in nested_list:
            if isinstance(item, list):
                flattened_list.extend(self._flatten_list_recursively(item))
            else:
                flattened_list.append(item)
        return flattened_list

    def _get_journal_content(self, date: datetime, keyword: str, start_block: int) -> list:
        raw_journal_content = self.notion_client.get_daily_journal_content(date)

        journal_reflection = self._find_value_recursively(raw_journal_content, keyword).pop()
        journal_reflection_summary = self._flatten_list_recursively(journal_reflection[start_block:])

        return journal_reflection_summary

    def get_day_journal(self, date: datetime) -> list[str]:
        logging.info(f"Getting journal for date {date}")
        return self._get_journal_content(date, "night reflection", 2)

    def get_day_recap(self, date: datetime) -> list[str]:
        logging.info(f"Getting recap for date {date}")
        return self._get_journal_content(date, "day logs", 0)

    def generate_recap_summary(self, raw_recap_logs: list[str]) -> str:
        logging.info("Getting recap summary for date")

        recap_logs = "\n".join(raw_recap_logs)
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=AIPrompts.summarize_day_recap(recap_logs),
            temperature=0.6,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message.content
