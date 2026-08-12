"""Decode the clock's state characteristic.

The clock pushes two bytes on `scene_state` whenever what it says changes. We
had read them as two separate bytes -- a flag byte and a constant -- because
every sample captured on hardware ended in 0x22 and nothing suggested otherwise.

They are one little-endian 16-bit word. The flag table below comes from
mrmstn/glance_clock_ha (MIT), which took it from the official Android
application's own parser, and it decodes our captured samples exactly:

    0x2204   scenes_enabled, cable_connected, no_data
    0x2214   the above, plus do_not_disturb
    0x220c   the above, plus muted

So the "constant" 0x22 was never constant. It is `cable_connected | no_data`,
and it read as a constant only because the clock it was captured from spends its
life plugged in. Unplug it and the high byte becomes 0x20.

The bits we had already found the hard way survive unchanged -- 0x0010 is Do Not
Disturb and 0x0008 is mute -- and the bit we had noted as "set in every sample"
turns out to be `scenes_enabled`. The rest of the word is free: whether the
clock is charging, whether the hands failed to home, and which power-saving band
it is in were all arriving in every push, unread.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Bit masks the official application interprets, by the name it uses.
STATE_FLAGS = {
    "scenes_enabled": 0x0004,
    "muted": 0x0008,
    "do_not_disturb": 0x0010,
    "ancs_enabled": 0x0020,
    "homing_failure": 0x0040,
    "homing_in_progress": 0x0080,
    "time_adjustment_in_progress": 0x0100,
    "cable_connected": 0x0200,
    "homing_confirmation_wait": 0x0400,
    "motor_failure": 0x0800,
    "charging": 0x1000,
    "no_data": 0x2000,
}

#: Battery percentage band for each of the four power-saving modes, as
#: (high, low). Mode 3 is the bottom band, where the clock does least.
POWER_SAVING_THRESHOLDS = {
    0: (100, 50),
    1: (50, 25),
    2: (25, 10),
    3: (10, 0),
}

#: Bits 0-1 are the power-saving mode; the flags above cover up to 0x2000.
#: Anything outside this mask is undocumented and reported as-is rather than
#: silently dropped, so a firmware that starts using it is visible.
KNOWN_MASK = 0x3FFF


@dataclass(frozen=True)
class ClockState:
    """One decoded sample of the state characteristic."""

    word: int

    @classmethod
    def from_bytes(cls, data: bytes | bytearray) -> "ClockState":
        """Decode the first two bytes, little-endian.

        A one-byte sample is padded rather than refused: the flags we care about
        all live in the low byte, so a short read still answers the question.
        """
        if not data:
            raise ValueError("state characteristic returned no data")
        return cls(int.from_bytes(bytes(data[:2]).ljust(2, b"\x00"), "little"))

    @property
    def power_saving_mode(self) -> int:
        """Return the power-saving mode, 0 through 3."""
        return self.word & 0x0003

    @property
    def unknown_bits(self) -> int:
        """Return the bits no known flag claims."""
        return self.word & ~KNOWN_MASK & 0xFFFF

    def flag(self, name: str) -> bool:
        """Return one named flag."""
        return bool(self.word & STATE_FLAGS[name])

    def as_attributes(self) -> dict[str, bool | int | str]:
        """Return every flag, for an entity to publish as attributes."""
        high, low = POWER_SAVING_THRESHOLDS[self.power_saving_mode]
        attributes: dict[str, bool | int | str] = {
            "raw": f"0x{self.word:04x}",
            "power_saving_mode": self.power_saving_mode,
            "power_saving_high_threshold": high,
            "power_saving_low_threshold": low,
            "unknown_bits": f"0x{self.unknown_bits:04x}",
        }
        attributes.update(
            {name: bool(self.word & mask) for name, mask in STATE_FLAGS.items()}
        )
        return attributes
