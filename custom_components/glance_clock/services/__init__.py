"""Service management for Glance Clock integration."""
import logging
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.config_entries import ConfigEntry

from ..const import DOMAIN
from .display_settings import handle_update_display_settings, handle_read_current_settings
from .refresh import handle_refresh_entities
from .notice import handle_send_notice
from .forecast import handle_send_forecast
from .timer import handle_send_timer
from .dnd_schedule import handle_set_dnd_schedule, handle_read_dnd_schedule
from .leds import (handle_set_leds, handle_clear_leds, handle_set_animation,
                   handle_set_scene)
from .raw import handle_send_command
from .read_raw import handle_read_characteristic
from .commands import NAMED_COMMANDS, handle_named_command
from .other_forecasts import (handle_send_rain_forecast,
                              handle_send_daylight_forecast)

_LOGGER = logging.getLogger(__name__)


async def async_register_services(hass: HomeAssistant, entry: ConfigEntry):
    """Register all services for the integration."""

    async def _handle_update_display_settings(call: ServiceCall):
        await handle_update_display_settings(hass, entry, call)

    async def _handle_read_current_settings(call: ServiceCall):
        await handle_read_current_settings(hass, entry, call)

    async def _handle_refresh_entities(call: ServiceCall):
        await handle_refresh_entities(hass, entry, call)

    async def _handle_send_notice(call: ServiceCall):
        await handle_send_notice(hass, entry, call)

    async def _handle_send_forecast(call: ServiceCall):
        await handle_send_forecast(hass, entry, call)

    async def _handle_send_timer(call: ServiceCall):
        await handle_send_timer(hass, entry, call)

    async def _handle_set_dnd_schedule(call: ServiceCall):
        await handle_set_dnd_schedule(hass, entry, call)

    async def _handle_read_dnd_schedule(call: ServiceCall):
        await handle_read_dnd_schedule(hass, entry, call)

    async def _handle_set_leds(call: ServiceCall):
        await handle_set_leds(hass, entry, call)

    async def _handle_clear_leds(call: ServiceCall):
        await handle_clear_leds(hass, entry, call)

    async def _handle_set_animation(call: ServiceCall):
        await handle_set_animation(hass, entry, call)

    async def _handle_set_scene(call: ServiceCall):
        await handle_set_scene(hass, entry, call)

    async def _handle_send_command(call: ServiceCall):
        await handle_send_command(hass, entry, call)

    async def _handle_read_characteristic(call: ServiceCall) -> dict:
        return await handle_read_characteristic(hass, entry, call)

    async def _handle_named_command(call: ServiceCall):
        await handle_named_command(hass, entry, call)

    async def _handle_send_rain_forecast(call: ServiceCall):
        await handle_send_rain_forecast(hass, entry, call)

    async def _handle_send_daylight_forecast(call: ServiceCall):
        await handle_send_daylight_forecast(hass, entry, call)

    # Register services
    hass.services.async_register(
        DOMAIN, "update_display_settings", _handle_update_display_settings
    )
    hass.services.async_register(
        DOMAIN, "read_current_settings", _handle_read_current_settings
    )
    hass.services.async_register(
        DOMAIN, "refresh_entities", _handle_refresh_entities
    )
    hass.services.async_register(
        DOMAIN, "send_notice", _handle_send_notice
    )
    hass.services.async_register(
        DOMAIN, "send_forecast", _handle_send_forecast
    )
    hass.services.async_register(
        DOMAIN, "send_timer", _handle_send_timer
    )
    hass.services.async_register(
        DOMAIN, "set_dnd_schedule", _handle_set_dnd_schedule
    )
    hass.services.async_register(
        DOMAIN, "read_dnd_schedule", _handle_read_dnd_schedule
    )
    hass.services.async_register(
        DOMAIN, "set_leds", _handle_set_leds
    )
    hass.services.async_register(
        DOMAIN, "clear_leds", _handle_clear_leds
    )
    hass.services.async_register(
        DOMAIN, "set_animation", _handle_set_animation
    )
    hass.services.async_register(
        DOMAIN, "set_scene", _handle_set_scene
    )
    hass.services.async_register(
        DOMAIN, "send_command", _handle_send_command
    )
    hass.services.async_register(
        DOMAIN, "read_characteristic", _handle_read_characteristic,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN, "send_rain_forecast", _handle_send_rain_forecast
    )
    hass.services.async_register(
        DOMAIN, "send_daylight_forecast", _handle_send_daylight_forecast
    )

    # Each of these carries no arguments, so one handler reads its own name.
    for name in NAMED_COMMANDS:
        hass.services.async_register(DOMAIN, name, _handle_named_command)

    _LOGGER.info("All Glance Clock services registered")


async def async_unregister_services(hass: HomeAssistant):
    """Unregister all services for the integration."""
    # Only unregister if this is the last config entry
    if len(hass.data.get(DOMAIN, {})) <= 1:
        hass.services.async_remove(DOMAIN, "update_display_settings")
        hass.services.async_remove(DOMAIN, "read_current_settings")
        hass.services.async_remove(DOMAIN, "refresh_entities")
        hass.services.async_remove(DOMAIN, "send_notice")
        hass.services.async_remove(DOMAIN, "send_forecast")
        hass.services.async_remove(DOMAIN, "send_timer")
        hass.services.async_remove(DOMAIN, "set_dnd_schedule")
        hass.services.async_remove(DOMAIN, "read_dnd_schedule")
        hass.services.async_remove(DOMAIN, "set_leds")
        hass.services.async_remove(DOMAIN, "clear_leds")
        hass.services.async_remove(DOMAIN, "set_animation")
        hass.services.async_remove(DOMAIN, "set_scene")
        hass.services.async_remove(DOMAIN, "send_command")
        hass.services.async_remove(DOMAIN, "read_characteristic")
        hass.services.async_remove(DOMAIN, "send_rain_forecast")
        hass.services.async_remove(DOMAIN, "send_daylight_forecast")
        for name in NAMED_COMMANDS:
            hass.services.async_remove(DOMAIN, name)
        _LOGGER.info("All Glance Clock services unregistered")
