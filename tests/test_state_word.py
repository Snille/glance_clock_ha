"""The state characteristic is one little-endian word, not a byte and a constant.

The samples below are the ones captured from hardware on 2026-08-12 by moving
the Do Not Disturb window across the current time and toggling mute. They were
originally read as "flag byte, then 0x22". The flag table proves the 0x22 is
`cable_connected | no_data`, so these tests are what stops anyone reintroducing
the constant.
"""

import importlib.util
import sys
from pathlib import Path

# Loaded by path: state.py imports nothing but the standard library, so it needs
# none of the package machinery -- and importing the package would drag in
# Home Assistant.
_SPEC = importlib.util.spec_from_file_location(
    "_glance_state",
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "glance_clock"
    / "state.py",
)
_state = importlib.util.module_from_spec(_SPEC)
# @dataclass looks its own module up in sys.modules; without this it finds None.
sys.modules["_glance_state"] = _state
_SPEC.loader.exec_module(_state)

ClockState = _state.ClockState
STATE_FLAGS = _state.STATE_FLAGS
POWER_SAVING_THRESHOLDS = _state.POWER_SAVING_THRESHOLDS

#: What the clock actually sent, in the order the bytes arrive.
NOTHING_SUPPRESSED = bytes.fromhex("0422")
QUIET_WINDOW_IN_FORCE = bytes.fromhex("1422")
MUTED = bytes.fromhex("0c22")


def _flags_on(sample: bytes) -> set[str]:
    state = ClockState.from_bytes(sample)
    return {name for name in STATE_FLAGS if state.flag(name)}


def test_captured_samples_decode_to_the_documented_flags():
    assert _flags_on(NOTHING_SUPPRESSED) == {
        "scenes_enabled",
        "cable_connected",
        "no_data",
    }
    assert _flags_on(QUIET_WINDOW_IN_FORCE) == {
        "scenes_enabled",
        "cable_connected",
        "no_data",
        "do_not_disturb",
    }
    assert _flags_on(MUTED) == {
        "scenes_enabled",
        "cable_connected",
        "no_data",
        "muted",
    }


def test_the_bits_found_by_hand_are_the_bits_in_the_table():
    """0x10 and 0x08 were derived from hardware before the table was known."""
    assert STATE_FLAGS["do_not_disturb"] == 0x10
    assert STATE_FLAGS["muted"] == 0x08


def test_the_high_byte_is_not_a_constant():
    """0x22 is two flags. Unplug the clock and the sample changes."""
    on_a_cable = ClockState.from_bytes(NOTHING_SUPPRESSED)
    unplugged = ClockState(on_a_cable.word & ~STATE_FLAGS["cable_connected"])
    assert on_a_cable.flag("cable_connected")
    assert not unplugged.flag("cable_connected")
    assert unplugged.word == 0x2004


def test_byte_order_is_little_endian():
    """Read big-endian, DND would land in the high byte and never be seen."""
    assert ClockState.from_bytes(QUIET_WINDOW_IN_FORCE).word == 0x2214


def test_a_short_sample_still_answers_the_question():
    """The flags worth acting on are all in the low byte."""
    assert ClockState.from_bytes(b"\x14").flag("do_not_disturb")


def test_an_empty_sample_is_refused():
    try:
        ClockState.from_bytes(b"")
    except ValueError:
        return
    raise AssertionError("an empty state sample should raise")


def test_power_saving_mode_comes_from_the_low_two_bits():
    for mode in POWER_SAVING_THRESHOLDS:
        assert ClockState(0x2204 | mode).power_saving_mode == mode


def test_undocumented_bits_are_reported_rather_than_dropped():
    """A firmware that starts using bit 15 should be visible, not silently lost."""
    state = ClockState(0x8000 | 0x2204)
    assert state.unknown_bits == 0x8000
    assert state.as_attributes()["unknown_bits"] == "0x8000"


def test_the_state_flags_do_not_collide_with_the_display_bits():
    """scene_state and scene_data are different characteristics.

    Both are decoded in binary_sensor.py, and mixing them up would produce a
    sensor that is subtly wrong rather than obviously broken.
    """
    source = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "glance_clock"
        / "binary_sensor.py"
    ).read_text(encoding="utf-8")
    display: dict = {}
    for line in source.splitlines():
        if line.startswith(("IDLE_BIT", "DIGITAL_CLOCK_BIT")):
            exec(line, display)  # noqa: S102 -- two constant assignments

    for bit in (display["IDLE_BIT"], display["DIGITAL_CLOCK_BIT"]):
        assert not STATE_FLAGS["do_not_disturb"] & bit
        assert not STATE_FLAGS["muted"] & bit


def test_attributes_carry_every_flag():
    attributes = ClockState.from_bytes(MUTED).as_attributes()
    for name in STATE_FLAGS:
        assert name in attributes
    assert attributes["raw"] == "0x220c"
    assert attributes["muted"] is True
