[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Yamaha Soundbar


This component allows you to control Yamaha soundbar.

Tested on Yamaha YAS-109 & YAS-209, any Yamaha soundbar based on Linkplay A118 should be supported as well.


## Installation

#### 1. Install custom component
 - Using HACS
 - Install manually: copy all files in `custom_components/yamha_soundbar` to your `<config directory>/custom_components/yamaha_soundbar/` directory.

#### 2. Restart Home-Assistant.
#### 3. Add the configuration to your configuration.yaml.
#### 4. Restart Home-Assistant again.

### Configuration

```yaml
# Example configuration.yaml entry
media_player:
    - platform: yamaha_soundbar
      host: 192.168.1.11
      name: My Sound Bar
```

## Todo

1. Proper Integration with config_flow
2. Add on/off support
3. Add other API features 

## License

This project is licensed under MIT license. See [LICENSE](LICENSE) file for details.
