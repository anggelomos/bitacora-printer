from src.cli_processor import get_pages_dates
from src.page_processor import PageProcessor

day_date, week_start_date = get_pages_dates()
pp = PageProcessor()

daily_tasks_page = pp.generate_daily_tasks_page(day_date)
pp.save_pages_as_pdf(f"bitacora-day-print-{day_date.strftime('%d-%b-%Y').lower()}",
                     [daily_tasks_page],
                     open_after_save=True)

if week_start_date is not None:
    weekly_task_page = pp.generate_weekly_tasks_page(week_start_date)
    pp.save_pages_as_pdf(f"bitacora-week-print-{week_start_date.strftime('%d-%b-%Y').lower()}",
                         [weekly_task_page],
                         open_after_save=True)
