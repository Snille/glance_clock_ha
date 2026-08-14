"""Named services for the command frames worth having a name.

`send_command` can already send any of these. These exist because the useful
ones should not require knowing a number, and because a timer the clock is
running had no way to be cancelled at all -- `send_timer` could start one and
nothing could stop it.

A note on 30 and 31, settled against hardware 2026-08-14 after a disagreement
with mrmstn/glance_clock_ha, which called them `previous_scene`/`next_scene`.

**31 advances to the next scene.** Sent three times, four seconds apart, with
three slots filled and nothing else going on, it changed the displayed slot
each time -- off the fifteen-second rotation beat, restarting the dwell timer
from the command. Something that only started playback already running would
have done nothing. So the service is `next_scene` now, with `start_scenes`
kept as an alias.

**30 stops playback.** Each 30 cleared the `scenes_enabled` bit in the state
word, 0x2204 -> 0x2200, and the display went idle. A step to the previous scene
would not touch that bit. The stop does not hold: the clock sets the bit again
by itself within about a second.

Why this stayed open so long: both readings predict the same outcome when only
one slot is filled, because "next scene" with one scene is that same scene --
and the earlier test had one slot. Three slots separate them. That is also why
sending 31 after a scene write still works as a refresh, and why it is left in
place; see `_refresh_scene_playback` in notify.py, and SCENES.md for the quirk
where a manual 31 makes the *next* write wait for the natural tick.
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
    "next_scene": 31,
    #: Alias, kept because automations and Node-RED flows written against
    #: earlier versions call it. Sends 31, exactly as next_scene does.
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
