# Changelog

All notable changes to this project will be documented in this file.

## [1.18.1] - 2026-08-11
### Fixed
- Last Notification now carries `count` and `received_at`. The clock repeats itself, and
  a sensor that only records changes hid every repeat -- five button presses pushing the
  same byte looked like one. Counting them is the difference between an instrument and a
  decoration.

## [1.18.0] - 2026-08-11
### Added
- **The integration now listens to the clock.** Both Glance characteristics carry the
  notify property, so the clock can speak first -- it just had nobody listening. Anything
  it pushes is fired as a `glance_clock_notification` event carrying the characteristic
  and the raw bytes, which makes it usable as an automation trigger in Node-RED or a
  Home Assistant automation.
- A **Last Notification** diagnostic sensor showing the most recent push and which
  characteristic it came from, so this is visible without watching the event bus.

  What the clock actually sends is undocumented and, as of this release, unobserved. The
  interesting candidate is the physical button: the clock has exactly one, and if a press
  arrives here it becomes a trigger for anything.

## [1.17.1] - 2026-08-11
### Added
- `read_characteristic` accepts `list`, which enumerates every service and
  characteristic with the properties each supports. Whether the clock can push anything
  at all -- a button press, a timer expiring -- comes down to whether some
  characteristic carries notify, and nothing available documents that.

### Notes
- The ambient light reading is **not** exposed over GATT reads. Fifteen samples across
  two minutes with a lamp on the sensor, with `brightnessSceneStart` (61) active and the
  clock in automatic mode, left all three characteristics byte-identical. Command 61 does
  work -- the clock displays "Auto" -- it just publishes nothing. Notifications remain
  untested, and are the only path left.

## [1.17.0] - 2026-08-11
### Added
- A **Read characteristic** service. The clock exposes characteristics this integration
  never reads, and what is in them is undocumented. It returns a service response rather
  than logging: this deployment writes no log file to disk, and a message nobody can
  retrieve is the same as no message -- which is exactly how a whole day was lost.

## [1.16.1] - 2026-08-11
### Changed
- **Time Mode** is now **Digital Clock**. It shows and hides the digital time on the
  matrix, which the old name -- taken from the protocol field `timeModeEnable` -- did
  not say. The control was there all along; nobody could tell that it was.

## [1.16.0] - 2026-08-11
### Added
- **The three effects are now in the Animation select**, alongside the firmware
  animations: `pulse`, `wave` and `light_flash`. They use the same colour and speed
  controls and the same Animation Run and Animation Stop buttons, so nothing about them
  needs YAML. An effect needs an area lit before it can modulate one, and the button
  fills the whole ring first and chains the effect after it.

### Changed
- A bad speed or colour on Animation Run now surfaces in the interface instead of only
  in the log, the same way the LED services do since 1.15.0.

## [1.15.1] - 2026-08-11
### Verified on hardware
- All three effects now confirmed working. `pulse` breathes in place. `wave` runs across
  the rings from the inside out, not around them. `light_flash` flashes at uneven
  intervals and **replaces** the area's colour rather than layering over it, so the fill
  colour is gone for its duration -- pick the flash colour as the one you want to see.

## [1.15.0] - 2026-08-11
### Fixed
- **An unknown colour name failed as silence.** The services caught the error, logged
  it, and returned, so the call looked like it had succeeded and the clock simply never
  heard from it. They now raise, so the mistake appears where it was made. The message
  lists the palette, which is all it ever took to fix.
- The palette is the firmware's own and has no plain `green`, `purple`, `orange` or
  `cyan` -- the first names anyone reaches for. Those, plus `cyan`, `magenta`, `violet`,
  `gold`, `spring_green` and `off`, now resolve to their nearest real entry.

### Verified on hardware
- `wave` runs across the rings from the inside out, not around them, and leaves the
  rings at different intensities when it stops.
- An effect must be chained after the fill that drew its area, never overlapped with it.

### Correction to 1.14.0
- The claim that the clock ignores scenes sent to a busy slot was **wrong**. Every test
  that appeared to show it used the colour name `green`, which does not exist, so those
  scenes were never sent at all. The slot is still cleared before a write, which is
  harmless and may still be worth doing, but it is unverified and fixed nothing.

## [1.14.1] - 2026-08-11
### Changed
- **Confirm Hand Position** is now **Confirm Hand Positions at 12**. The button names
  its precondition rather than its action: pressing it while the hands are anywhere but
  straight up teaches the clock a wrong reference, and the old name did not say so.

## [1.14.0] - 2026-08-11
### Fixed
- **[Later shown to be wrong -- see 1.15.0.]** Scenes sent to a busy slot were
  believed to be silently dropped: the clock was thought to ignore a scene
  written to a slot that is still playing: it acknowledges the write, draws nothing,
  and logs nothing. Every scene service now clears the slot before writing it, so a
  send does what it says. This was behind a long run of tests that looked like broken
  effects, a broken slot, and then broken firmware -- it was none of those.
- Buttons no longer stay greyed out after the clock reconnects. They do not poll, so
  availability was only re-evaluated when something else happened to write their state;
  a button set up while the clock was still connecting looked dead but worked.

## [1.13.0] - 2026-08-11
### Added
- A **Send command** service for raw command frames. The firmware understands more than
  this integration models, and some of it only matters in situations that are awkward to
  reach -- scene playback being left stopped after a power cycle, for one. It also gives
  Node-RED a way to drive the clock without waiting for a named service to exist.

  Commands 42 and 50 are refused. They unpair the clock, which has no pairing button to
  recover with, and wipe user data that the manufacturer's servers can no longer restore.

### Notes
- `pulse` is confirmed working on hardware. An effect must **not** overlap the fill that
  drew its area: the fill holds the area at a constant colour for its whole lifetime and
  overwrites the effect's modulation. Chaining the steps, which is what happens when a
  step omits `at`, is the correct shape. `wave` and `light_flash` remain unverified.

## [1.12.0] - 2026-08-11
### Added
- A **Sound** select and a **Sound Play** button. The clock has eighteen sounds whose
  names say little about how they sound, so they can now be auditioned from the device
  page. The sound's name is shown on the clock while it plays, so stepping through the
  list tells you which is which.

### Changed
- The animation controls are named **Animation Run** and **Animation Stop** rather than
  "Run Animation" and "Stop Animation", so every animation control sorts together in
  the UI. Entity ids are unchanged, so existing automations keep working.

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
