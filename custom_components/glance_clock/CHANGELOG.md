# Changelog

All notable changes to this project will be documented in this file.

## [1.11.0] - 2026-08-11
### Added
- A **Mute** switch. The clock's permanent mute flag was neither visible nor settable,
  so a muted clock looked like broken sound support rather than a setting.

### Fixed
- Non-ASCII characters are transliterated instead of masked to 7 bits. Masking turned
  them into different letters -- "Hej då" arrived as "Hej de" -- which is worse than
  either translating or dropping them. Anything still unmappable now becomes the font's
  own missing-character glyph, so a lost letter is visible. Applies to notices, timers
  and scene text alike.
- `set_scene` warns when a text step is combined with `watchface` mode. The digital
  clockface owns the matrix there, so the text never appears; silence looked like a
  broken service.

## [1.10.0] - 2026-08-11
### Added
- `set_scene` steps now take a `type`, unlocking the rest of the CustomScene object:
  - `effect` -- pulse, wave or light_flash, layered onto areas already drawn in the
    same scene rather than drawing anything itself. Pulse takes rise and fall times,
    wave and light_flash take a speed, and light_flash its own colour.
  - `weather` -- snow, rain or fog as a particle effect over the whole face or half of
    it, with an intensity. It is not a forecast readout. Verified on hardware: snow
    drifts across the face with the digital time still readable underneath.
  - `text` -- text that stays on screen, unlike a notice, with the same `[icon:CODE]`
    markers.
  - `sound` -- a sound cue placed at a frame on the timeline.

### Changed
- `text_with_icons_to_bytes` was defined twice as a nested function; it is now one
  module-level helper shared by notices, timers and scenes.

## [1.9.0] - 2026-08-11
### Added
- `glance_clock.set_scene`: a timed sequence of fills that the clock plays itself at
  50 frames per second. One call uploads the whole timeline, which is the only way to
  animate -- sending fills one at a time cannot, because a scene change only takes
  effect on the clock's roughly 15 second scene cycle.

Verified on hardware with an eight step chase around the rings. Two things worth
knowing: anything drawn stays on screen after its step ends, so a step that should
erase has to paint black over it; and the clock restarts the scene on its own cycle,
so a timeline shorter than about 750 frames pauses visibly before repeating.

## [1.8.0] - 2026-08-11
### Added
- Animation controls on the device page: an **Animation** select, an **Animation
  Colour** select, an **Animation Speed** slider and **Run Animation** / **Stop
  Animation** buttons. The whole thing can now be driven from the UI without writing
  a service call.

The selects and the slider are local choices rather than device state -- the clock
stores no pending animation -- so they restore across restarts. Black is left out of
the colour list: it is a valid colour that renders nothing, which is indistinguishable
from a broken integration. Run Animation always uses the same scene slot, so running
one replaces the last instead of filling the clock's slots and making it cycle.

## [1.7.0] - 2026-08-11
### Added
- `glance_clock.set_animation`, exposing the animations built into the firmware:
  fire, wheel, flower, flower2, fan, sun, thunderstorm and cloud, plus a `sweep`
  that fills the ring from a start pixel and repeats.

They are single-colour patterns tinted by the colour you pick, so a colour must be
given -- black renders nothing at all. Only `sweep` has a direction: its speed sign
reverses it. The firmware animations render lengths in multiples of 8 and round
anything else down, which the service now warns about instead of leaving it looking
like a bug.

## [1.6.0] - 2026-08-11
### Added
- `glance_clock.set_leds` and `glance_clock.clear_leds`, giving direct control of the
  four 48-pixel LED rings through CustomScene fills. Areas are described by start
  pixel, length, ring and colour; several can be lit in one call.
- Display mode is selectable: `watchface` shows the scene together with the digital
  time, `exclusive` hides the digital clockface, `ring_and_text` alternates with it.

The segment layout was mapped against hardware: pixel 0 sits at twelve o'clock and
numbering runs clockwise, ring 0 is the outermost, and length and height are stored
one less than their real values.

## [1.5.0] - 2026-08-11
### Added
- **Calibrate Hands** and **Confirm Hand Position** buttons on the device page, so the
  whole hand calibration can be done from Home Assistant the way the original app
  allowed. Previously this was only reachable through the options flow.

## [1.4.0] - 2026-08-11
### Fixed
- Brightness is no longer treated as a plain 0-255 value. Measured against hardware,
  only the low byte of `displayBrightness` is the manual level -- 1 is barely visible,
  255 is full, and 0 hands control back to the ambient light sensor. A working clock
  reported 2016768 (`0x1EC600`) in that field, so the old code both misreported the
  state (calling automatic "brightness 2016768") and destroyed the upper bits when
  writing, which has been observed to leave the rim points dark. The upper bits are
  now preserved.

## [1.3.1] - 2026-08-11
### Fixed
- Two settings changes in quick succession no longer undo each other. The settings
  cache was filled on read, lived for 60 seconds and was never invalidated after a
  write, so a second change started from pre-first-change bytes and silently reverted
  it. This is why switches in Home Assistant could disagree with the device. Writes
  now update the cache with what was actually sent.

## [1.3.0] - 2026-08-10
### Fixed
- Settings writes no longer discard fields this integration does not model. The
  message was rebuilt from nine named fields, which deleted the device's nested
  Do-Not-Disturb schedule and an undocumented field, and invented
  `mgrUserActivityTimeout`. Writing that field as `0` stops the twelve rim points
  staying lit. Writes now parse the device's own bytes and change only what the
  caller asked for. Verified against hardware (model 666, firmware 1.6.7).
- `mgrUserActivityTimeout` removed from the no-read fallback defaults rather than
  invented for a device that may not use it.

### Added
- `glance_clock.set_dnd_schedule` and `glance_clock.read_dnd_schedule` services for
  the recurring Do-Not-Disturb window stored on the clock.
- **DND Start** and **DND End** number entities so the window can be adjusted from
  the device page.
- Tests covering settings preservation and the DND submessage.

## [1.2.0] - 2025-11-14
### Added
- Support for icons in notification text using `[icon:CODE]` syntax. See `ICONS.md` for available codes.
- New timer service: send timer scenes with intervals and final text, including icon support.
- Major code cleanup and refactor:
	- Moved service handlers to dedicated files under `services/`.
	- Moved color utilities to `utils/color_utils.py`.
	- Improved Bluetooth connection management and modularized code.
	- Updated and clarified documentation and service descriptions.

## [1.1.0] - 2025-11-11
### Added
- Calibration flow added to the integration.
- Placeholder for "Scene clear" added to integration

## [1.0.2]
### Added
- Updated readme to include Bluetooth CTS addon

## [1.0.1]
### Added
- Cleanup and HAC submission prep

## [1.0.0]
### Added
- Initial release.
