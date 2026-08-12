# Glance Clock Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Snille/glance_clock_ha.svg)](https://github.com/Snille/glance_clock_ha/releases)
[![License](https://img.shields.io/github/license/Snille/glance_clock_ha.svg)](LICENSE)

Home Assistant custom integration for Glance Clock devices via Bluetooth.

> **This is a fork of [PorlyBe/glance_clock_ha](https://github.com/PorlyBe/glance_clock_ha)**
> with a good deal added and several things fixed, all tested against a real
> clock. See [HISTORY.md](./HISTORY.md) for what changed and why.
>
> Glance Clock's manufacturer is gone and the servers with it, so a clock on the
> wall has nothing left to talk to. This integration is how it gets used again.

📖 **[SCENES.md](./SCENES.md)** — the rings, the fixed colour palette, and how to
build your own animations · **[examples/](./examples/)** — automations, scripts,
scenes and Node-RED flows, ready to copy · **[ICONS.md](./ICONS.md)** — the
built-in glyphs

<!-- [IMAGE: Banner image showing the Glance Clock device] -->

## Features

- 🔔 **Notifications** - Custom messages with animations and sounds
- 💍 **The LED rings** - Four rings of 48 addressable pixels, drivable directly
- 🎬 **Scenes** - Upload a timeline the clock plays itself at 50 frames per second
- ✨ **Effects** - Pulse, wave and light flash, all confirmed on hardware
- 🔥 **Firmware animations** - Fire, wheel, flower, fan, sun, thunderstorm, cloud, sweep
- 🌨️ **Weather particles** - Snow, rain and fog drawn on the rings
- 🕐 **Hand calibration** - From the device page, no app required
- 🔊 **Sound** - All eighteen, auditionable from the interface
- 💡 **Brightness** - Automatic or manual, without destroying the clock's own state
- 🌙 **Do not disturb** - The recurring quiet window, readable and settable
- 🛠️ **Raw access** - Send any command frame, read any characteristic
- 🔗 **Bluetooth Native** - Uses Home Assistant's built-in Bluetooth integration

<!-- [IMAGE: Screenshot of the integration in Home Assistant UI] -->


## Prerequisites

⚠️ **Important:** Before using this integration, you must:


1. Reset your Glance Clock to factory settings
2. (Optional) Update the firmware
3. Synchronize the time using the [bluetooth-cts Home Assistant add-on](https://github.com/PorlyBe/bluetooth-cts)
4. Pair with your system's Bluetooth

### Step 1: Factory Reset Your Glance Clock

Before setup, perform a complete factory reset on your Glance Clock. This ensures a clean state for pairing and configuration.

**To reset your Glance Clock:**

Hold the reset button + Power button. Let go of the reset button and keep holding the Power button until the LED blinking pattern changes. Then release it as well.

NOTE: this will also reset the firmware back to the factory version.



### Step 2: (Optional) Update Firmware

If you wish to update your Glance Clock's firmware, you can use the nRF Connect app to perform a Device Firmware Update (DFU):

#### Download nRF Connect

- **Android**: [nRF Connect on Google Play](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp)
- **iOS**: [nRF Connect on App Store](https://apps.apple.com/us/app/nrf-connect-for-mobile/id1054362403)

#### Update Firmware Steps

1. Download the latest firmware from the [`/firmware`](firmware/) directory in this repository.
2. Open the nRF Connect app on your phone.
3. Go to the **Scanner** tab and find your Glance Clock in the device list.
4. Tap **Connect** to connect to your Glance Clock.
5. Tap the **DFU** icon (circular arrows) in the top right corner.
6. Select **Distribution packet (ZIP)** when prompted.
7. Browse and select the firmware ZIP file you downloaded.
8. Tap **Start** to begin the update. Wait for the update to complete (do not disconnect). The clock will restart automatically when finished.

For more details, see the [original instructions](https://github.com/Hypfer/glance-clock).

### Step 3: Add Bluetooth CTS Home Assistant Add-on

The Glance Clock requires time synchronization before use. This can now be done easily using the [bluetooth-cts Home Assistant add-on](https://github.com/PorlyBe/bluetooth-cts), which provides a GATT Current Time Service (CTS) server for your clock to sync with.

**To set the time:**

1. Install the [bluetooth-cts add-on](https://github.com/PorlyBe/bluetooth-cts) in Home Assistant (follow the instructions in that repository).
2. Start the add-on so it advertises the Current Time Service (CTS) over Bluetooth.
3. Once your Glance Clock is connected in the next step, the time will automatically sync.
4. Leave the add-on running to keep your clock in sync with Home Assistant time.

### Step 4: Pair Your Glance Clock with Home Assistant

After resetting and setting the time, pair the clock with Home Assistant.

Open a terminal in Home Assistant (Settings → System → Terminal) and run:

```bash
bluetoothctl
agent on
default-agent
scan on
```

Wait until you see your Glance Clock appear (look for "Glance" in the name). Note the MAC address (format: `XX:XX:XX:XX:XX:XX`), then:

```bash
pair XX:XX:XX:XX:XX:XX
```

Replace `XX:XX:XX:XX:XX:XX` with your actual MAC address. When prompted, enter the PIN shown on the Glance Clock display, then exit:

```bash
exit
```

Your Glance Clock is now paired and ready to add to Home Assistant.

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the repository URL: `https://github.com/PorlyBe/glance_clock_ha`
6. Select category "Integration"
7. Click "Add"
8. Find "Glance Clock" in the integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/PorlyBe/glance_clock_ha/releases)
2. Extract the `glance_clock` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

After pairing your Glance Clock, Home Assistant will automatically discover it.

1. Go to **Settings** → **Devices & Services**
2. You should see a "Discovered" notification for your Glance Clock
3. Click **Configure** on the discovered device
4. Follow the prompts to complete setup

If the device doesn't appear automatically, you can manually add it:
1. Click **Add Integration**
2. Search for "Glance Clock"
3. Select your Glance Clock from the list of discovered devices
4. Click **Submit**

<!-- [IMAGE: Configuration flow screenshot] -->

## Entities

Once configured, the integration provides:

- **Light** - Control brightness and power state
- **Switches** - Digital Clock, Night Mode, Always Show Points, Mute
- **Selects** - Date Format options
- **Numbers** - DND Start and DND End, the recurring quiet window stored on the clock
- **Buttons** - Calibrate Hands, Confirm Hand Positions at 12, Animation Run, Animation Stop,
  and **Clear All Scenes**, which empties all eight slots. A scene replays until something
  clears it, so this is the way back when you no longer have the call that started it
- **Animation controls** - Animation, Animation Colour, Animation Speed and **Animation
  Slot**, driving Animation Run. The Animation select carries the firmware animations *and*
  the three effects, so `pulse`, `wave` and `light_flash` need no YAML either. Animation
  Slot picks which of the eight slots Run writes to, so several animations can be parked at
  once; Animation Stop clears whichever slot is selected
- **Sound controls** - a Sound select and a Sound Play button for auditioning the eighteen sounds
- **Sensors** - Battery level, and Last Notification showing anything the clock pushes on its own
- **Binary sensors**
  - **Busy**, true while a notice or scene is playing. The clock reports this itself, so
    it is something to wait on rather than guess at
  - **Do Not Disturb**, true while the quiet window is in force. Also the clock's own
    answer, pushed the moment it changes, with the mute flag carried alongside as an
    attribute. Setting the DND schedule says when the clock *should* be quiet; this says
    whether it is quiet *now*, which is what an automation needs before deciding a notice
    is worth sending
- **Notify** - a notify entity, so the clock can be a target like any phone. Use
  `notify.send_message`; the settings ride in the message as markers, see below


## Using Icons in Notifications

You can include icons in your Glance Clock notifications by inserting special codes in your message text. To add an icon, use `[icon:CODE]` in your message (for example: `Wake up! [icon:128]`).

See the full list of available icon codes and their meanings in [ICONS.md](./ICONS.md).

## Services

### Send Notification

Send a custom notification to your Glance Clock.

**Service:** `glance_clock.send_notice`

> Note for anyone upgrading: this README used to document a `notify.glance_clock`
> service, which never existed -- the platform registered no entity. Since 1.27.0
> there **is** a notify entity, but it is the modern kind: target it with
> `notify.send_message`, not `notify.glance_clock`.

```yaml
action: glance_clock.send_notice
data:
  text: "Meeting in 5 minutes!"
  animation: "pulse"
  sound: "bells"
  color: "blue"
  priority: "high"
```

**Parameters:**

- `text` (required): Notification text
- `animation`: One of 23 — `none`, `pulse`, `wave`, `fire`, `wheel`, `flower`, `flower2`,
  `fan`, `sun`, `thunderstorm`, `cloud`, and twelve `weather_*` icons
- `sound`: One of 18 — see the Sound select on the device page to audition them
- `color`: Any of the 25 palette colours, listed in [SCENES.md](./SCENES.md#the-colour-palette)
- `priority`: `low`, `medium`, `high`, `highest`, `critical`
- `text_modifier`: Text effect (none, repeat, rapid, delay)

A name outside those lists raises and says what would have worked, rather than
quietly sending white, silence or a pulse. Raw indices are still accepted.

### Notify entity

The clock is also a notify target, for the automations that were written for
everything rather than for the clock:

```yaml
action: notify.send_message
target:
  entity_id: notify.glance_clock      # your clock's own name
data:
  title: "Posten"
  message: "PAKET HAR KOMMIT [sound:bells] [anim:pulse] [color:dark_orange]"
```

`notify.send_message` carries a message and a title and nothing else, which is
the right shape for a phone and a poor fit for a clock. So the settings ride in
the message, in the same bracket idiom the display text already uses for
`[icon:130]`:

| Marker | Sets | Also spelled |
|---|---|---|
| `[sound:bells]` | The sound | |
| `[anim:pulse]` | The animation | `[animation:...]`, `[effect:...]` |
| `[color:red]` | The colour | `[colour:...]` |
| `[priority:high]` | The priority | |

Markers are removed from the text; anything unrecognised is left in it, so a
message that merely looks like a marker still arrives whole. `title` stays a
title and is put in front of the message -- it is deliberately *not* overloaded
to mean one of the settings, because a generic sender will eventually put a real
title there.

For everything the firmware can do, use `glance_clock.send_notice` above. This
entity is the lowest common denominator on purpose.

### Update Display Settings

Configure display settings on your Glance Clock.

**Service:** `glance_clock.update_display_settings`

```yaml
service: glance_clock.update_display_settings
data:
  nightModeEnabled: true
  displayBrightness: 128
  timeModeEnable: true
  timeFormat12: false
  dateFormat: 1
```

### Send Weather Forecast

Send weather forecast data with color gradients.

**Service:** `glance_clock.send_forecast`

```yaml
service: glance_clock.send_forecast
data:
  weather_entity: weather.home
  max_color: "#FF0000"
  min_color: "#0000FF"
```

### Set LEDs

Lights areas of the four LED rings. Each ring has 48 pixels, pixel 0 is at twelve
o'clock and numbering runs clockwise. Ring 0 is the outermost.

```yaml
action: glance_clock.set_leds
data:
  mode: watchface
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

`mode` decides how the scene shares the display: `watchface` draws it alongside the
digital time, `exclusive` hides the digital clockface, and `ring_and_text` alternates
between the two. Colours are names from the clock's fixed palette -- there is no
arbitrary RGB. The full palette, the ring geometry and a set of worked examples are
in [SCENES.md](./SCENES.md).

### Set Scene

Uploads a timed sequence of fills that the clock plays itself at 50 frames per second.
This is how to build your own animations: one call carries the whole timeline.

```yaml
action: glance_clock.set_scene
data:
  steps:
    - seconds: 0.5
      segments:
        - { start: 0, length: 6, ring: 0, rings_tall: 4, color: red }
    - seconds: 0.5
      segments:
        - { start: 0, length: 6, ring: 0, rings_tall: 4, color: black }
        - { start: 6, length: 6, ring: 0, rings_tall: 4, color: red }
```

Steps take a `type`. `fill` is the default; the others reach the rest of what a scene
can hold:

```yaml
- type: effect          # pulse | wave | light_flash, layered onto what is already drawn
  effect: pulse
  rise: 20
  fall: 80
  segments: [{ start: 0, length: 12, rings_tall: 4, color: royal_blue }]
  seconds: 3
- type: weather         # snow | rain | fog -- a particle effect, not a forecast
  condition: snow
  position: full        # full | upper | lower
  intensity: 8
  seconds: 15
- type: text            # stays on screen, unlike a notice
  text: "Ute: -3[icon:176]C"
- type: sound           # a cue at a point on the timeline
  sound: bells
```

A step without `at` follows on from the previous one, so a simple sequence needs only
durations. Two things to design around:

- **Fills persist.** Anything drawn stays after its step ends, so paint black over what
  should disappear -- that is what makes a block move instead of a ring fill up.
- **The clock restarts the scene on its own ~15 second cycle.** A timeline shorter than
  roughly 750 frames will run, finish, and visibly wait before repeating.

### Set Animation

Runs one of the animations built into the clock's firmware.

```yaml
action: glance_clock.set_animation
data:
  animation: fire
  color: red
  speed: 3
```

Available: `fire`, `wheel`, `flower`, `flower2`, `fan`, `sun`, `thunderstorm`, `cloud`,
and `sweep`. They are single-colour patterns tinted by `color` -- picking black renders
nothing. Only `sweep` has a direction; a negative `speed` runs it anticlockwise.

A scene or animation appears as soon as it is sent: the integration asks the clock to
start playback straight after the write, which brings it up at once. What still separates
the two is not speed but shape -- a notice interrupts and hands the display back, a scene
joins what is there and stays until its slot is cleared.

### Clear LEDs

```yaml
action: glance_clock.clear_leds
data:
  slot: 0
```

### Removing the forecast again

`send_forecast` writes to **scene slot 1**, and a scene stays in its slot and replays
until something clears it. So the forecast comes off the clock with:

```yaml
action: glance_clock.clear_leds
data:
  slot: 1
```

Worth keeping the slots straight: slot 0 is what the animation buttons on the device page
use, and slot 1 belongs to the forecast. Two things sharing a slot means whichever
arrives second wins.

The degree symbol follows Home Assistant's own units. The forecast values are already
converted by the time they reach the integration, so only the letter changes -- °C or °F,
taken from the weather entity, falling back to the system setting.

### Send Command

Sends a raw command frame. The firmware understands more than this integration models,
and this is how to reach the rest of it -- useful commands include 30 and 31 (stop and
start scene playback), 35 (update and refresh) and 61 and 60 (start and stop the
brightness scene, which puts "Auto" on the display).

Commands 42 and 50 are refused. They unpair the clock, which has no pairing button to
recover with, and wipe user data the manufacturer's servers can no longer restore.

```yaml
action: glance_clock.send_command
data:
  command: 31
  modifiers: [0, 0, 0]   # optional, padded with zeroes
  payload: "20 01"       # optional, hex or a list of bytes
```

### Read Characteristic

Reads one of the clock's GATT characteristics and returns the bytes as a service
response, rather than logging them where they may not be retrievable.

Pass `list` instead of a name to enumerate every service and characteristic with the
properties each supports.

```yaml
action: glance_clock.read_characteristic
data:
  characteristic: scene_state    # settings, scene_data, scene_state, list, or a UUID
```

### Set DND Schedule

Sets the recurring Do Not Disturb window the clock applies itself. This is stored on the
device and keeps working while Home Assistant is down. It is separate from the permanent
DND flag.

```yaml
action: glance_clock.set_dnd_schedule
data:
  from_hour: 21
  till_hour: 7
  recurring: true
```

`from_hour` and `till_hour` are hours, 0-23. The end may be earlier than the start, to
span midnight. The same window is available as the **DND Start** and **DND End** number
entities on the device page.

### Read DND Schedule

Writes the window currently stored on the clock to the Home Assistant log.

```yaml
action: glance_clock.read_dnd_schedule
```

### Read Current Settings

Retrieve current device settings.

**Service:** `glance_clock.read_current_settings`

### Refresh Entities

Force refresh all entity states.

**Service:** `glance_clock.refresh_entities`

## Automations

A dozen worked automations -- doorbell, washing machine, progress rings,
electricity price, weather particles, and the patterns behind them -- are in
**[examples/yaml/](./examples/yaml/)**, one per file. One to start with:

### Weather Forecast Automation

Automatically update your Glance Clock with weather forecast data whenever it changes.

1. Go to **Settings** → **Automations & Scenes**
2. Click **Create Automation** → **Create new automation**
3. Click the three dots (⋮) and select **Edit in YAML**
4. Paste the following configuration:

```yaml
alias: Weather Update
description: Update Glance Clock with weather forecast
triggers:
  - trigger: state
    entity_id:
      - weather.forecast_home  # Replace with your weather entity
conditions: []
actions:
  - action: glance_clock.send_forecast
    data:
      weather_entity: weather.forecast_home  # Replace with your weather entity
      max_color: [255, 102, 0]    # Orange for hot temperatures
      min_color: [0, 120, 255]    # Blue for cold temperatures
      min_value: 0                # Minimum temperature scale (°C)
      max_value: 40               # Maximum temperature scale (°C)
  - action: glance_clock.send_notice
    data:
      text: Weather Updated
      animation: sun
      sound: none
      color: blue
      priority: medium
mode: single
```

5. Update `weather.forecast_home` to match your weather entity
6. Adjust `min_value` and `max_value` to suit your local temperature range
7. Click **Save** and give your automation a name

The clock will now automatically display a 24-hour temperature forecast with color gradients whenever the weather updates!

## Troubleshooting

### Integration won't add or connect

- Ensure your Glance Clock is **paired** with your system via Bluetooth (see Prerequisites)
- Verify the MAC address is correct (use `bluetoothctl devices` to list paired devices)
- Check that Home Assistant's Bluetooth integration is enabled and working
- Restart Home Assistant and try again

### Device shows as unavailable

- The Glance Clock may have gone to sleep or moved out of range
- Check Bluetooth adapter signal strength
- Re-pair the device if connection issues persist

### Notifications not appearing

- Ensure the Glance Clock is powered on and connected
- Check that the message text is not empty
- Try sending a simple notification without optional parameters

### Battery sensor shows unavailable

- Some Glance Clock models may not support battery reporting via Bluetooth
- Battery data updates periodically, not in real-time

## Driving it from Node-RED

Everything is a Home Assistant service call, so Node-RED needs no special node.
There are five worked flows in [`examples/node-red/`](./examples/node-red/) --
weather on the rings, an espresso machine announcing itself when it comes up to
temperature, any sensor as a progress arc, a queue that stops notices being
lost, and a scene generated in code -- along with the handful of things worth
knowing before you start.

Three of those are worth repeating here, because each one looks like a bug the
first time:

**A scene stays in its slot.** It does not disappear when its lifetime ends; it
stays and replays until the slot is cleared with `clear_leds`.

**A notice empties the slot.** It does not borrow the display and give it back --
after a notice the scene is gone, and no playback command restores it. To show
text without losing what is on the rings, put a `text` step in the scene instead
of sending a notice.

**A notice interrupts, a scene joins.** Both arrive at once. The difference is
what happens next: a notice takes the display and gives it back, a scene sits
alongside the time until something clears it.

**Sound needs the clock unmuted.** A muted clock plays nothing and reports no
error, which looks exactly like a bad sound name. There is a Mute switch on the
device page.

## What the clock will not do

Recorded so it does not get investigated twice:

- **The ambient light sensor is not readable.** The clock measures light and sets
  its own brightness from it, but no characteristic exposes the value. Fifteen
  samples over two minutes with a lamp on the sensor, with `brightnessSceneStart`
  active and the clock in automatic mode, were byte-identical.
- **The button is not a trigger.** A short press shows a status message on the
  clock and pushes nothing over Bluetooth. The clock does notify on connect and
  on power state, which is what the Last Notification sensor shows.

## Credits

This integration uses protocol and implementation insights from [Hypfer's Glance Clock project](https://github.com/Hypfer/glance-clock). Special thanks to the original developers for documenting the Glance Clock protocol and providing a foundation for Bluetooth communication.

## Support

- [Report Issues](https://github.com/Snille/glance_clock_ha/issues)
- [Upstream project](https://github.com/PorlyBe/glance_clock_ha) this is forked from

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
