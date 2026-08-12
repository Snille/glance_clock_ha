"""Rain and daylight, drawn with the clock's own forecast face.

`send_forecast` draws temperature. The frame it uses does not care what the
numbers mean -- it takes 24 of them, a range, two colours, and a label -- so the
same face draws rain and daylight. Both live in scene slot 2 by default, leaving
slot 1 to the temperature forecast so the two can stand together.

Adapted from mrmstn/glance_clock_ha (MIT).
"""

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.util import dt as dt_util

from ..const import DOMAIN
from ..forecast_encoders import (
    DAYLIGHT_MAX,
    DAYLIGHT_TEMPLATE,
    RAIN_TEMPLATE,
    encode_daylight_values,
    encode_rain_values,
)
from ..utils.color_utils import parse_color_input
from .forecast import _calculate_forecast_timestamp

_LOGGER = logging.getLogger(__name__)

#: Where these two go unless told otherwise. Slot 1 belongs to the temperature
#: forecast; putting rain there would silently replace it.
DEFAULT_SLOT = 2

#: The forecast face's graphics-only mode, which is what these two want -- the
#: label carries the meaning, and there is no single number to show.
GRAPHICS_ONLY = 8


def _notify_service(hass: HomeAssistant, entry: ConfigEntry):
    """Return the object that knows how to send a forecast frame."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    service = hass.data.get(DOMAIN + "_notify", {}).get(entry.entry_id)
    if not service:
        raise ServiceValidationError("the clock's notification service is not set up")

    connection_manager = entry_data.get("connection_manager")
    if connection_manager and not hasattr(service, "_connection_manager"):
        service._connection_manager = connection_manager
    return service


async def handle_send_rain_forecast(
    hass: HomeAssistant, entry: ConfigEntry, call: ServiceCall
) -> None:
    """Draw the next 24 hours of precipitation."""
    service = _notify_service(hass, entry)

    weather_entity = call.data.get("weather_entity")
    if not weather_entity or not hass.states.get(weather_entity):
        raise ServiceValidationError(
            f"weather_entity '{weather_entity}' is not a known entity"
        )

    response = await hass.services.async_call(
        "weather",
        "get_forecasts",
        {"entity_id": weather_entity, "type": "hourly"},
        blocking=True,
        return_response=True,
    )
    entity_forecast = response.get(weather_entity, {}) if isinstance(response, dict) else {}
    forecast = entity_forecast.get("forecast", [])
    if not forecast:
        raise ServiceValidationError(
            f"{weather_entity} returned no hourly forecast; rain needs an hourly one"
        )

    values, encoded, max_units = encode_rain_values(
        forecast, float(call.data.get("max_value", 2.0))
    )

    _LOGGER.info(
        "Rain forecast: peak %.1f mm/h over 24 hours", max(values) / 10
    )

    sent = await service.async_send_forecast(
        max_temp=max_units,
        min_temp=0,
        max_color=parse_color_input(call.data.get("max_color"), 0x00BFFF),
        min_color=parse_color_input(call.data.get("min_color"), 0x000010),
        values=encoded,
        start_timestamp=_calculate_forecast_timestamp(),
        template=RAIN_TEMPLATE,
        scene_slot=int(call.data.get("slot", DEFAULT_SLOT)),
        display_mode=GRAPHICS_ONLY,
    )
    if not sent:
        _LOGGER.error("Failed to send the rain forecast")


async def handle_send_daylight_forecast(
    hass: HomeAssistant, entry: ConfigEntry, call: ServiceCall
) -> None:
    """Draw which of the next 24 hours are daylight.

    This one needs no weather entity. Home Assistant already knows where the sun
    is, and the answer is arithmetic rather than a forecast.
    """
    service = _notify_service(hass, entry)

    start = dt_util.now().replace(minute=0, second=0, microsecond=0)

    # Two days of sun events, because 24 hours from now crosses midnight for all
    # but one hour of the day.
    sun_events: dict = {}
    for day in range(3):
        date = (start + datetime.timedelta(days=day)).date()
        sun_events[date] = (
            get_astral_event_date(hass, "sunrise", date),
            get_astral_event_date(hass, "sunset", date),
        )

    values, encoded = encode_daylight_values(start, sun_events)
    _LOGGER.info("Daylight forecast: %d of the next 24 hours are lit",
                 sum(1 for v in values if v))

    sent = await service.async_send_forecast(
        max_temp=DAYLIGHT_MAX,
        min_temp=0,
        max_color=parse_color_input(call.data.get("max_color"), 0xFFD700),
        min_color=parse_color_input(call.data.get("min_color"), 0x000010),
        values=encoded,
        start_timestamp=_calculate_forecast_timestamp(),
        template=DAYLIGHT_TEMPLATE,
        scene_slot=int(call.data.get("slot", DEFAULT_SLOT)),
        display_mode=GRAPHICS_ONLY,
    )
    if not sent:
        _LOGGER.error("Failed to send the daylight forecast")
