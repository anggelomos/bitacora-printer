#!C:\Users\angel\OneDrive\Documentos\projects\daily_card\env-daily-card\Scripts\python.exe
import locale
import logging
import os
import sys
from datetime import datetime, timedelta

from PIL import Image, ImageDraw

from src.image_processor import add_date_to_img, add_tasks_to_img, add_weather_to_img
from src.task_processor import TaskProcessor

delta_days = 0

logging.info(f"Generating daily card for {delta_days} days ago")
task_processor = TaskProcessor(os.getenv('TT_user'), os.getenv('TT_pass'))
daily_card_base = Image.open("designs/bitacora_diaria_base.png")
daily_card = ImageDraw.Draw(daily_card_base)

locale.setlocale(locale.LC_TIME, "fr_CA")
card_date = datetime.now() + timedelta(days=delta_days)
daily_card_with_date = add_date_to_img(daily_card, card_date)
daily_card_with_weather = add_weather_to_img(daily_card_with_date, card_date)

task_titles = task_processor.get_day_active_task_titles(card_date.strftime("%Y-%m-%d"))
daily_card_with_tasks = add_tasks_to_img(daily_card_with_weather, task_titles)

logging.info("Saving bitacora diaria")
daily_card_filename = f"bitacora-diaria-{card_date.strftime('%d-%b-%Y').lower()}.pdf"
daily_card_base.save(daily_card_filename, "PDF", resolution=700)
os.startfile(daily_card_filename)
