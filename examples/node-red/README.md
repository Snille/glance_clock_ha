# Driving the clock from Node-RED

Everything the clock can do is a Home Assistant service call, so from Node-RED
it is a **call service** node with `glance_clock` as the domain. Nothing here
needs a custom node or a direct Bluetooth connection — Node-RED talks to Home
Assistant, and Home Assistant owns the clock.

The flows in this directory are meant to be read as much as imported. Each one
is short, and the interesting part is the payload rather than the wiring.

| File | What it does |
|---|---|
| `weather.json` | Turns a weather entity into snow, rain or fog on the rings |
| `espresso.json` | Watches a temperature sensor and says when the machine is ready |
| `progress-ring.json` | Turns any 0-100 sensor into an arc, with a dim track behind it |
| `notice-queue.json` | Waits for the clock to be free before sending, so nothing is lost |
| `comet.json` | Generates a scene timeline in code — the thing YAML is bad at |
| `clear-all-slots.json` | Empties all eight slots, paced so Bluetooth keeps up |

Import with **Menu → Import** and paste the file contents. Every flow
references entity ids you will need to change to your own.

For the drawing model these flows assume — ring geometry, the fixed palette,
scene slots, step types — see [SCENES.md](../../SCENES.md). For the same ideas
as Home Assistant automations, see [`../yaml/`](../yaml/).

## The three things worth knowing first

**A scene stays in its slot.** It does not vanish when its lifetime runs out —
it stays and replays until something clears the slot. Use `clear_leds` with the
same slot when you want it gone. This is the single most surprising thing about
the clock, and it will look like a bug the first time it happens.

**It also keeps the display for as long as its timeline runs.** `seconds` bounds
the animation, and nothing written during it is seen — a flow that fires two
scenes a few seconds apart shows only the first. Never let a timeline outlast
the gap before the next write. The same rule sinks forecasts, which are lost
rather than queued if the display is busy: `clear_leds` first, then send.

**A notice interrupts, a scene joins.** Both appear at once. The difference is
what happens afterwards: a notice takes the display and hands it back, a scene
sits alongside the time until its slot is cleared. Announce with a notice, show
with a scene.

One exception to that: a notice takes **slot 0** for itself, so a scene parked
there is destroyed rather than handed back. Start your scenes at slot 2, which
these flows do.

## Weather on the rings

`set_scene` has a `weather` step type. It is a particle effect, not a forecast
readout: snow falls, rain streaks, fog drifts. The clock draws it.

```yaml
service: glance_clock.set_scene
data:
  mode: watchface
  slot: 2
  steps:
    - type: weather
      condition: snow      # snow, rain or fog
      position: full       # full, upper or lower
      intensity: 7         # 0-10
      seconds: 30
```

Slot 2 is deliberate, and the slots are worth keeping straight: slot 0 belongs
to the animation buttons on the device page, and slot 1 is where
`send_forecast` writes its temperature graph. Two things sharing a slot means
whichever arrives second wins.

The flow maps a weather entity's state onto that: `snowy` becomes snow,
`rainy` and `pouring` become rain, `fog` becomes fog, and anything else clears
the slot so the clock goes back to normal. Intensity rises with `pouring`.

## The espresso machine

This is the case the clock is genuinely good at: a thing you are waiting for,
in a room you walk past, where you do not want to open an app to check.

The flow watches a temperature sensor and fires once when it crosses the ready
threshold — the `rbe` node matters here, or you get a notice every time the
sensor reports while hot.

```yaml
service: glance_clock.send_notice
data:
  text: "ESPRESSO [icon:130]"
  animation: pulse
  color: lime_green
  sound: bells
```

A notice takes an animation from its own list, which is not the same list as
the LED animations: `none`, `pulse`, `wave`, `fire`, `sun`, `wheel`, the
`flower` pair, `fan`, `cloud`, `thunderstorm`, and a set of `weather_*` icons.
`none` shows the text with no ring animation at all, which is what the Sound
Play button uses.

The `[icon:CODE]` syntax puts one of the clock's built-in glyphs inline; 130 is
the clock face. See `ICONS.md` in the repository root for the full list.

Text is drawn from a limited font. Swedish letters are transliterated -- `å`
and `ä` become `a`, `ö` becomes `o` -- and anything with no glyph at all is
replaced by a visible box rather than silently dropped, so a mangled string
looks wrong instead of looking fine.

### Cooling down again

The second half of the flow sends a notice when the machine drops back below
temperature. Leave it out if you find it chatty — it is there to show that a
notice is cheap and that the clock is fine being talked to often.

## A value as an arc

`progress-ring.json` is the workhorse flow: a 0-100 sensor becomes an arc on
the outer ring. Each ring is 48 pixels, so the length is the percentage times
0.48 — floored, then clamped to at least 1, because a `length` of 0 is invalid
and fails the call.

```javascript
let length = Math.floor((Math.min(Math.max(pct, 0), 100) / 100) * 48);
length = Math.min(Math.max(length, 1), 48);
```

Two segments rather than one, painted in order: a dim `dark_green` track over
the whole ring first, then the value drawn on top of it. Without the track an
empty ring is just darkness, and it stops reading as a gauge.

The flow also carries an inject node that clears the slot, because a scene does
not leave on its own.

## Not losing notices

`notice-queue.json` exists because **a notice sent while another one is playing
is not queued — it is lost**. The flow takes a notice on a link-in node, checks
`binary_sensor.<name>_busy`, and loops through a two second delay until the
clock is free. After ten tries it sends anyway and warns: after twenty seconds,
a message that might collide beats a message that definitely never arrives.

Send into it from any other flow with a link-out node:

```javascript
msg.payload = {
    text: 'PARCEL [icon:128]',
    color: 'dark_orange',
    sound: 'hello',
};
return msg;
```

Anything left out is filled in by the flow, so a text alone is a valid message.

## Generating a scene

`comet.json` is the case where Node-RED genuinely beats YAML. A scene is a
timeline you upload in **one** call, which the clock then plays by itself at 50
frames per second — so animation means generating a list of steps, and a list
of steps is a `for` loop in a function node against a page of copy-paste in an
automation.

```javascript
for (let i = 0; i < 48 / 4; i++) {
    const head = (i * 4) % 48;
    const tail = (head - 4 + 48) % 48;
    const gone = (head - 8 + 96) % 48;
    steps.push({ seconds: 0.2, segments: [
        { start: gone, length: 4, ring: 0, rings_tall: 4, color: 'black' },
        { start: tail, length: 4, ring: 0, rings_tall: 4, color: 'royal_blue' },
        { start: head, length: 4, ring: 0, rings_tall: 4, color: 'white' },
    ]});
}
```

The black segment is the whole trick. Anything drawn stays on screen after its
step ends, so without it you get a ring slowly filling up rather than a comet
going round. Both are useful — know which one you are building.

The second half of the flow shows an `effect` step, which is a different animal:
`pulse`, `wave` and `light_flash` do not draw anything themselves, they modulate
an area **already drawn in the same scene**. The fill has to come first.

## Waiting for the clock to be free

`binary_sensor.<name>_busy` is true while a notice or scene is playing. The
clock reports this itself and pushes every change, so it is something to wait
on rather than guess at -- a notice sent while another one plays is not queued,
it is simply lost.

The usual shape is a **current state** node checking the sensor is `off`
before the call service node, with a short delay and a retry when it is not.
`notice-queue.json` is that shape, ready to import. Its attributes carry
`digital_clock` and the raw byte, if you want to know whether the digital time
is on screen.

## Sound

Sound only plays if the clock is not muted. There is a **Mute** switch on the
device page, and it is easy to forget: a muted clock plays nothing and reports
no error, which looks exactly like a broken sound argument.

## Errors

Bad values now fail loudly. A colour name that does not exist raises and shows
up in Node-RED as a failed service call rather than doing nothing at all. The
message lists the whole palette.

The palette has no plain `green`, `purple`, `orange` or `cyan`, but those names
are accepted as aliases for the nearest real colour. See the colour list in
`custom_components/glance_clock/const.py`.
