# Changelog

All notable changes to this project will be documented in this file.

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
