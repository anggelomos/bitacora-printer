import logging
import os
import textwrap
from datetime import datetime

from PIL import ImageDraw, Image, ImageOps
from PIL.Image import Image as ImageType

from src.image_processor import add_date_to_img, add_weather_to_img, add_tasks_to_img, add_logs_to_img, \
    add_stats_to_img, add_journal_qr_to_img, add_thoughts_to_img
from src.data_processor import DataProcessor

data_processor = DataProcessor()


def generate_tasks_page(page_date: datetime) -> ImageType:
    """Generate tasks page.

    Args:
        page_date: Date to add to page.

    Returns:
        Image object with tasks page.
    """
    logging.info(f"Generating tasks page for {page_date}")

    tasks_page_base = Image.open("designs/bitacora_diaria_base_front_task.png")
    raw_tasks_page = ImageDraw.Draw(tasks_page_base)

    tasks_page_with_date = add_date_to_img(raw_tasks_page, page_date)
    tasks_page_with_weather = add_weather_to_img(tasks_page_with_date, page_date)

    task_titles = data_processor.get_day_active_task_titles(page_date.strftime("%Y-%m-%d"))
    add_tasks_to_img(tasks_page_with_weather, task_titles)

    return tasks_page_base


def generate_logs_page(page_date: datetime) -> ImageType:
    """Generate a logs page as an image for a given date.

    This function takes a date as an argument and generates a logs page as an image. The logs page includes the logs
    for the given date, the stats for the day, and a QR code for the journal of the day.

    Args:
        page_date: The date for which the logs page is to be generated. The date should be in the format
        "YYYY-MM-DD".

    Returns:
        A PIL Image object representing the generated logs page.
    """
    logging.info(f"Generating logs page for {page_date}")

    logs_page_base = Image.open("designs/bitacora_diaria_base_front_logs.png")
    raw_logs_page = ImageDraw.Draw(logs_page_base)

    day_logs = data_processor.get_day_logs(page_date.strftime("%Y-%m-%d"))
    logs_page_with_logs = add_logs_to_img(raw_logs_page, day_logs)

    day_stats = data_processor.get_day_stats(page_date)
    add_stats_to_img(logs_page_with_logs, day_stats)

    day_journal_url = data_processor.get_day_journal_url(page_date)
    add_journal_qr_to_img(logs_page_base, day_journal_url)

    return logs_page_base


def generate_thoughts_page() -> ImageType:
    thoughts_page_base = Image.open("designs/bitacora_diaria_base_back.png")
    raw_thoughts_page = ImageDraw.Draw(thoughts_page_base)

    with open("thoughts.txt") as f:
        raw_thoughts = f.read()

    thoughts = "\n".join([textwrap.fill(line, width=58) for line in raw_thoughts.split("\n")])
    add_thoughts_to_img(raw_thoughts_page, thoughts)

    return thoughts_page_base


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


def save_pages_as_png(page_title: str, page: ImageType):
    """Saves the given page as a PDF file and optionally opens it after saving.

    Args:
        page_title: The title of the page, which will be used as the filename for the saved PDF.
        page: The ImageDraw object representing the page to be saved.
    """
    logging.info(f"Saving {page_title}")
    filename = f"{page_title}.png"

    page.save(filename, "PNG")


def generate_front_page_merged(logs_page: ImageType, logs_date: datetime, files_folder: str) -> list[ImageType]:
    """Generate a front page as an image for a given date.

    This function takes a date as an argument and generates a front page as an image. The front page includes the
    tasks for the given date, the logs for the given date, the stats for the day, and a QR code for the journal of the
    day.

    Args:
        logs_page: The logs page to merge with the tasks page.
        logs_date: The date for which the logs page is to be generated. The date should be in the format
        "YYYY-MM-DD".
        files_folder: The folder where the pages to merge are retrieved from

    Returns:
        A PIL Image object representing the generated front page.
    """
    logging.info(f"Generating front page for {logs_date}")

    if os.path.exists(files_folder):
        old_task_page = Image.open(f"{files_folder}{logs_date.strftime('%d-%b-%Y').lower()}-old-task-page.png")
        old_thoughts_page = Image.open(f"{files_folder}{logs_date.strftime('%d-%b-%Y').lower()}-old-thoughts-page.png")
        old_task_page.paste(logs_page, (0, 0), mask=ImageOps.invert(logs_page.copy().convert('L')))

        return [old_task_page, old_thoughts_page]
    return []
