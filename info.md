# Yamaha Soundbars Linkplay-A119-based sound bars

This component allows you to integrate control of audio devices based on Yamaha Soundbars such as YAS-109 and YAS-209 into your [Home Assistant](http://www.home-assistant.io) smart home system. 

Fully compatible with Mini Media Player card for Lovelace UI, including speaker group management.

[Configuration details and documentation](https://github.com/catduckgnaf/yamaha-soundbar#installation)


## Supported features:
- Configurable input sources list, to match choices in HA with the pyhsical inputs available on each device
- Retrieval of current playing content metadata from Icecast webradio streams and filenames on directly attached USB sticks
- Retrieval of coverart from last.fm service based on current playing content metadata
- Multirooom in both WiFi-Direct and Router mode, using sonos-like standard 'join' and 'unjoin' service calls.
- Recall of music presets stored on the device
- Snapshot and restore state of the player for smooth usage with TTS
- Browsing and playing media files from the directly attached USB sticks through Lovelace UI
- Linkplay-chipset specific commands through HA service calls

## About Linkplay

Linkplay is a smart audio chipset and module manufacturer. Their various module types share the same functionality across the whole platform and alow for native audio content playback from lots of sources, including local inputs, local files, Bluetooth, DNLA, Airplay and also web-based services like Icecast, Spotify, Tune-In, Deezer, Tidal etc. They allow setting up multiroom listening environments using either self-created wireless connections or relying on existing network infrastructure, for longer distances coverage. For more information visit https://linkplay.com/.

## Component authors & contributors


[Support Discord](https://discord.gg/dtZCRDyj)
