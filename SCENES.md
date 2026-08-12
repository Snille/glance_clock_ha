# Scenes, colours and the LED rings

Everything on this page is about the four LED rings and the scene engine behind
them. Notifications are the other half of the clock and are covered in the
[README](./README.md); scenes are what you reach for when something should *stay*
on the display rather than announce itself and go away.

- [The display, physically](#the-display-physically)
- [The colour palette](#the-colour-palette)
- [Three ways to draw](#three-ways-to-draw)
- [The ready-made animations](#the-ready-made-animations)
- [Building your own scene](#building-your-own-scene)
- [Step types](#step-types)
- [Scene slots](#scene-slots)
- [Display modes](#display-modes)
- [Timing, and why the clock waits](#timing-and-why-the-clock-waits)
- [Worked examples](#worked-examples)
- [Things that will look like bugs](#things-that-will-look-like-bugs)

## The display, physically

Four concentric rings, each of **48 pixels**. Pixel 0 sits at twelve o'clock and
numbering runs **clockwise**. **Ring 0 is the outermost**, ring 3 the innermost.

```
              0
        44         4
     40               8      ring 0  (outer)
                             ring 1
   36     ( 12 : 34 )   12   ring 2
                             ring 3  (inner)
     32              16
        28         20
              24
```

Since 48 divides evenly by 12, one hour on a clock face is **4 pixels** — pixel
0 is twelve, pixel 12 is three o'clock, pixel 24 is six, pixel 36 is nine. That
makes the rings genuinely good at anything time-shaped, and it is why the
original manufacturer's API drew calendars this way.

An area of light is described by five numbers:

| Field | Range | Meaning |
|---|---|---|
| `start` | 0–47 | First pixel, clockwise from twelve o'clock |
| `length` | 1–48 | How many pixels to light |
| `ring` | 0–3 | Which ring to start on, counted from the outside |
| `rings_tall` | 1–4 | How many rings the area covers, inwards |
| `color` | name | From the palette below |

`ring + rings_tall` may not exceed 4 — the clock rejects an area that runs off
the inner edge, and the integration raises before it gets that far.

There is also a **text matrix**, 48 × 4, which the digital clockface normally
occupies. That matters for text steps; see [Display modes](#display-modes).

## The colour palette

The clock has a **fixed palette of 25 colours**. There is no arbitrary RGB —
anything you send is one of these indices. This is firmware, not a limitation of
the integration.

| # | Name | Approx. | | # | Name | Approx. |
|---|---|---|---|---|---|---|
| 0 | `black` | ⬛ #000000 | | 13 | `light_slate_blue` | 🟦 #8470FF |
| 1 | `dark_golden_rod` | 🟨 #B8860B | | 14 | `royal_blue` | 🟦 #4169E1 |
| 2 | `dark_orange` | 🟧 #FF8C00 | | 15 | `blue` | 🟦 #0000FF |
| 3 | `olive` | 🟫 #808000 | | 16 | `cornflower_blue` | 🟦 #6495ED |
| 4 | `orange_red` | 🟧 #FF4500 | | 17 | `sky_blue` | 🟦 #87CEEB |
| 5 | `red` | 🟥 #FF0000 | | 18 | `turquoise` | 🟩 #40E0D0 |
| 6 | `maroon` | 🟥 #800000 | | 19 | `aqua` | 🟩 #00FFFF |
| 7 | `dark_magenta` | 🟪 #8B008B | | 20 | `medium_spring_green` | 🟩 #00FA9A |
| 8 | `medium_violet_red` | 🟪 #C71585 | | 21 | `lime_green` | 🟩 #32CD32 |
| 9 | `brown` | 🟫 #A52A2A | | 22 | `dark_green` | 🟩 #006400 |
| 10 | `indigo` | 🟪 #4B0082 | | 23 | `lime` | 🟩 #00FF00 |
| 11 | `blue_violet` | 🟪 #8A2BE2 | | 24 | `lawn_green` | 🟩 #7CFC00 |
| 12 | `white` | ⬜ #FFFFFF | | | | |

The hex values are the CSS colour names the palette is named after. They tell
you what the firmware was aiming at, not what a small diffused LED actually
looks like on a wall — the dark shades in particular (`maroon`, `dark_green`,
`olive`, `indigo`) read considerably dimmer in the room than on screen. Treat
the table as a starting point and trust your eyes.

Note what is *not* there: no plain green, purple, orange or cyan — the first
four names anyone reaches for. The integration accepts them as aliases:

| You write | You get |
|---|---|
| `green` | `lime_green` |
| `cyan` | `aqua` |
| `magenta` | `dark_magenta` |
| `purple` | `indigo` |
| `violet` | `blue_violet` |
| `orange` | `dark_orange` |
| `gold` | `dark_golden_rod` |
| `spring_green` | `medium_spring_green` |
| `off` | `black` |

**`black` is not transparent, it is paint.** Filling an area with black is how
you erase it. A firmware animation tinted black renders nothing at all, which is
the one case where "off" is a surprise rather than a convenience.

A colour name that does not exist raises a `ServiceValidationError` naming the
whole palette — with one exception. `send_notice` falls back to white on an
unknown colour instead of failing, so a typo there shows up as an unexpectedly
white notice rather than an error.

## Three ways to draw

The integration offers three services, in rising order of effort:

| Service | Use it for | Animates? |
|---|---|---|
| `set_leds` | A static picture — arcs, gauges, indicators | No |
| `set_animation` | One of the firmware's built-in patterns | Yes, by itself |
| `set_scene` | Anything you design yourself, frame by frame | Yes, you author it |

They all write to a scene slot, and they all behave the same way afterwards:
what you sent stays until the slot is cleared.

### `set_leds` — a static picture

```yaml
action: glance_clock.set_leds
data:
  mode: watchface
  slot: 3
  segments:
    - start: 0
      length: 12
      ring: 0
      color: red
    - start: 24
      length: 6
      ring: 1
      color: sky_blue
```

`length` defaults to 1, `ring` to 0, `rings_tall` to 1. A segment needs at
minimum `start` and `color`.

### `set_animation` — the firmware's own

```yaml
action: glance_clock.set_animation
data:
  animation: fire
  color: orange_red
  speed: 3
  ring: 0
  rings_tall: 4
```

### `set_scene` — your own timeline

See [Building your own scene](#building-your-own-scene) below.

## The ready-made animations

Nine patterns live in the firmware. They are **single-colour** — the pattern is
fixed, and `color` tints it.

| Name | What it looks like |
|---|---|
| `sweep` | Fills the area from its start pixel, pauses, repeats |
| `fire` | Flickering, uneven, warmest with `orange_red` or `red` |
| `wheel` | A rotating spoke — this is the one the old Uber integration used |
| `flower` | Petals opening and closing from the centre |
| `flower2` | The same idea, different rhythm |
| `fan` | Rotating blades, denser than `wheel` |
| `sun` | A pulsing radial burst |
| `thunderstorm` | Irregular bright flashes |
| `cloud` | Slow drifting, low contrast |

Two quirks are worth knowing before you spend an evening on it:

**Only `sweep` has a direction.** Its `speed` runs −10 to 10 and the sign
reverses it; anticlockwise is a negative speed. The other eight take 0–10 and a
negative value is rejected rather than silently clamped, because a silent clamp
would look like the direction argument being ignored.

**The eight firmware animations only render lengths that are a multiple of 8.**
Anything else is rounded down by the clock. Ask for 20 pixels and you get 16.
The integration logs a warning saying so rather than letting the result look
like a bug. `sweep` is exempt — it takes any length.

### The three effects

Separate from the animations, and different in kind: `pulse`, `wave` and
`light_flash` do not draw anything themselves. They **modulate an area that has
already been drawn** in the same scene, which means an effect step has to come
*after* the fill that painted its area.

| Effect | Behaviour |
|---|---|
| `pulse` | The area breathes, dimming and brightening in place. Takes `rise` and `fall` |
| `wave` | Runs across the rings from the inside out — not around them — and leaves them at differing intensities when it stops |
| `light_flash` | Flashes at uneven intervals, and **replaces** the area's colour rather than layering over it. Pick the flash colour as the one you want to see |

From the device page they behave like ordinary animations, because the Animation
Run button draws an area for them first.

## Building your own scene

A scene is **a timeline you upload in one call**, which the clock then plays by
itself at 50 frames per second. This is the part worth internalising: you do not
animate by sending a series of service calls. A scene change only takes effect
on the clock's own cycle, so a sequence of calls produces a stutter, not motion.
One call carries the whole animation.

```yaml
action: glance_clock.set_scene
data:
  mode: watchface
  slot: 3
  steps:
    - seconds: 0.5
      segments:
        - { start: 0, length: 6, ring: 0, rings_tall: 4, color: red }
    - seconds: 0.5
      segments:
        - { start: 0, length: 6, ring: 0, rings_tall: 4, color: black }
        - { start: 6, length: 6, ring: 0, rings_tall: 4, color: red }
```

That is a red block that moves. The second step paints the first position black
— because **anything drawn stays on screen after its step ends**. Leave the
black fill out and you get a ring filling up instead of a block travelling
around it. Both are useful; know which one you are building.

### Timing a step

Every step takes one of:

- `seconds` — converted at 50 fps, so `0.5` is 25 frames. Fractions are fine.
- `frames` — exact, 1/50 s each.
- neither, in which case `default_frames` applies (25 frames, half a second).

A step without `at` **follows on from the previous one**, which is what you want
almost every time. Give `at` explicitly — a frame number from the start of the
scene — when you want steps to overlap or to start together:

```yaml
steps:
  # A fill and a sound firing at the same instant
  - at: 0
    seconds: 3
    segments: [{ start: 0, length: 48, rings_tall: 4, color: royal_blue }]
  - at: 0
    type: sound
    sound: bells
```

### The flat shorthand

A step with exactly one area can skip the nested list and write the segment's
fields directly on the step:

```yaml
- seconds: 1
  start: 0
  length: 12
  color: red
```

## Step types

Five kinds. `fill` is the default and needs no `type`.

### `fill`

Paints areas. Takes `segments` (or the flat shorthand above).

```yaml
- type: fill
  seconds: 1
  segments:
    - { start: 0, length: 24, ring: 0, rings_tall: 2, color: lime_green }
```

### `effect`

Modulates areas already drawn. Takes `effect` (`pulse`, `wave`, `light_flash`),
`segments`, and depending on the effect `rise`, `fall`, `speed` and `color`.
Each effect reads its own settings and ignores the rest, so passing all of them
is harmless.

```yaml
- type: effect
  effect: pulse
  rise: 20
  fall: 80
  segments: [{ start: 0, length: 12, rings_tall: 4, color: royal_blue }]
  seconds: 3
```

### `text`

Puts a string on the matrix. Unlike a notice, it **stays**.

```yaml
- type: text
  text: "Ute: -3[icon:176]C"
  scroll: repeat        # none | repeat | rapid | delay
  seconds: 10
```

Two constraints:

- **Text does not render in `watchface` mode.** The digital clockface owns the
  matrix there, so the text has nowhere to go and simply never appears. Use
  `exclusive`. The integration logs a warning when you get this wrong.
- **The font is limited.** Swedish letters are transliterated — `å` and `ä`
  become `a`, `ö` becomes `o`. Anything with no glyph is replaced by a visible
  box rather than dropped, so a mangled string looks wrong instead of looking
  fine. `[icon:CODE]` inserts a built-in glyph; the codes are in
  [ICONS.md](./ICONS.md), and 176 is the degree sign.

### `sound`

A cue at a point on the timeline. Takes a name or an index.

```yaml
- type: sound
  sound: bells
```

All eighteen: `none`, `waves`, `rise`, `charging`, `steps`, `radar`, `bells`,
`bye`, `hello`, `flowers`, `circles`, `complete`, `popcorn`, `break`, `opening`,
`high`, `shine`, `extension`. There is a Sound select and a Sound Play button on
the device page for auditioning them.

**Sound needs the clock unmuted.** A muted clock plays nothing and reports no
error, which looks exactly like a bad sound name. There is a Mute switch on the
device page.

Unknown sound names raise here, unlike in `send_notice`.

### `weather`

A particle effect drawn by the clock — not a forecast readout.

```yaml
- type: weather
  condition: snow       # snow | rain | fog
  position: full        # full | upper | lower
  intensity: 8          # 0-10
  seconds: 15
```

For an actual temperature graph, use `send_forecast`, which is a different thing
entirely and writes to slot 1.

## Scene slots

There are **eight slots, 0–7**. A slot holds one scene, and a scene stays in its
slot and replays until something clears it. Sending to an occupied slot replaces
what was there.

| Slot | Claimed by |
|---|---|
| 0 | The Animation Run button on the device page — and the default for every service |
| 1 | `send_forecast` |
| 2–7 | Yours |

Two things sharing a slot means whichever arrives second wins, so give each of
your own scenes a slot and write it down somewhere. Clearing:

```yaml
action: glance_clock.clear_leds
data:
  slot: 3
```

This is also how the forecast comes off the clock — `clear_leds` with slot 1.

## Display modes

Every drawing service takes `mode`:

| Mode | Behaviour |
|---|---|
| `watchface` | The scene draws on the rings alongside the digital time. The default |
| `exclusive` | The scene owns the display; the digital clockface is hidden while it shows |
| `ring_and_text` | The scene joins the rotation, alternating with the clockface every ~15 s |

`watchface` for anything ambient you want visible next to the time.
`exclusive` when you need the matrix — that is, for text.

## Timing, and why the clock waits

**The scene engine updates on a roughly 15-second cycle.** A scene you send
appears when that cycle comes round, up to fifteen seconds later. This is the
single most important thing to design around, and it drives one rule:

> Notices are for things that *happen*. Scenes are for showing *state*.

A timer finishing, a door opening, the coffee being ready — those are notices,
and a notice interrupts and shows at once. Battery level, a progress ring, the
weather, how much of the workday is left — those are scenes, and nobody minds
that they arrived twelve seconds ago.

The same cycle is why a short scene visibly waits before repeating: a timeline
shorter than about 750 frames finishes, then sits there until the cycle brings
it round again. If you want continuous motion, either build a timeline of
roughly 15 seconds or accept the pause as part of the rhythm.

Filmed on hardware 2026-08-12, which puts numbers on all of that. A 2.4 second
comet ran its twelve steps at exactly four pixels per 0.2 s, then stood still
for about twelve seconds before running again. A 14 second pulse never went
dark at all, so a timeline built to fill the cycle does read as continuous.

The same recording settled the effect timings: `rise: 20` and `fall: 80` gave a
breath of almost exactly two seconds, which is 100 frames at 50 fps. The units
are frames, and they behave.

And one thing worth stealing: **a scene that draws has to sweep up after
itself.** When the comet's last step left its head and tail lit, they stayed lit
for the whole twelve second wait, because nothing ever painted over the final
position. A closing step of black is the difference between an animation and an
animation that leaves a smear on the wall.

`life_time` on `set_leds` and `set_animation` is frames at 50 fps before the
scene **stops animating**. It is not how long the scene is visible — a fill
stays on screen afterwards, and the slot stays occupied either way.

## Worked examples

These live in [`examples/yaml/scenes/`](./examples/yaml/scenes/) as files you can
paste straight into **Developer Tools → Actions → YAML mode** and run. Roughly in
order of difficulty:

| Example | What it shows |
|---|---|
| [`gauge-with-track.yaml`](./examples/yaml/scenes/gauge-with-track.yaml) | Two segments in one call, and why paint order matters |
| [`quarter-markers.yaml`](./examples/yaml/scenes/quarter-markers.yaml) | The four-pixels-to-an-hour geometry, as a frame of reference |
| [`ring-fill.yaml`](./examples/yaml/scenes/ring-fill.yaml) | A timeline, and the fact that fills persist |
| [`countdown-empty.yaml`](./examples/yaml/scenes/countdown-empty.yaml) | The same in reverse — black as paint, not transparency |
| [`comet.yaml`](./examples/yaml/scenes/comet.yaml) | Motion, which is persistence plus one black segment |
| [`pulse-breathe.yaml`](./examples/yaml/scenes/pulse-breathe.yaml) | An effect, and the fill it needs underneath |
| [`text-with-sound.yaml`](./examples/yaml/scenes/text-with-sound.yaml) | `at:` for simultaneous steps, and why text needs `exclusive` |

The shortest useful one, in full — a progress arc two thirds of the way round:

```yaml
action: glance_clock.set_leds
data:
  slot: 3
  mode: watchface
  segments:
    - { start: 0, length: 32, ring: 0, rings_tall: 2, color: lime_green }
```

For a live value, compute the length in a template — see
[`examples/yaml/automations/progress-ring.yaml`](./examples/yaml/automations/progress-ring.yaml).

Writing a comet by hand is twelve near-identical steps, which is exactly what a
template or a Node-RED function node is for. Compare `comet.yaml` above with
[`examples/node-red/comet.json`](./examples/node-red/comet.json), which generates
the same timeline in a six-line loop.

## Things that will look like bugs

Collected here so they cost you a minute rather than an evening.

**Nothing happened for fifteen seconds.** The scene engine's own cycle. Expected.
Use a notice if it needs to be immediate.

**The scene will not go away.** Scenes persist in their slot. `clear_leds` with
the right slot number. Ending a lifetime does not remove it.

**The animation is shorter than I asked for.** The eight firmware animations
round lengths down to a multiple of 8.

**My text never appears.** `watchface` mode. Switch to `exclusive`.

**No sound.** The clock is muted. There is a switch for it on the device page.

**The colour is wrong, or white.** A name outside the palette. In `send_notice`
that silently becomes white; everywhere else it raises with the full list.

**My animation drew nothing.** A firmware animation tinted `black`.

**The block smeared instead of moving.** Fills persist — paint black over the
previous position.

**Something stayed lit after the animation ended.** The same rule, at the end
rather than the middle: the last thing drawn has nobody to paint over it. Add a
closing step of black.

**Two scenes are fighting.** They share a slot. Slot 0 belongs to the device
page's animation buttons and slot 1 to `send_forecast`; start yours at 2.

**The effect did nothing.** `pulse`, `wave` and `light_flash` modulate an area
that has already been drawn. Put a fill step before them.
