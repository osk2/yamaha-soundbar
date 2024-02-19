[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Yamaha Soundbar

This component allows you to control Yamaha soundbar.

Tested on Yamaha YAS-109 & YAS-209, any Yamaha soundbar based on Linkplay A118 should be supported as well. (These include ATS-1090, ATS-2090, SR-X40A, SR-X50A, ATS-X500, Please make an issue in Github if you have a different model and it's not working, or even better if it is, so we can update the compatibility list.)

## Installation

#### 1. Install custom component
 - Using HACS
 - Install manually: copy all files in `custom_components/yamha_soundbar` to your `<config directory>/custom_components/yamaha_soundbar/` directory.

#### 2. Restart Home-Assistant.
#### 3. Add the configuration to your configuration.yaml.
#### 4. Restart Home-Assistant again.

## Upgrading from version 3.1.9 and earlier.

If you are upgrading from version 3.1.9 or earlier:
#### 1. You will need to remove the old integration which is /custom_components/linkplay/ and then install the new integration.
#### 2. You will need to update the platform configuration to `yamaha_soundbar` from `linkplay` in your `configuration.yaml` file.

### Configuration

```yaml
# Example configuration.yaml entry
media_player:
  - platform: yamaha_soundbar
    host: 192.168.1.11
    name: My Sound Bar
    # To Name your sources (optional)
    sources:
      {
        'HDMI': 'TV', 
        'optical': 'Plexamp', 
        'bluetooth': 'Bluetooth',
      }
```

## Todo

1. Proper Integration with config_flow
2. Add on/off support
3. Add other API features 

## License

This project is licensed under MIT license. See [LICENSE](LICENSE) file for details.
