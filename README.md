[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Yamaha Soundbar

Home Assistant custom integration for Yamaha soundbars based on Linkplay A118.

Tested on Yamaha YAS-109 & YAS-209. Compatible models: ATS-1090, ATS-2090, SR-X40A, SR-X50A, ATS-X500. If your model works (or doesn't), please open an issue on GitHub.

## Features

- **Config Flow** — full UI-based setup, no YAML required
- **Options Flow** — configure sources, volume step, and other parameters after setup
- **Media Player** — playback control, source selection, sound mode selection
- **Switches** — Clear Voice, 3D Surround, Bass Extension, Power, Mute
- **Numbers** — Volume (0–100), Subwoofer Volume (-12–12)
- **Diagnostics** — sensor with firmware version, MCU version, WiFi info, and all Yamaha sound parameters
- **Sound Modes** — music, sports, tv program, game, movie, stereo
- **Sources** — TV (optical), Bluetooth, HDMI, NET (WiFi), and custom source mapping
- **Multiroom** — grouping/ungrouping devices
- **TTS & Announcements** — snapshot/restore for seamless TTS playback
- **Services** — `sound_settings`, `join`, `unjoin`, `preset`, `snapshot`, `restore`, and more

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=osk2&repository=yamaha-soundbar&category=integration)

#### Using HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Install **Yamaha Soundbar**
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration → Yamaha Soundbar**
5. Enter the IP address of your soundbar

#### Manual installation

1. Copy all files from `custom_components/yamaha_soundbar` to `<config>/custom_components/yamaha_soundbar/`
2. Restart Home Assistant
3. Add the integration via UI as described above

## Configuration

After adding the integration, all configuration is done through the UI.

Go to **Settings → Devices & Services → Yamaha Soundbar → Configure** to set:

| Option | Description | Default |
|--------|-------------|---------|
| Sources | Custom source name mapping (e.g. `optical: TV`) | Built-in defaults |
| Common sources | Additional sources shared across devices | — |
| Source ignore | Sources to hide from the UI | — |
| Volume step | Volume increment for up/down buttons | 5 |
| Announce volume increase | Extra volume for TTS announcements | 15 |
| Icecast metadata | Metadata mode for internet radio | StationName |
| Multiroom WiFi Direct | Use WiFi Direct for multiroom | false |
| LED off | Turn off device LED | false |
| Last.fm API key | For album art metadata | — |

## Entities

After setup, the following entities are created for your soundbar:

### Media Player
The primary entity with playback controls, source/sound mode selection, volume, and grouping.

### Switches
| Entity | Description |
|--------|-------------|
| Clear Voice | Enhance voice clarity |
| 3D Surround | Virtual surround sound |
| Bass Extension | Extended bass response |
| Power | Power on/off the soundbar (via power saving mode) |
| Mute | Mute/unmute audio output |

### Numbers
| Entity | Range | Description |
|--------|-------|-------------|
| Volume | 0–100 | Main volume level |
| Subwoofer Volume | -12–12 | Subwoofer level adjustment |

### Diagnostics
A diagnostic sensor showing firmware/MCU version with attributes including host, UUID, WiFi channel, SSID, player mode/status, and all Yamaha sound parameters.

## Services

### `yamaha_soundbar.sound_settings`

Set one or more sound options in a single call.

```yaml
action: yamaha_soundbar.sound_settings
data:
  entity_id: media_player.my_sound_bar
  sound_program: movie
  clear_voice: true
  surround: true
  subwoofer_volume: 2
```

Available fields: `sound_program`, `subwoofer_volume` (int), `surround` (bool), `clear_voice` (bool), `bass_extension` (bool), `mute` (bool), `power_saving` (bool).

### Other services

| Service | Description |
|---------|-------------|
| `yamaha_soundbar.join` | Join a multiroom group |
| `yamaha_soundbar.unjoin` | Leave a multiroom group |
| `yamaha_soundbar.preset` | Play a saved preset |
| `yamaha_soundbar.snapshot` | Save current playback state |
| `yamaha_soundbar.restore` | Restore saved playback state |
| `yamaha_soundbar.command` | Send a raw command to the device |

## Upgrading from version 3.1.x (YAML-based)

1. Remove the `media_player: - platform: yamaha_soundbar` block from `configuration.yaml`
2. If upgrading from the old `linkplay` integration, remove `/custom_components/linkplay/`
3. Restart Home Assistant
4. Add the integration via UI: **Settings → Devices & Services → Add Integration → Yamaha Soundbar**

## License

This project is licensed under MIT license. See [LICENSE](LICENSE) file for details.
