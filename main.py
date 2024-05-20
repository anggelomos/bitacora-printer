import os

from config import OLD_PAGES_FOLDER
from src.cli_processor import get_pages_dates
from src.page_processor import PageProcessor

current_date, old_date = get_pages_dates()
pp = PageProcessor()

empty_page = pp.generate_empty_page()
stats_page = pp.generate_stats_page(old_date)
tasks_page = pp.generate_tasks_page(current_date)
journal_page = pp.generate_journal_page()

day_recap = pp.data_processor.get_day_recap(old_date)
summary_recap = pp.data_processor.generate_recap_summary(day_recap)
recap_page = pp.generate_recap_page(summary_recap)
pp.upload_recap(summary_recap, old_date)
pp.create_day_highlights(day_recap, old_date)

old_bitacora_pages = pp.generate_old_bitacora_pages(stats_page, old_date)

pp.save_pages_as_pdf(f"bitacora-print-{current_date.strftime('%d-%b-%Y').lower()}",
                     [empty_page, recap_page, stats_page, journal_page, tasks_page],
                     open_after_save=True)

pp.save_pages_as_pdf(f"bitacora-save-{old_date.strftime('%d-%b-%Y').lower()}",
                     old_bitacora_pages,
                     open_after_save=False)

if not os.path.exists(OLD_PAGES_FOLDER):
    os.makedirs(OLD_PAGES_FOLDER)

pp.save_pages_as_png(f"{OLD_PAGES_FOLDER}{current_date.strftime('%d-%b-%Y').lower()}-old-task-page", tasks_page)
pp.save_pages_as_png(f"{OLD_PAGES_FOLDER}{current_date.strftime('%d-%b-%Y').lower()}-old-journal-page", recap_page)
