"""Named services for the command frames worth having a name.

`send_command` can already send any of these. These exist because the useful
ones should not require knowing a number, and because a timer the clock is
running had no way to be cancelled at all -- `send_timer` could start one and
nothing could stop it.

A note on 30 and 31, because there is a disagreement on record. This integration
calls them stop and start scene playback, on the strength of what 31 does here:
sending it after writing a scene makes that scene appear at once, which is why
every scene write is followed by one. mrmstn/glance_clock_ha names the same two
numbers `previous_scene` and `next_scene` -- carousel navigation -- and keeps
stop/start as aliases for them.

Both readings cannot be right, and only one of them is tested here. If 31 meant
"advance the carousel", writing a scene to slot 2 and then sending it would
show whatever came next rather than slot 2, and what we filmed is slot 2. So
they are named for what they were watched doing. Whether the firmware also has
carousel navigation, on these numbers or others, is open -- see SCENES.md.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

#: Command frames that cannot lose anything the owner cares about, by service
#: name. Each is sent as a bare command byte with three zero modifiers, which is
#: the envelope every frame observed working on hardware uses.
NAMED_COMMANDS = {
    "stop_timer": 10,
    "stop_alarm": 20,
    "stop_scenes": 30,
    "start_scenes": 31,
}


def build_command(name: str) -> bytes:
    """Build the four-byte envelope for one named command."""
    if name not in NAMED_COMMANDS:
        raise ValueError(
            f"unknown command '{name}'; expected one of {', '.join(sorted(NAMED_COMMANDS))}"
        )
    return bytes([NAMED_COMMANDS[name], 0, 0, 0])


async def send_named_command(
    hass: HomeAssistant, entry: ConfigEntry, name: str
) -> bool:
    """Send one named command, returning whether the clock took it."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    connection_manager = entry_data.get("connection_manager")

    if not connection_manager or not connection_manager.is_connected:
        _LOGGER.error("%s: device not connected", name)
        return False

    frame = build_command(name)
    if await connection_manager.send_command(frame):
        return True

    _LOGGER.error("%s: failed to send %s", name, frame.hex())
    return False


async def handle_named_command(
    hass: HomeAssistant, entry: ConfigEntry, call: ServiceCall
) -> None:
    """Handle a service whose own name says which command to send."""
    await send_named_command(hass, entry, call.service)
