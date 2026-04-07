# light_bot

Offline voice-controlled light switch for Philips Hue (or any Hue-compatible bridge). Listens on a USB microphone using the [Vosk](https://alphacephei.com/vosk/) Chinese speech recognition model, and toggles configured lights when it hears your custom on/off keywords.

Runs fully on-device — no cloud, no network speech APIs.

## How it works

- `audio.py` — captures audio from a USB mic via `sounddevice` and downsamples to 16 kHz
- `recognizer.py` — feeds audio to a Vosk recognizer with a fixed grammar (your two keywords + `[unk]` to absorb background speech)
- `light_control.py` — sends `PUT` requests to the Hue bridge to switch lights on/off
- `light_bot.py` — main loop tying it all together

## Installation

```bash
./install.sh
```

This installs system audio dependencies, creates a venv, downloads the Vosk Chinese model, copies `config.yaml.example` to `config.yaml`, and installs a systemd service.

Then edit `config.yaml`:

- `command_on` / `command_off` — your wake keywords
- `light_base_url` — your Hue bridge URL with API token (`%s` is replaced by light ID)
- `light_ids` — list of light IDs to control
- `device_name` — substring of your mic name (e.g. `"USB"`)

Start the service:

```bash
sudo systemctl start light-bot
journalctl -u light-bot -f
```

To remove: `./uninstall.sh`

## Requirements

- Linux with `systemd`
- Python 3
- A USB microphone
- A Hue bridge (or compatible) reachable on the LAN
