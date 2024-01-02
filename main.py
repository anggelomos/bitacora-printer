import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.page_processor import generate_tasks_page, save_pages_as_pdf, generate_logs_page, generate_thoughts_page, \
    save_pages_as_png, generate_front_page_merged

tasks_delta_days = 0
logs_delta_days = -1
old_pages_folder = "old_pages/"

quebec_timezone = ZoneInfo("America/Toronto")
current_date = datetime.now(quebec_timezone)
tasks_date = current_date + timedelta(days=tasks_delta_days)
logs_date = current_date + timedelta(days=logs_delta_days)

tasks_page = generate_tasks_page(tasks_date)
logs_page = generate_logs_page(logs_date)
thoughts_page = generate_thoughts_page()

bitacora_front_page_merged = generate_front_page_merged(logs_page, logs_date, old_pages_folder)

save_pages_as_pdf(f"bitacora-print-{current_date.strftime('%d-%b-%Y').lower()}",
                  [logs_page, thoughts_page, tasks_page],
                  open_after_save=True)

save_pages_as_pdf(f"bitacora-save-{current_date.strftime('%d-%b-%Y').lower()}",
                  bitacora_front_page_merged,
                  open_after_save=True)

if not os.path.exists(old_pages_folder):
    os.makedirs(old_pages_folder)
save_pages_as_png(f"{old_pages_folder}old-task-page-{current_date.strftime('%d-%b-%Y').lower()}", tasks_page)
save_pages_as_png(f"{old_pages_folder}old-thoughts-page-{current_date.strftime('%d-%b-%Y').lower()}", thoughts_page)
