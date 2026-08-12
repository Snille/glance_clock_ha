# Examples

Working examples for the Glance Clock integration, in the two forms people
actually drive it from.

```
examples/
├── yaml/                  Home Assistant
│   ├── automations/       12 automations, one per file
│   ├── scripts/           a queued notice entry point
│   └── scenes/            7 service calls to run from Developer Tools
└── node-red/              5 flows, importable
```

| Directory | Start here |
|---|---|
| [`yaml/`](yaml/) | [`yaml/README.md`](yaml/README.md) — what each file does and where to paste it |
| [`node-red/`](node-red/) | [`node-red/README.md`](node-red/README.md) — the flows, and what Node-RED is better at |

The reference material lives one level up: **[SCENES.md](../SCENES.md)** for the
ring geometry, the fixed colour palette and the scene model, **[ICONS.md](../ICONS.md)**
for the built-in glyphs, and the **[README](../README.md)** for every service and
its parameters.

## Where to start

**You want the clock to say something.** `yaml/automations/doorbell.yaml`, then
`yaml/scripts/glance-say.yaml` once you have more than two of them.

**You want the clock to show something.** `yaml/scenes/gauge-with-track.yaml` to
see it work, then `yaml/automations/progress-ring.yaml` to point it at a real
sensor.

**You want to build your own animation.** `yaml/scenes/ring-fill.yaml` and
`yaml/scenes/comet.yaml`, in that order — the second is the first plus one black
segment, and that difference is the whole idea.

**You already live in Node-RED.** `node-red/README.md`. Everything is a Home
Assistant service call, so no custom node and no Bluetooth connection of its own
is needed.

## YAML or Node-RED?

They reach exactly the same services, so it is a question of what you already
run. One real difference: **a scene is a timeline you upload in one call**, so
building an animation means generating a list of steps. That is a `for` loop in
a Node-RED function node against a page of copy-paste in YAML — compare
[`yaml/scenes/comet.yaml`](yaml/scenes/comet.yaml) with
[`node-red/comet.json`](node-red/comet.json), which produce the same thing.

Templates close some of that gap in YAML, and `yaml/automations/progress-ring.yaml`
and `electricity-price.yaml` show how far they get.

## Before anything works

Two things catch everyone once:

**A notice sent while another one is playing is lost** — not queued. Wait on
`binary_sensor.<name>_busy`, which the clock reports itself. Both
`yaml/scripts/glance-say.yaml` and `node-red/notice-queue.json` are that wait,
packaged.

**Sound needs the clock unmuted.** A muted clock plays nothing and reports no
error, which looks exactly like a bad sound name. There is a Mute switch on the
device page.

## Slots

Scenes live in one of eight slots and stay there until cleared. Slot 0 belongs
to the animation buttons on the device page and slot 1 to `send_forecast`, so
these examples use 2 and up:

| Slot | Used by |
|---|---|
| 0 | The device page's animation buttons |
| 1 | `send_forecast` |
| 2 | `weather-particles.yaml`, `node-red/weather.json` |
| 3 | The scene examples, `progress-ring` |
| 4 | `workday-band.yaml` |
| 5 | `electricity-price.yaml` |
| 6 | `water-leak.yaml` |
| 7 | Free |

Two things sharing a slot means whichever arrives second wins, so if you run
several of these at once, give each one its own number.
