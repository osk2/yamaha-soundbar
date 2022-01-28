# Linkplay-based speakers and sound devices

This component allows you to integrate control of audio devices based on Linkplay chipset into your [Home Assistant](http://www.home-assistant.io) smart home system. Originally developed by nicjo814, maintained by limych. This version mostly rewritten by nagyrobi. Read more about Linkplay at the bottom of this file.

Fully compatible with [Mini Media Player card for Lovelace UI](https://github.com/kalkih/mini-media-player) by kalkih, including speaker group management.

## Installation
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
* Install using HACS, or manually: copy all files in `custom_components/linkplay` to your `<config directory>/custom_components/linkplay/` directory.
* Restart Home-Assistant.
* Add the configuration to your configuration.yaml.
* Restart Home-Assistant again.

[Support forum](https://community.home-assistant.io/t/linkplay-integration/33878/133)

### Configuration

It is recommended to create static DHCP leases in your network router to ensure the devices always get the same IP address. Recent firmware versions allow setting static IP address, if you see that option, use it.

To add Linkplay units to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
media_player:
    - platform: linkplay
      host: 192.168.1.11
      name: Sound Room1
      volume_step: 10
      icecast_metadata: 'StationNameSongTitle'
      multiroom_wifidirect: False
      sources: 
        {
          'optical': 'TV sound', 
          'line-in': 'Radio tuner', 
          'bluetooth': 'Bluetooth',
          'udisk': 'USB stick',
          'http://94.199.183.186:8000/jazzy-soul.mp3': 'Jazzy Soul',
        }

    - platform: linkplay
      host: 192.168.1.12
      name: Sound Room2
      icecast_metadata: 'Off'  # valid values: 'Off', 'StationName', 'StationNameSongTitle'
      sources: {}
      common_sources: !include linkplay-radio-sources.yaml
```

### Configuration Variables

**host:**  
  *(string)* *(Required)* The IP address of the Linkplay unit.

**name:**  
  *(string)* *(Required)* Name that Home Assistant will generate the `entity_id` based on. It is also the base of the friendly name seen in Lovelace UI, but will be overriden by the device name set in the Android app.

**volume_step:**  
  *(integer)* *(Optional)* Step size in percent to change volume when calling `volume_up` or `volume_down` service against the media player. Defaults to `5`, can be a number between `1` and `25`. 

**sources:**  
  *(list)* *(Optional)* A list with available source inputs on the device. If not specified, the integration will assume that all the supported source input types are present on it:
```yaml
'bluetooth': 'Bluetooth', 
'line-in': 'Line-in', 
'line-in2': 'Line-in 2', 
'optical': 'Optical', 
'co-axial': 'Coaxial', 
'HDMI': 'HDMI', 
'udisk': 'USB disk', 
'TFcard': 'SD card', 
'RCA': 'RCA', 
'XLR': 'XLR', 
'FM': 'FM', 
'cd': 'CD'
```
The sources can be renamed to your preference (change only the part _after_ **:** ). You can also specify http-based (Icecast / Shoutcast) internet radio streams as input sources:
```yaml
'http://1.2.3.4:8000/your_radio': 'Your Radio',
'http://icecast.streamserver.tld/mountpoint.aac': 'Another radio'
```
If you don't want a source selector to be available at all, set option to empty: `sources: {}`.

**common_sources:**  
  *(list)* *(Optional)* Another list with sources which should appear on the device. Useful if you have multiple devices on the network and you'd like to maintain a common list of http-based internet radio stream sources for all of them in a single file with `!include linkplay-radio-sources.yaml`. The included file should be in the same place as the main config file containing `linkplay` platform.   
  For example:
```yaml
{
  'http://1.2.3.4:8000/your_radio': 'Your Radio',
  'http://icecast.streamserver.tld/mountpoint.aac': 'Another radio'
}
```

**icecast_metadata:**  
  *(string)* *(Optional)* When playing icecast webradio streams, how to handle metadata. Valid values here are `'Off'`, `'StationName'`, `'StationNameSongTitle'`, defaulting to `'StationName'` when not set. With `'Off'`, Home Assistant will not try do request any metadata from the IceCast server. With `'StationName'`, Home Assistant will request only once when starting the playback the stream name from the headers, and display it in the `media_title` property of the player. With `'StationNameSongTitle'` Home Assistant will request the stream server periodically for icy-metadata, and read out `StreamTitle`, trying to figure out correct values for `media_title` and `media_artist`, in order to gather cover art information from LastFM service (see below). Note that metadata retrieval success depends on how the icecast radio station servers and encoders are configured, if they don't provide proper infos or they don't display correctly, it's better to turn it off or just use StationName to save server load. There's no standard way enforced on the servers, it's up to the server maintainers how it works.

**lastfm_api_key:**  
  *(string)* *(Optional)* API key to LastFM service to get album covers. Register for one.

**multiroom_wifidirect:**  
  *(boolean)* *(Optional)* Set to `True` to override the default router mode used by the component with wifi-direct connection mode (more details below).

**led_off:**  
  *(boolean)* *(Optional)* Set to `True` to turn off the LED on the front panel of the Arylic devices (works only for this brand).


## Multiroom

Linkplay devices support multiroom in two modes:
- WiFi direct mode, where the master turns into a hidden AP and the slaves connect directly to it. The advantage is that this is a dedicated direct connection between the speakers, with network parameters optimized by the factory for streaming. Disadvantage is that switching of the stream is slower, plus the coverage can be limited due to the building's specifics. _This is the default method used by the Android app to create multirooms._
- Router mode, where the master and slaves connect to each other through the local network (from firmware `v4.2.8020` up). The advantage is that all speakers remain connected to the existing network, swicthing the stream happens faster, and the coverage can be bigger being ensured by the network infrastructure of the building (works through multiple interconnected APs and switches). Disadvantage is that the network is not dedicated and it's the user responsibility to provide proper network infrastructure for reliable streaming. _This only works through this component and it's the preferred mode._

This integration will autodetect the firmware version running on the player and choose multiroom mode accordingly. Units with firmware version lower than `v4.2.8020` can connect to multirooms _only in wifi-direct mode_. Firmware version number can be seen in device attributes. If the user has a mix of players running old and new firmware, autodetection can be overriden with option `multiroom_wifidirect: True`, and is needed only for units with newer versions, to force them down to wifi-direct multiroom.

To create a multiroom group, connect `media_player.sound_room2` (slave) to `media_player.sound_room1` (master):
```yaml
    - service: linkplay.join
      data:
        entity_id: media_player.sound_room2
        master: media_player.sound_room1
```
To exit from the multiroom group, use the entity ids of the players that need to be unjoined. If this is the entity of a master, all slaves will be disconnected:
```yaml
    - service: linkplay.unjoin
      data:
        entity_id: media_player.sound_room1
```
These services are compatible out of the box with the speaker group object in @kalkih's [Mini Media Player](https://github.com/kalkih/mini-media-player) card for Lovelace UI.

Since v2.0.37 of this component it's also possible to use Home Assistant's [standard multiroom](https://www.home-assistant.io/integrations/media_player/#service-media_playerjoin) join and unjoin functions for multiroom control.

*Tip*: if you experience temporary `Unavailable` status on the slaves afer unjoining from a multiroom group in router mode, run once the Linkplay-specific command `RouterMultiroomEnable` - see details further down.

## Presets

Linkplay devices allow to save, using the control app on the phone/tablet, music presets (for example Spotify playlists) to be recalled for later listening. Recalling a preset from Home Assistant:
```yaml
    - service: linkplay.preset
      data:
        entity_id: media_player.sound_room1
        preset: 1
```
Preset count vary from device type to type, usually the phone app shows how many presets can be stored maximum. The integration detects the max number and the command only accepts numbers from the allowed range. You can specify multiple entity ids separated by comma or use `all` to run the service against.

## Snapshot and restore

To prepare the player to play TTS and save the current state of it for restoring afterwards, current playback will stop:
```yaml
    - service: linkplay.snapshot
      data:
        entity_id: media_player.sound_room1
```
To restore the player state:
```yaml
    - service: linkplay.restore
      data:
        entity_id: media_player.sound_room1
```
You can specify multiple entity ids separated by comma or use `all` to run the service against. Currently the following state is being snapshotted/restored:
- Volume
- Input source
- Webradio stream (as long as it's configured as an input source)
- USB audio files playback (track will restart from the beginning)
- Spotify (snapshot will use the device's highest preset number to store and recall the current playlist, playback may restart the same track or not, depends on Spotify settings. You should manually store a preset first with the app).

## Media Browser

For devices with an USB port, make sure that in the sources configuration you have specified a `udisk` entry. Plug in a USB stick with MP3s on it, and switch to that source in Home Assistant (some models switch to USB automatically as soon as you connect a USB drive). The Media Browser will populate with the list of files present on the stick, clicking a file will start playing it.

## Specific commands

Linkplay devices support some commands through the API, this is a wrapper to be able to use these in Home Assistant:
```yaml
    - service: linkplay.command
      data:
        entity_id: media_player.sound_room1
        command: Reboot
        notify: False
```
Implemented commands:
- `Rescan` - do not wait for the current 60 second throttle cycle to reconnect to the unavailable devices, trigger testing for availability immediately
- `PromptEnable` and `PromptDisable` - enable or disable the audio prompts played through the speakers when connecting to the network or joining multiroom etc.
- `"WriteDeviceNameToUnit: My Device Name"` - change the friendly name of the device both in firmware and in Home Assistant. Needs to be in qoutes.
- `"SetApSSIDName: NewWifiName"` - change the SSID name of the AP created by the unit for wifidirect multiroom connections. Needs to be in qoutes.
- `SetRandomWifiKey`- perhaps as an extra security feature, one could make an automation to change the keys on the APs to some random values periodically.
- `TimeSync` - is for units on networks not connected to internet to compensate for an unreachable NTP server. Correct time is needed for the alarm clock functionality (not implemented yet here)
- `RouterMultiroomEnable` - router mode is available by default in firmwares above v4.2.8020, but there’s also a logic included to build it up, this command ensures to set the good priority. Only use if you have issues with multiroom in router mode.
- `MCU+XXX+XXX` - passthrough for direct TCP UART commands [supported by the module](https://forum.arylic.com/t/home-assistant-integratio-available/729/23). Input not validated, use at your own risk.

If parameter `notify: False` is omitted, results will appear in Lovelace UI's left pane as persistent notifications which can be dismissed. You can specify multiple entity ids separated by comma or use `all` to run the service against.

## Automation examples

Play a sound file located on an http server or a webradio stream:
```yaml
    - service: media_player.play_media
      data:
        entity_id: media_player.sound_room1
        media_content_id: 'http://icecast.streamserver.tld/mountpoint.mp3'
        media_content_type: url
```

Play the first sound file located on the local storage directly attached to the device (folder\files order seen by the chip seems to be alphabetic):
```yaml
    - service: media_player.play_media
      data:
        entity_id: media_player.sound_room1
        media_content_id: '1'
        media_content_type: music
```

Select an input and set volume and unmute via an automation:
```yaml
- alias: 'Switch to the line input of the TV when TV turns on'
  trigger:
    - platform: state
      entity_id: media_player.tv_room1
      to: 'on'
  action:
    - service: media_player.select_source
      data:
        entity_id: media_player.sound_room1
        source: 'TV sound'
    - service: media_player.volume_set
      data:
        entity_id: media_player.sound_room1
        volume_level: 1
    - service: media_player.volume_mute
      data:
        entity_id: media_player.sound_room1
        is_volume_muted: false
```
Note that you have to specify source names as you've set them in the configuration of the component.

Intrerupt playback of a source, say a TTS message and resume playback afterwards:
```yaml
- alias: 'Notify by TTS that Mary has arrived'
  trigger:
    - platform: state
      entity_id: person.mary
      to: 'home'
  action:
    - service: linkplay.snapshot
      data:
        entity_id: media_player.sound_room1
    - service: media_player.volume_set
      data:
        entity_id: media_player.hang_nappali
        volume_level: 0.8
    - service: tts.google_translate_say
      data:
        entity_id: media_player.sound_room1
        message: 'Mary arrived home'
    - delay: '00:00:02'
    - service: linkplay.restore
      data:
        entity_id: media_player.sound_room1
```
Note the `delay`, that should be equal or more with the time it takes for the TTS to spkeak out the text, usually that's an average of 1 second for every 3 words spoken out.

Browsing media files through Lovelace UI:
_This is deprecated, but left here as a reference. Use Media Browser as described above._
Some device models equipped with an USB port can play music from directly attached USB sticks. There are two services, `linkplay.get_tracks` and `linkplay.play_track` which allow reading the list of the files into an `input_select`, and trigger playback when selecting a file from the list. Here's how to set this up, with the list automatically filling itself when changing to USB.
Add to `configuration.yaml`:
```yaml
input_select:
  tracks_room1:
    name: Room1 music list
    icon: mdi:music
    options:
      - "____ Room1 ____"
    initial: "____ Room1 ____"
```
Add to your automations the followings (load the list when changing source to `USB stick`; clear the list when changing to other source; play the selected track):
```yaml
- alias: 'Music list load'
  trigger:
    platform: template
    value_template: "{% if is_state_attr('media_player.sound_room1', 'source', 'USB stick') %}True{% endif %}"
  action:
    - service: linkplay.get_tracks
      data:
        entity_id: media_player.sound_room1
        input_select: input_select.tracks_room1

- alias: 'Music list clear'
  trigger:
    platform: template
    value_template: "{% if not(is_state_attr('media_player.sound_room1', 'source', 'USB stick')) %}True{% endif %}"
  action:
    - service: input_select.set_options
      data:
        entity_id: input_select.tracks_room1
        options:
          - "____ Room1 ____"

- alias: 'Music list play selected track'
  trigger:
    - platform: state
      entity_id: input_select.tracks_room1
  action:
    - service: linkplay.play_track
      data:
        entity_id: media_player.sound_room1
        track: "{{ states('input_select.tracks_room1') }}"
```
You can use @mattieha's [Select List Card](https://github.com/mattieha/select-list-card) to display the input_select in Lovelace as scrollable list.

## About Linkplay

Linkplay is a smart audio chipset and module manufacturer. Their various module types share the same functionality across the whole platform and alow for native audio content playback from lots of sources, including local inputs, local files, Bluetooth, DNLA, Airplay and also web-based services like Icecast, Spotify, Tune-In, Deezer, Tidal etc. They allow setting up multiroom listening environments using either self-created wireless connections or relying on existing network infrastructure, for longer distances coverage. For more information visit https://linkplay.com/.
There are quite a few manufacturers and devices that operate on the basis of Linkplay platform. Here are just some examples of the brands and models:
- **Arylic** (S50Pro, A50, Up2Stream),
- **August** (WS300G),
- **Audio Pro** (A10, A26, A36, A40, Addon C3/C5/C5A/C10/C-SUB, D-1, Drumfire, Link 1),
- **Auna** (Intelligence Tube),
- **Bauhn** (SoundMax 5),
- **Bem** (Speaker Big Mo),
- **Centaurus** (Flyears),
- **Champion** (AWF320),
- **COWIN** (DiDa, Thunder),
- **Crystal Acoustics** (Crystal Audio),
- **CVTE** (FD2140),
- **Dayton Audio** (AERO),
- **DOSS** (Deshi, Soundbox Mini, DOSS Assistant, Cloud Fox A1),
- **DYON** (DYON Area Player),
- **Edifier** (MA1),
- **Energy Sistem** (Multiroom Tower Wi-Fi, Multiroom Portable Wi-Fi),
- **FABRIQ** (Chorus, Riff),
- **First Alert** (Onelink Safe & Sound),
- **GE Sol** (C),
- **GGMM** (E2 Wireless, E3 Wireless, E5 Wireless),
- **GIEC** (Hi-Fi Smart Sound S1),
- **Harman Kardon** (Allure),
- **Hyundai** (Modern Oxygen Bar),
- **iDeaUSA** (iDEaHome, Home Speaker, Mini Home Soundbar),
- **iEAST Sonoé** (AudioCast M5, SoundStream, Stream Pro, StreamAmp AM160, StreamAmp i50B),
- **iHome** (iAVS16),
- **iLive** (Concierge, Platinum),
- **iLuv** (Aud Air, Aud Click Shower, Aud Click),
- **JAM Audio** (Voice, Symphony, Rhythm),
- **JD** (CrazyBoa 2Face),
- **KEiiD**,
- **Lowes** (Showbox),
- **Magnavox** (MSH315V),
- **Medion** (MD43631, MedionX MD43259),
- **Meidong** (Meidong 3119),
- **MK** (MK Alexa Speaker),
- **MÜZO** (Cobblestone),
- **Naxa** (NAS-5003, NHS-5002, NAS-5001, NAS-5000),
- **Nexum** (Memo),
- **Omaker** (WoW),
- **Omars** (Dogo),
- **Polaroid** (PWF1001),
- **Roxcore**	(Roxcore),
- **Sharper Image** (SWF1002),
- **Shenzhen Renqing Technology Ltd** (ROCKLAVA),
- **SoundBot** (SB600),
- **SoundLogic** (Buddy),
- **Stereoboommm** (MR200, MR300),
- **Tibo** (Choros Tap),
- **Tinman** (Smart JOJO),
- **Venz** (A501),
- **Uyesee** (AM160),
- **Youzhuan** (Intelligent Music Ceiling),
- **Zolo Audio** (Holo),
- etc.

## Home Assisnatnt component authors & contributors
    "@nicjo814",
    "@limych",
    "@nagyrobi"

## Home Assisnatnt component License

MIT License

- Copyright (c) 2019 Niclas Berglind nicjo814
- Copyright (c) 2019—2020 Andrey "Limych" Khrolenok
- Copyright (c) 2020 nagyrobi Robert Horvath-Arkosi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[forum-support]: https://community.home-assistant.io/t/linkplay-integration/33878
