import asyncio
from datetime import datetime
import logging
from typing import List

import python_weather
from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw as ImageDrawType
from PIL.Image import Image as ImageType
from aiohttp import ClientConnectorError, ServerDisconnectedError
from nothion import PersonalStats
from python_weather import Kind
import qrcode

from src.data.active_task_model import ActiveTaskModel, ActiveTaskColumns

font_path = "fonts/RobotoMono-Regular.ttf"
bold_font_path = "fonts/RobotoMono-Bold.ttf"


def add_date_to_tasks_img(base_image: ImageDrawType, date: datetime) -> ImageDrawType:
    """Add date to base image.

    Args:
        base_image: Base image to draw on.
        date: Date to add to base image in format dd-mmm.

    Returns:
        Base image with date added.
    """
    logging.info(f"Adding date {date} to tasks image")
    day = date.strftime("%A").capitalize()[0:3]
    day_number = date.timetuple().tm_yday
    formatted_date = date.strftime("%d-%b")

    base_image.text((368, 70), day, font=ImageFont.truetype(font_path, size=195), fill="black")
    base_image.text((395, 270), f"Day {day_number}", font=ImageFont.truetype(font_path, size=68), fill="black")
    base_image.text((395, 340), formatted_date, font=ImageFont.truetype(font_path, size=68), fill="black")
    return base_image


def _does_task_have_specific_time(task_date: str) -> bool:
    return task_date != "12:00am"


def _group_tasks_by_column(tasks: list[ActiveTaskModel]) -> dict[str, list[ActiveTaskModel]]:
    """Group tasks by column.
    
    Args:
        tasks: List of tasks to group by column.

    Returns:
        Dictionary with tasks grouped by column.
    """
    return {column: [task for task in tasks if task.column == column]
            for column in ActiveTaskColumns.get_column_ids()}


def _add_tasks_group_to_img(base_image: ImageDrawType, tasks: list[ActiveTaskModel], current_height: int) \
        -> tuple[ImageDrawType, int]:
    """Add tasks group to base image.

    Args:
        base_image: Base image to draw on.
        tasks: List of tasks to add to base image.
        current_height: Current height of the image.

    Returns:
        Tuple with current height and base image with tasks added.
    """
    task_height_padding = 118.5
    base_left_width = 2630
    base_task_font_size = 68
    task_font = ImageFont.truetype(font_path, size=base_task_font_size)

    for task in tasks:
        text_width = base_image.textlength(task.title, font=task_font)
        base_image.text((base_left_width - text_width, current_height), task.title, font=task_font, fill="black")
        current_height += task_height_padding

    return base_image, current_height


def _add_divider_to_img(base_image: ImageDrawType, current_height: int) -> tuple[ImageDrawType, int]:
    left_width = 2630
    divider_height = 15

    current_height += divider_height
    base_image.line((left_width - 2300, current_height, left_width, current_height), fill="black", width=5)
    base_image.line((left_width - 1500, current_height, left_width, current_height), fill="black", width=8)
    base_image.line((left_width - 1000, current_height, left_width, current_height), fill="black", width=12)
    current_height += (divider_height * 2)

    return base_image, current_height


def add_tasks_to_img(base_image: ImageDrawType, tasks: list[ActiveTaskModel]) -> ImageDrawType:
    """Add tasks to base image.

    Args:
        base_image: Base image to draw on.
        tasks: List of tasks to add to base image.

    Returns:
        Base image with tasks added.
    """
    logging.info("Adding tasks to image")
    work_tasks_height = 620
    personal_tasks_height = 2105

    grouped_tasks = _group_tasks_by_column(tasks)

    base_image, work_tasks_height = _add_tasks_group_to_img(base_image,
                                                            grouped_tasks[ActiveTaskColumns.WORK_GREAT.value],
                                                            work_tasks_height)
    base_image, work_tasks_height = _add_divider_to_img(base_image, work_tasks_height)
    base_image, work_tasks_height = _add_tasks_group_to_img(base_image,
                                                            grouped_tasks[ActiveTaskColumns.WORK_AMAZING.value],
                                                            work_tasks_height)

    base_image, personal_tasks_height = _add_tasks_group_to_img(base_image,
                                                                grouped_tasks[ActiveTaskColumns.PERSONAL_GREAT.value],
                                                                personal_tasks_height)
    base_image, personal_tasks_height = _add_divider_to_img(base_image, personal_tasks_height)
    base_image, personal_tasks_height = _add_tasks_group_to_img(base_image,
                                                                grouped_tasks[ActiveTaskColumns.PERSONAL_AMAZING.value],
                                                                personal_tasks_height)

    return base_image


async def get_weather_forecast(timeout: int):
    """Get weather forecast for Quebec City.

    Returns:
        Generator of weather forecasts.
    """

    async def getweather():
        # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            # fetch a weather forecast from a city
            weather = await client.get("Quebec City")
        return weather.forecasts

    return await asyncio.wait_for(getweather(), timeout=timeout)


def get_weather_icon(forecast_kind: Kind, forecast_time: int) -> ImageType:
    match forecast_kind:
        case Kind.PARTLY_CLOUDY:
            icon_path = "designs/weather_icons/partially-cloudy.png"
        case Kind.CLOUDY | Kind.VERY_CLOUDY:
            icon_path = "designs/weather_icons/cloudy.png"
        case Kind.LIGHT_SHOWERS | Kind.LIGHT_SLEET_SHOWERS | Kind.LIGHT_SLEET | Kind.LIGHT_RAIN:
            icon_path = "designs/weather_icons/rain.png"
        case Kind.THUNDERY_SHOWERS | Kind.HEAVY_RAIN | Kind.THUNDERY_HEAVY_RAIN | Kind.HEAVY_SHOWERS:
            icon_path = "designs/weather_icons/heavy-rain.png"
        case Kind.LIGHT_SNOW | Kind.LIGHT_SNOW_SHOWERS:
            icon_path = "designs/weather_icons/snow.png"
        case Kind.HEAVY_SNOW | Kind.HEAVY_SNOW_SHOWERS | Kind.THUNDERY_SNOW_SHOWERS:
            icon_path = "designs/weather_icons/heavy-snow.png"
        case _:
            icon_path = "designs/weather_icons/sunny.png"
            if forecast_time >= 18:
                icon_path = "designs/weather_icons/night.png"

    return Image.open(icon_path)


def add_weather_to_img(base_image: ImageDrawType, date: datetime) -> ImageDrawType:
    try:
        date_forecast = next((fc for fc in asyncio.run(get_weather_forecast(timeout=10)) if fc.date == date.date()),
                             None)
    except (ClientConnectorError, asyncio.TimeoutError, ServerDisconnectedError):
        logging.warning("Could not connect to weather API")
        date_forecast = None

    if date_forecast is None:
        return base_image

    forcast_padding = 0
    for hour_forecast in date_forecast.hourly:
        forecast_time = hour_forecast.time.hour
        if forecast_time not in [6, 9, 12, 15, 18, 21]:
            continue

        temperature_font = ImageFont.truetype(font_path, size=60)
        forecast_temperature = str(hour_forecast.temperature) + "°"
        base_image.text((1959 + forcast_padding, 349), forecast_temperature,
                        font=temperature_font, fill="black", anchor="mm")

        forecast_feels_like = str(hour_forecast.feels_like) + "°"
        base_image.text((1959 + forcast_padding, 424), forecast_feels_like,
                        font=temperature_font, fill="black", anchor="mm")

        forecast_kind = hour_forecast.kind
        forecast_kind_icon = get_weather_icon(forecast_kind, forecast_time)
        base_image._image.paste(forecast_kind_icon, (1912 + forcast_padding, 199), forecast_kind_icon)

        forcast_padding += 138

    return base_image


def add_logs_to_img(base_image: ImageDrawType, logs: List[str]) -> ImageDrawType:
    logging.info("Adding logs to image")
    current_height = 1770
    task_padding = 90

    for log in logs:
        task_font_path = font_path
        if log.startswith(" щ"):
            task_font_path = bold_font_path

        task_font = ImageFont.truetype(task_font_path, size=60)
        base_image.text((350, current_height), log, font=task_font, fill="black")
        current_height += task_padding

    return base_image


def add_date_to_logs_img(base_image: ImageDrawType, date: datetime) -> ImageDrawType:
    """Add date to base image.

    Args:
        base_image: Base image to draw on.
        date: Date to add to base image in format dd-mmm.

    Returns:
        Base image with date added.
    """
    logging.info(f"Adding date {date} to logs image")
    formatted_date = date.strftime("%d-%b-%Y")
    base_image.text((2320, 120), formatted_date, font=ImageFont.truetype(font_path, size=58), fill="black")
    return base_image


def add_stats_to_img(base_image: ImageDrawType, stats: PersonalStats) -> ImageDrawType:
    print_stats: list[tuple[float, tuple[int, int]]] = [(stats.work_time, (770, 140)),
                                                        (stats.focus_time, (1040, 140)),
                                                        (stats.sleep_time, (770, 268)),
                                                        (stats.leisure_time, (1040, 268))]

    for stat, position in print_stats:
        if stat > 0:
            base_image.text(position, str(round(stat, 1)), font=ImageFont.truetype(font_path, size=59), fill="black")

    return base_image


def _generate_qr_code(url: str, size_in_cm: float, dpi: int) -> ImageType:
    cm_to_inches = 0.393701
    size_in_pixels = int(size_in_cm * cm_to_inches * dpi)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img.resize((size_in_pixels, size_in_pixels))


def add_journal_qr_to_img(base_image: ImageType, journal_url: str) -> ImageType:
    qr_code_img = _generate_qr_code(journal_url, 1, 700)
    base_image.paste(qr_code_img, (1500, 140))

    return base_image


def add_journal_summary_to_img(base_image: ImageDrawType, thoughts: str) -> ImageDrawType:
    logging.info("Adding thoughts to image")
    thoughts = "\n".join(thoughts.split("\n")[:21])
    base_image.text((135, 2156), thoughts, font=ImageFont.truetype(font_path, size=59), spacing=8, fill="black")

    return base_image
