import asyncio
import datetime
import logging
from typing import List

import python_weather
from PIL import Image, ImageDraw, ImageFont
from python_weather import Kind

font_path = "fonts/RobotoMono-Regular.ttf"


def add_date_to_img(base_image: ImageDraw, date: datetime) -> ImageDraw:
    """Add date to base image.

    Args:
        base_image: Base image to draw on.
        date: Date to add to base image in format dd-mmm.

    Returns:
        Base image with date added.
    """
    logging.info(f"Adding date {date} to image")
    day = date.strftime("%A").capitalize()[0:3]
    day_number = date.timetuple().tm_yday
    formatted_date = date.strftime("%d-%b")[:-1]

    base_image.text((350, 70), day, font=ImageFont.truetype(font_path, size=200), fill="black")
    base_image.text((363, 300), f"Day {day_number}", font=ImageFont.truetype(font_path, size=80), fill="black")
    base_image.text((363, 395), formatted_date, font=ImageFont.truetype(font_path, size=80), fill="black")
    return base_image


def add_tasks_to_img(base_image: ImageDraw, tasks: List[str]) -> ImageDraw:
    """Add tasks to base image.

    Args:
        base_image: Base image to draw on.
        tasks: List of tasks to add to base image.

    Returns:
        Base image with tasks added.
    """
    logging.info(f"Adding tasks {tasks} to image")
    task_font = ImageFont.truetype(font_path, size=80)
    current_height = 627.5
    task_padding = 115.5
    for task in tasks:
        base_image.text((460, current_height), task, font=task_font, fill="black")
        current_height += task_padding
    return base_image


def get_weather_forecast():
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

    return asyncio.run(getweather())


def get_weather_icon(forecast_kind: Kind, forecast_time: int) -> ImageDraw:

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


def add_weather_to_img(base_image: ImageDraw, date: datetime) -> ImageDraw:
    date_forecast = next((fc for fc in get_weather_forecast() if fc.date == date.date()), None)

    if date_forecast is None:
        return base_image

    forcast_padding = 0
    for hour_forecast in date_forecast.hourly:
        forecast_time = hour_forecast.time.hour
        if forecast_time not in [6, 9, 12, 15, 18, 21]:
            continue

        temperature_font = ImageFont.truetype(font_path, size=60)
        forecast_temperature = str(hour_forecast.temperature) + "°"
        base_image.text((1959+forcast_padding, 349), forecast_temperature,
                        font=temperature_font, fill="black", anchor="mm")

        forecast_feels_like = str(hour_forecast.feels_like) + "°"
        base_image.text((1959+forcast_padding, 424), forecast_feels_like,
                        font=temperature_font, fill="black", anchor="mm")

        forecast_kind = hour_forecast.kind
        forecast_kind_icon = get_weather_icon(forecast_kind, forecast_time)
        base_image._image.paste(forecast_kind_icon, (1912+forcast_padding, 199), forecast_kind_icon)

        forcast_padding += 138

    return base_image
