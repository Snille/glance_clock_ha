"""The command frames that got a name of their own.

Two of these numbers are disputed. mrmstn/glance_clock_ha calls 30 and 31
`previous_scene` and `next_scene`; this integration calls them stop and start
scene playback, because 31 is what every scene write already sends and the scene
that appears is the one just written, not the one after it.

That disagreement is the reason these are tested at all. A frame built here goes
straight out over BLE, and a wrong number is a command the clock happily obeys.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "glance_clock"


def _load_commands():
    """Load services/commands.py without dragging in Home Assistant."""
    package = types.ModuleType("_glancec")
    package.__path__ = [str(COMPONENT)]
    sys.modules["_glancec"] = package

    const = types.ModuleType("_glancec.const")
    const.DOMAIN = "glance_clock"
    sys.modules["_glancec.const"] = const

    services = types.ModuleType("_glancec.services")
    services.__path__ = [str(COMPONENT / "services")]
    sys.modules["_glancec.services"] = services

    for name, attrs in (
        ("homeassistant", {}),
        ("homeassistant.core", {"HomeAssistant": object, "ServiceCall": object}),
        ("homeassistant.config_entries", {"ConfigEntry": object}),
    ):
        module = sys.modules.get(name) or types.ModuleType(name)
        if name == "homeassistant":
            module.__path__ = []
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules[name] = module

    spec = importlib.util.spec_from_file_location(
        "_glancec.services.commands", COMPONENT / "services" / "commands.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["_glancec.services.commands"] = module
    spec.loader.exec_module(module)
    return module


commands = _load_commands()


def test_every_named_command_builds_a_four_byte_envelope():
    for name in commands.NAMED_COMMANDS:
        frame = commands.build_command(name)
        assert len(frame) == 4
        assert frame[1:] == b"\x00\x00\x00"


@pytest.mark.parametrize(
    ("name", "number"),
    [
        ("stop_timer", 10),
        ("stop_alarm", 20),
        ("stop_scenes", 30),
        ("next_scene", 31),
    ],
)
def test_the_numbers_are_the_ones_observed(name, number):
    assert commands.build_command(name)[0] == number


def test_next_scene_is_the_frame_scene_writes_already_send():
    """notify.py sends bytes([31, 0, 0, 0]) after every scene write.

    If that stops matching, one of the two is wrong and scenes will either
    reappear late or the wrong command will go out under this name.
    """
    source = (COMPONENT / "notify.py").read_text(encoding="utf-8")
    assert "bytes([31, 0, 0, 0])" in source
    assert commands.build_command("next_scene") == bytes([31, 0, 0, 0])


def test_next_scene_sends_31_and_the_old_name_is_gone():
    """31 was measured stepping to the next scene, not starting playback.

    The old `start_scenes` was removed rather than aliased: a name describing
    behaviour the command does not have is what made this take two attempts to
    work out in the first place.
    """
    assert commands.build_command("next_scene") == bytes([31, 0, 0, 0])
    assert "start_scenes" not in commands.NAMED_COMMANDS


def test_an_unknown_name_is_refused_with_the_alternatives():
    with pytest.raises(ValueError) as err:
        commands.build_command("rewind_scene")
    message = str(err.value)
    assert "rewind_scene" in message
    for name in commands.NAMED_COMMANDS:
        assert name in message


def test_no_named_command_is_one_of_the_blocked_ones():
    """42 and 50 unpair the clock and wipe user data. Nothing here may be either."""
    assert not {c for c in commands.NAMED_COMMANDS.values()} & {42, 50}
