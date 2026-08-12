"""The clock's own built-in faces, and the byte that names them.

The table is from mrmstn/glance_clock_ha (MIT), which took it from the official
Android application. What makes it worth testing here is that the byte it is
written to is scene_data -- the same byte the Busy binary sensor reads as a
status. Those two readings have to coexist without either one corrupting the
other, and the inactive flag is where they meet.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "_glance_const",
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "glance_clock"
    / "const.py",
)
_const = importlib.util.module_from_spec(_SPEC)
sys.modules["_glance_const"] = _const
_SPEC.loader.exec_module(_const)

FACTORY_SCENES = _const.FACTORY_SCENES
INACTIVE = _const.FACTORY_SCENE_INACTIVE
decode = _const.decode_factory_scene


def test_every_face_decodes_back_to_its_own_name():
    for name, number in FACTORY_SCENES.items():
        assert decode(number) == name


def test_the_inactive_flag_does_not_change_which_face_is_named():
    """Bit 7 says the face is not on screen, not that it is a different face."""
    for name, number in FACTORY_SCENES.items():
        if number == FACTORY_SCENES["repeat_all"]:
            continue
        assert decode(number | INACTIVE) == name


def test_the_inactive_flag_is_the_bit_the_busy_sensor_calls_idle():
    """Same byte, same bit, two names. They must not drift apart."""
    source = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "glance_clock"
        / "binary_sensor.py"
    ).read_text(encoding="utf-8")
    namespace: dict = {}
    for line in source.splitlines():
        if line.startswith("IDLE_BIT"):
            exec(line, namespace)  # noqa: S102 -- one constant assignment
    assert namespace["IDLE_BIT"] == INACTIVE


def test_repeat_all_is_not_masked():
    """255 is a mode, not a face, so the inactive flag must not be stripped."""
    assert decode(255) == "repeat_all"


def test_an_unknown_face_number_is_not_guessed_at():
    unused = max(n for n in FACTORY_SCENES.values() if n != 255) + 1
    assert decode(unused) is None


@pytest.mark.parametrize("byte", [0x00, 0x80])
def test_both_forms_of_the_plain_face_read_as_off(byte):
    """0x00 and 0x80 were both watched on an idle clock."""
    assert decode(byte) == "off"


def test_the_face_numbers_are_the_ones_recorded():
    assert FACTORY_SCENES["off"] == 0
    assert FACTORY_SCENES["weather"] == 4
    assert FACTORY_SCENES["repeat_all"] == 255
