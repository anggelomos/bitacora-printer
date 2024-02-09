import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.page_processor import generate_tasks_page, save_pages_as_pdf, generate_stats_page, generate_thoughts_page, \
    save_pages_as_png, generate_front_page_merged, generate_logs_page

tasks_delta_days = 0
logs_delta_days = -1
old_pages_folder = "old_pages/"

quebec_timezone = ZoneInfo("America/Toronto")
current_date = datetime.now(quebec_timezone)
tasks_date = current_date + timedelta(days=tasks_delta_days)
logs_date = current_date + timedelta(days=logs_delta_days)

tasks_page = generate_tasks_page(tasks_date)
stats_page = generate_stats_page(logs_date)
thoughts_page = generate_thoughts_page()
logs_page = generate_logs_page(tasks_date)

bitacora_front_page_merged = generate_front_page_merged(stats_page, logs_date, old_pages_folder)

save_pages_as_pdf(
    f"bitacora-print-{current_date.strftime('%d-%b-%Y').lower()}",
    [stats_page, thoughts_page, tasks_page, logs_page],
    open_after_save=False)

save_pages_as_pdf(f"bitacora-save-{logs_date.strftime('%d-%b-%Y').lower()}",
                  bitacora_front_page_merged,
                  open_after_save=False)

if not os.path.exists(old_pages_folder):
    os.makedirs(old_pages_folder)
save_pages_as_png(
    f"{old_pages_folder}{current_date.strftime('%d-%b-%Y').lower()}-old-task-page",
    tasks_page)
save_pages_as_png(
    f"{old_pages_folder}{current_date.strftime('%d-%b-%Y').lower()}-old-thoughts-page",
    thoughts_page)
