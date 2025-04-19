import logging
import os
import textwrap
from datetime import datetime

from PIL import ImageDraw, Image, ImageOps
from PIL.Image import Image as ImageType
from tickthon import Task

from config import OLD_PAGES_FOLDER
from src.image_processor import (add_day_date_to_img, add_week_date_to_img, add_day_tasks_to_img, add_week_tasks_to_img,
                                 add_stats_to_img, add_journal_qr_to_img, add_journal_summary_to_img, add_date_to_logs_img)
from src.data_processor import DataProcessor


class PageProcessor:

    def __init__(self):
        self.data_processor = DataProcessor()

    def generate_daily_tasks_page(self, page_date: datetime) -> ImageType:
        """Generate daily tasks page.

        Args:
            page_date: Date to add to page.

        Returns:
            Image object with tasks page.
        """
        logging.info(f"Generating daily tasks page for {page_date}")

        tasks_page_base = Image.open("designs/bitacora_diaria_base_front_task.png")
        raw_tasks_page = ImageDraw.Draw(tasks_page_base)

        tasks_page_with_date = add_day_date_to_img(raw_tasks_page, page_date)

        task_data = self.data_processor.get_active_task_data(page_date.strftime("%Y-%m-%d"), 49)
        add_day_tasks_to_img(tasks_page_with_date, task_data)

        return tasks_page_base

    def generate_weekly_tasks_page(self, week_start_date: datetime) -> ImageType:
        """Generate tasks page.

        Args:
            week_start_date: Date to add to page.

        Returns:
            Image object with tasks page.
        """
        logging.info(f"Generating weekly tasks page for {week_start_date}")

        tasks_page_base = Image.open("designs/bitacora_semanal_base_front_task.png")
        raw_tasks_page = ImageDraw.Draw(tasks_page_base)

        tasks_page_with_date = add_week_date_to_img(raw_tasks_page, week_start_date)

        task_data = self.data_processor.get_active_task_data(date="", max_title_length=45, discard_tasks_with_parents=True)
        add_week_tasks_to_img(tasks_page_with_date, task_data)

        return tasks_page_base

    def generate_stats_page(self, page_date: datetime) -> ImageType:
        """Generate a stats page as an image for a given date.

        This function takes a date as an argument and generates the stats for the day, and a QR code for the journal of
        the day.

        Args:
            page_date: The date for which the logs page is to be generated.

        Returns:
            A PIL Image object representing the generated stats page.
        """
        logging.info(f"Generating stats page for {page_date}")

        stats_page_base = Image.open("designs/bitacora_diaria_base_front_stats.png")
        raw_logs_page = ImageDraw.Draw(stats_page_base)

        day_stats = self.data_processor.get_day_stats(page_date)
        add_stats_to_img(raw_logs_page, day_stats)

        day_journal_url = self.data_processor.get_day_journal_url(page_date)
        add_journal_qr_to_img(stats_page_base, day_journal_url)

        return stats_page_base

    def generate_journal_page(self) -> ImageType:
        """Generate a page with the daily journal.

        Returns:
            Image object with thoughts page.
        """
        journal_page_base = Image.open("designs/bitacora_diaria_base_journal.png")
        return journal_page_base

    @staticmethod
    def generate_logs_page(page_date: datetime) -> ImageType:
        """Generate a page to log activities through the day.

        Args:
            page_date: The date for which the logs page is to be generated.

        Returns:
            A PIL Image object representing the generated logs page.
        """
        logs_page_base = Image.open("designs/bitacora_diaria_base_front_logs.png")
        raw_logs_page = ImageDraw.Draw(logs_page_base)

        add_date_to_logs_img(raw_logs_page, page_date)

        return logs_page_base

    @staticmethod
    def generate_recap_page(raw_summary_recap: str) -> ImageType:
        """Generate a page with the daily recap.

        Args:
            raw_summary_recap: The daily recap to add to the page.

        Returns:
            A PIL Image object representing the generated recap page.
        """
        recap_page_base = Image.open("designs/bitacora_diaria_empty.png")
        raw_recap_page = ImageDraw.Draw(recap_page_base)

        summary_recap = "\n".join([textwrap.fill(paragraph, width=68) for paragraph in raw_summary_recap.split("\n")])

        add_journal_summary_to_img(raw_recap_page, summary_recap)
        return recap_page_base

    @staticmethod
    def generate_old_bitacora_pages(stats_page: ImageType, old_date: datetime) -> list[ImageType]:
        """Generate a front page as an image for a given date.

        This function takes a date as an argument and generates a front page as an image. The front page includes the
        tasks for the given date, the logs for the given date, the stats for the day, and a QR code for the journal of
        the day.

        Args:
            stats_page: The logs page to merge with the tasks page.
            old_date: The date for which the logs page is to be generated.

        Returns:
            A PIL Image object representing the generated front page.
        """
        logging.info(f"Generating front page for {old_date}")

        try:
            old_task_page = Image.open(f"{OLD_PAGES_FOLDER}/{old_date.strftime('%d-%b-%Y').lower()}-old-task-page.png")
            old_task_page.paste(stats_page, (0, 0), mask=ImageOps.invert(stats_page.copy().convert('L')))

            old_journal_page = Image.open(f"{OLD_PAGES_FOLDER}/{old_date.strftime('%d-%b-%Y').lower()}"
                                          f"-old-journal-page.png")
            old_recap_page = Image.open(f"{OLD_PAGES_FOLDER}/{old_date.strftime('%d-%b-%Y').lower()}-old-recap-page.png")

            return [old_task_page, old_journal_page, old_recap_page]
        except FileNotFoundError:
            logging.info(f"Old pages for {old_date} not found")

        return []

    @staticmethod
    def save_pages_as_pdf(page_title: str, pages: list[ImageType], open_after_save: bool = False):
        """Saves the given page as a PDF file and optionally opens it after saving.

        Args:
            page_title: The title of the page, which will be used as the filename for the saved PDF.
            pages: The ImageDraw object representing the page to be saved.
            open_after_save: A flag indicating whether to open the saved PDF file. Defaults to False.
        """
        logging.info(f"Saving {page_title}")
        filename = f"{page_title}.pdf"

        other_pages = pages[1:] if len(pages) > 1 else []
        if len(pages) > 0:
            pages[0].save(filename, "PDF", resolution=700, save_all=True, append_images=other_pages)

            if open_after_save:
                os.startfile(filename)

    @staticmethod
    def save_pages_as_png(page_title: str, page: ImageType):
        """Saves the given page as a PDF file and optionally opens it after saving.

        Args:
            page_title: The title of the page, which will be used as the filename for the saved PDF.
            page: The ImageDraw object representing the page to be saved.
        """
        logging.info(f"Saving {page_title}")
        filename = f"{page_title}.png"

        page.save(filename, "PNG")

    def upload_recap(self, summary_recap: str, tasks_date: datetime):
        self.data_processor.notion_client.create_note_page(title=f"Recap {tasks_date.strftime('%d-%b-%Y').lower()}",
                                                           page_type="note",
                                                           page_subtype=("day-recap",),
                                                           date=tasks_date,
                                                           content=summary_recap)

    def create_day_highlights(self, day_recap: list[str], date: datetime):
        highlight_identifier = "- !"
        highlights = [highlight.replace(highlight_identifier, "").strip()
                      for highlight in day_recap if highlight.startswith(highlight_identifier)]

        for highlight in highlights:
            highlight_task = Task(title=highlight, created_date=date.isoformat(),
                                  due_date="", ticktick_etag="", ticktick_id="")
            self.data_processor.notion_client.add_highlight_log(highlight_task)

    @staticmethod
    def generate_empty_page() -> ImageType:
        """Generate an empty page.

        Returns:
            Image object with empty page.
        """
        return Image.open("designs/bitacora_diaria_empty.png")
