[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# YAHAMA soundbar

```
This component is under heavy development and expect some major changes in the future.
```

This component allows you to control YAHAMA soundbar.

Tested on YAHAMA YAS-209, any YAMAHA soundbar based on Linkplay A118 should be supported as well.

The repo is forked from [nagyrobi/home-assistant-custom-components-linkplay](https://github.com/nagyrobi/home-assistant-custom-components-linkplay)

## Installation

#### 1. Install custom component
 - Using HACS
 - Install manually: copy all files in `custom_components/linkplay` to your `<config directory>/custom_components/linkplay/` directory.

#### 2. Restart Home-Assistant.
#### 3. Add the configuration to your configuration.yaml.
#### 4. Restart Home-Assistant again.

### Configuration

```yaml
# Example configuration.yaml entry
media_player:
    - platform: linkplay
      host: 192.168.1.11
      name: My Sound Bar
```

## License

This project is licensed under MIT license. See [LICENSE](LICENSE) file for details.
