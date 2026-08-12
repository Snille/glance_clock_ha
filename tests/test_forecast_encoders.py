"""Rain and daylight packed for the clock's forecast face.

The face draws 24 signed little-endian 16-bit values. Both encoders have to
produce exactly 24 whatever they are handed, because a short list is not
rejected by the clock -- it is drawn as a graph with the end missing.
"""

import datetime
import importlib.util
import struct
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "_glance_encoders",
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "glance_clock"
    / "forecast_encoders.py",
)
_enc = importlib.util.module_from_spec(_SPEC)
sys.modules["_glance_encoders"] = _enc
_SPEC.loader.exec_module(_enc)

UTC = datetime.timezone.utc


def _unpack(encoded: bytes) -> list[int]:
    return [v[0] for v in struct.iter_unpack("<h", encoded)]


# --------------------------------------------------------------- rain


def test_rain_always_produces_twenty_four_values():
    for length in (0, 1, 12, 24, 48):
        values, encoded, _ = _enc.encode_rain_values(
            [{"precipitation": 0.5}] * length
        )
        assert len(values) == 24
        assert len(encoded) == 48


def test_rain_is_carried_in_tenths_of_a_millimetre():
    values, _, _ = _enc.encode_rain_values([{"precipitation": 1.3}])
    assert values[0] == 13


def test_the_scale_caps_the_drawing_not_the_data():
    """Heavier rain is still drawn, just not taller than the scale."""
    values, _, max_units = _enc.encode_rain_values(
        [{"precipitation": 40.0}], max_mm_per_hour=2.0
    )
    assert max_units == 20
    assert values[0] == 20


def test_a_missing_or_unusable_figure_is_a_dry_hour():
    values, _, _ = _enc.encode_rain_values(
        [{}, {"precipitation": None}, {"precipitation": "wet"}]
    )
    assert values[:3] == [0, 0, 0]


def test_negative_precipitation_does_not_become_a_negative_bar():
    values, _, _ = _enc.encode_rain_values([{"precipitation": -5.0}])
    assert values[0] == 0


def test_rain_encodes_as_little_endian_shorts():
    _, encoded, _ = _enc.encode_rain_values([{"precipitation": 1.0}])
    assert _unpack(encoded)[0] == 10
    assert encoded[:2] == b"\x0a\x00"


def test_the_scale_never_collapses_to_zero():
    """A zero scale would divide the graph by nothing."""
    _, _, max_units = _enc.encode_rain_values([], max_mm_per_hour=0.0)
    assert max_units >= 1


# ----------------------------------------------------------- daylight


def _sun(day: datetime.date, rise: int, set_: int):
    return (
        datetime.datetime(day.year, day.month, day.day, rise, tzinfo=UTC),
        datetime.datetime(day.year, day.month, day.day, set_, tzinfo=UTC),
    )


def test_daylight_marks_the_hours_between_sunrise_and_sunset():
    start = datetime.datetime(2026, 8, 12, 0, tzinfo=UTC)
    events = {
        (start + datetime.timedelta(days=d)).date(): _sun(
            (start + datetime.timedelta(days=d)).date(), 6, 20
        )
        for d in range(2)
    }
    values, encoded = _enc.encode_daylight_values(start, events)

    assert len(values) == 24
    assert len(encoded) == 48
    # Midpoints: hour 5 is 05:30 (dark), hour 6 is 06:30 (lit).
    assert values[5] == 0
    assert values[6] == _enc.DAYLIGHT_MAX
    assert values[19] == _enc.DAYLIGHT_MAX
    assert values[20] == 0


def test_daylight_crosses_midnight_using_the_next_day():
    """Started in the evening, most of the window is tomorrow."""
    start = datetime.datetime(2026, 8, 12, 18, tzinfo=UTC)
    events = {
        (start + datetime.timedelta(days=d)).date(): _sun(
            (start + datetime.timedelta(days=d)).date(), 6, 20
        )
        for d in range(3)
    }
    values, _ = _enc.encode_daylight_values(start, events)
    assert values[0] == _enc.DAYLIGHT_MAX      # 18:30 today
    assert values[8] == 0                      # 02:30 tomorrow
    assert values[13] == _enc.DAYLIGHT_MAX     # 07:30 tomorrow


def test_a_day_with_no_sun_events_is_dark():
    """The known limit: polar summer reads as night."""
    start = datetime.datetime(2026, 8, 12, 0, tzinfo=UTC)
    values, _ = _enc.encode_daylight_values(start, {})
    assert set(values) == {0}


def test_a_naive_start_is_refused():
    with pytest.raises(ValueError):
        _enc.encode_daylight_values(datetime.datetime(2026, 8, 12, 0), {})


def test_the_templates_are_the_captured_byte_sequences():
    assert _enc.RAIN_TEMPLATE == bytes([0xC2, 149]) + b" RAIN"
    assert _enc.DAYLIGHT_TEMPLATE == bytes([0xC2, 133]) + b" DAY"
