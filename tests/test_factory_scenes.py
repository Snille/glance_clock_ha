"""The clock's own built-in faces, and the byte that selects them.

The table is from mrmstn/glance_clock_ha (MIT), which took it from the official
Android application. It describes what you WRITE to scene_data.

It does not describe what the clock PUSHES on the same characteristic, and
assuming it did shipped a real bug in 1.29.0: the Factory Scene select read the
pushed byte back to find out which face was showing, and 0x81 -- an idle clock
with its digits on -- decoded as "calendar". The clock pushes a status byte
after any setting is touched, so the control announced a face nobody had
selected, over and over. The last test here is what stops that returning.
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


def test_the_inactive_flag_sits_on_the_bit_the_busy_sensor_calls_idle():
    """The one place the two readings genuinely agree.

    Bit 7 clear means something is on the display, whether you got there by
    selecting a face or by sending a scene. The low bits are where they part
    company -- see the module docstring.
    """
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


def test_the_select_does_not_read_the_pushed_byte_back():
    """The 1.29.0 bug, in one assertion.

    A face number goes out; nothing comes back. If this control ever starts
    listening to glance_clock_notification or reading scene_data again, it will
    resume announcing "calendar" whenever the clock reports an idle display with
    the digital time showing.
    """
    source = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "glance_clock"
        / "select.py"
    ).read_text(encoding="utf-8")

    # Writing to scene_data is the whole point, so the UUID stays. What must
    # not come back is any path that turns a byte from the clock into state.
    assert "decode_factory_scene" not in source
    assert "glance_clock_notification" not in source
    assert "read_characteristic" not in source
