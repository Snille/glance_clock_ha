"""Encoders for the forecast scenes that are not temperature.

The clock's ForecastScene draws 24 hourly values as a graph around the dial. It
was built for temperature, but nothing in it is about temperature: it takes a
list of numbers, a range, two colours to interpolate between, and a template
string for the label. Point it at rain or at daylight and it draws those.

Both encoders here come from mrmstn/glance_clock_ha (MIT). The templates are the
byte sequences that firmware expects for the label, captured from the official
application.
"""

from __future__ import annotations

import datetime
import struct

#: Label template for the rain face. 0xC2 0x95 is the raindrop glyph.
RAIN_TEMPLATE = bytes([0xC2, 149]) + b" RAIN"

#: Label template for the daylight face. 0xC2 0x85 is the sun glyph.
DAYLIGHT_TEMPLATE = bytes([0xC2, 133]) + b" DAY"

#: Precipitation is sent in tenths of a millimetre, so the graph has usable
#: resolution over the drizzle most hours actually deliver.
RAIN_UNITS_PER_MM = 10

#: Daylight is a yes or no, drawn as a full bar or nothing.
DAYLIGHT_MAX = 100


def encode_rain_values(
    forecast: list[dict], max_mm_per_hour: float = 2.0
) -> tuple[list[int], bytes, int]:
    """Encode up to 24 hourly precipitation figures.

    `max_mm_per_hour` is the top of the scale, not a filter: anything heavier is
    drawn at full height. Two millimetres an hour is moderate rain, which keeps
    ordinary drizzle visible instead of flattening it against a scale set by one
    thunderstorm.

    Returns the values, the packed bytes, and the scale maximum the clock needs
    to be told about.
    """
    max_units = max(1, round(float(max_mm_per_hour) * RAIN_UNITS_PER_MM))

    values: list[int] = []
    for hour in forecast[:24]:
        try:
            precipitation = max(0.0, float(hour.get("precipitation", 0.0)))
        except (TypeError, ValueError):
            # A forecast entry without usable precipitation is a dry hour, not a
            # reason to refuse the whole graph.
            precipitation = 0.0
        values.append(min(max_units, round(precipitation * RAIN_UNITS_PER_MM)))

    # A short forecast is padded rather than refused: the clock draws 24 bars
    # whatever happens, and zeroes read as "nothing known" the same as dry.
    values.extend([0] * (24 - len(values)))

    return values, b"".join(struct.pack("<h", v) for v in values), max_units


def encode_daylight_values(
    start: datetime.datetime,
    sun_events: dict[
        datetime.date, tuple[datetime.datetime | None, datetime.datetime | None]
    ],
) -> tuple[list[int], bytes]:
    """Encode whether the middle of each of the next 24 hours is daylight.

    The midpoint rather than the start, so an hour is lit if most of it is. A
    date with no sunrise or sunset -- polar summer or winter -- is dark here,
    which is wrong half the year and is the known limit of this encoding.
    """
    if start.tzinfo is None:
        raise ValueError("the daylight forecast needs a timezone-aware start")

    values: list[int] = []
    for offset in range(24):
        midpoint = start + datetime.timedelta(hours=offset, minutes=30)
        sunrise, sunset = sun_events.get(midpoint.date(), (None, None))
        lit = sunrise is not None and sunset is not None
        if lit:
            lit = (
                sunrise.astimezone(start.tzinfo)
                <= midpoint
                < sunset.astimezone(start.tzinfo)
            )
        values.append(DAYLIGHT_MAX if lit else 0)

    return values, b"".join(struct.pack("<h", v) for v in values)
