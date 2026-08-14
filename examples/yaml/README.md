# YAML examples

Home Assistant automations, scripts and one-off service calls for the Glance
Clock. Every file stands alone — copy the one you want and change the entity
ids.

For the drawing model these assume — ring geometry, the fixed palette, scene
slots, step types — see [SCENES.md](../../SCENES.md). For the same ideas wired
up in Node-RED, see [`../node-red/`](../node-red/).

## How to use these

**`automations/`** — paste into **Settings → Automations & Scenes → Create
automation → ⋮ → Edit in YAML**, replacing everything in the editor. Or drop the
file's contents into `automations.yaml` as a list item.

**`scripts/`** — goes under `script:` in `configuration.yaml`, or into
`scripts.yaml` as-is. The exception is `demo-and-self-test.yaml`, which is
written for the UI script editor instead: it starts at `alias:` with no key
above it, so it can be pasted whole into **Scripts → Add script → Edit in
YAML**. It is meant to be run once and watched. It carries a `demo_version`,
printed in the notification it leaves behind, so a recording can be matched to
the script that produced it — bump it whenever the file changes.

**`scenes/`** — single service calls, not Home Assistant scenes. Paste into
**Developer Tools → Actions → YAML mode** and press Perform action. They are
here to be run once and looked at, and then stolen from.

## Which service for which job

| The situation | The service |
| :-- | :-- |
| **Something happened** | `send_notice` — immediate, interrupts, then gone |
| **Something is true right now** | `set_leds` / `set_scene` — arrives at once, stays until cleared |
| **Something is counting down** | `send_timer` — the clock runs it itself |
| **The weather** | `send_forecast` (temperature graph, slot 1) or a `weather` scene step (particles) |

Both arrive at once, so this is about shape rather than speed: a notice takes
the display and hands it back, a scene sits alongside the time until its slot is
cleared. A doorbell that stays on the rings until somebody clears it is the
wrong tool, however promptly it got there.

## automations/

### Announcements

| File | What it does |
|---|---|
| [`doorbell.yaml`](automations/doorbell.yaml) | The obvious one, and the shape every other notice follows |
| [`washing-machine.yaml`](automations/washing-machine.yaml) | Power-based detection with a `for:`, so a pause mid-cycle stays quiet |
| [`water-leak.yaml`](automations/water-leak.yaml) | A flashing scene *and* a notice repeated until the sensor clears |
| [`gate-opened.yaml`](automations/gate-opened.yaml) | Waits for the busy sensor first, so nothing is lost |

### State on the rings

| File | What it does |
|---|---|
| [`progress-ring.yaml`](automations/progress-ring.yaml) | Any 0-100 sensor as an arc. The workhorse |
| [`workday-band.yaml`](automations/workday-band.yaml) | 08:00–17:00 as a band in its real position on the dial |
| [`electricity-price.yaml`](automations/electricity-price.yaml) | The inner ring tinted by what the hour costs |
| [`weather-particles.yaml`](automations/weather-particles.yaml) | Snow, rain or fog — and clearing the slot when it stops |
| [`away-clear.yaml`](automations/away-clear.yaml) | Tidy every slot when the house empties |

### Housekeeping

| File | What it does |
|---|---|
| [`brightness.yaml`](automations/brightness.yaml) | Manual in the evening, automatic again at sunrise |
| [`restore-on-startup.yaml`](automations/restore-on-startup.yaml) | Recompute the standing scenes after a restart |
| [`tea-timer.yaml`](automations/tea-timer.yaml) | A staged timer the clock runs by itself |

Quiet hours are not an automation. The clock has a DND window it applies
**itself**, which keeps working while Home Assistant is down — set it once and
leave it:

```yaml
action: glance_clock.set_dnd_schedule
data:
  from_hour: 22
  till_hour: 6
  recurring: true
```

The same window is on the device page as the **DND Start** and **DND End**
number entities.

For "quiet until I say otherwise" rather than "quiet between these hours", there
is a **Do Not Disturb Hold** switch. It sets the firmware's own permanent flag,
so the clock keeps applying it while Home Assistant is elsewhere. This page used
to say that flag was unreachable; it was only unexposed — settings writes had
been carefully preserving it the whole time.

Whether the window is in force *right now* is a separate question, and the clock
answers it: `binary_sensor.<name>_do_not_disturb`, pushed the moment it changes,
with the mute flag alongside as an attribute.

## scripts/

| File | What it does |
|---|---|
| [`glance-say.yaml`](scripts/glance-say.yaml) | `script.glance_say` — one queued entry point for every notice |
| [`clear-all-slots.yaml`](scripts/clear-all-slots.yaml) | `script.glance_clear_all` — empty every slot when an experiment goes wrong |
| [`demo-and-self-test.yaml`](scripts/demo-and-self-test.yaml) | About a minute that exercises everything, in an order that reads as a demo |

`glance_say` is worth having even in a small setup: `mode: queued` means several
automations can call it at once and the messages come out one after another
instead of overwriting each other.

`glance_clear_all` is the way out. A scene stays in its slot and replays until
cleared, so an experiment that went wrong keeps going wrong on the wall — and
the slot number is exactly the thing nobody writes down. There is a **Clear All
Scenes** button on the device page that does the same in one click.

Clearing everything writes eight deletes in a row and took about five seconds on
hardware, with a blank dial throughout. That is fine as a way out of a mess, and
poor inside a sequence you are watching — when you know which slots you used,
call `clear_leds` on those instead.

## scenes/

Run them from Developer Tools, watch what happens, then take the parts you want.
They go up the difficulty curve roughly in this order:

| File | What it shows |
|---|---|
| [`gauge-with-track.yaml`](scenes/gauge-with-track.yaml) | Two segments in one call, and why order matters |
| [`quarter-markers.yaml`](scenes/quarter-markers.yaml) | The 4-pixels-to-an-hour geometry |
| [`ring-fill.yaml`](scenes/ring-fill.yaml) | A timeline, and the fact that fills persist |
| [`countdown-empty.yaml`](scenes/countdown-empty.yaml) | The same in reverse — black as paint, not transparency |
| [`comet.yaml`](scenes/comet.yaml) | Motion, which is persistence plus a black segment |
| [`pulse-breathe.yaml`](scenes/pulse-breathe.yaml) | An effect, which needs a fill under it |
| [`text-with-sound.yaml`](scenes/text-with-sound.yaml) | `at:` for simultaneous steps, and why text needs `exclusive` |

Clear any of them off the clock again with:

```yaml
action: glance_clock.clear_leds
data:
  slot: 3
```

## Two things that will look like bugs

**A short scene runs, then stands still.** It finishes its timeline and waits
for the engine's next pass — about twelve seconds — before repeating. Build a
timeline of roughly 15 seconds if you want continuous motion.

**The scene will not go away.** Scenes persist in their slot and replay until
cleared. Ending a lifetime does not remove one.

The longer list is at the end of [SCENES.md](../../SCENES.md#things-that-will-look-like-bugs).
