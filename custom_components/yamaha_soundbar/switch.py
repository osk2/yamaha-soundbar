import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, signal_device_updated

_LOGGER = logging.getLogger(__name__)

SWITCHES = [
    {
        "key": "clear voice",
        "name": "Clear Voice",
        "icon": "mdi:account-voice",
        "id_suffix": "clear_voice",
    },
    {
        "key": "3D surround",
        "name": "3D Surround",
        "icon": "mdi:surround-sound",
        "id_suffix": "3d_surround",
    },
    {
        "key": "bass extension",
        "name": "Bass Extension",
        "icon": "mdi:speaker",
        "id_suffix": "bass_extension",
    },
    {
        "key": "power saving",
        "name": "Power",
        "icon": "mdi:power",
        "id_suffix": "power_saving",
    },
    {
        "key": "mute",
        "name": "Mute",
        "icon": "mdi:volume-off",
        "id_suffix": "mute",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device = hass.data[DOMAIN].get(entry.entry_id)
    if device is None:
        return

    entities = [
        YamahaSoundbarSwitch(device, entry, sw)
        for sw in SWITCHES
    ]
    async_add_entities(entities)


class YamahaSoundbarSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, device, entry, description):
        self._device = device
        self._entry = entry
        self._yamaha_key = description["key"]
        self._attr_name = description["name"]
        self._attr_icon = description["icon"]
        self._attr_unique_id = f"{entry.unique_id}_{description['id_suffix']}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self._entry:
            self.async_on_remove(
                async_dispatcher_connect(
                    self.hass,
                    signal_device_updated(self._entry.entry_id),
                    self._handle_device_updated,
                )
            )

    @callback
    def _handle_device_updated(self, *args) -> None:
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo | None:
        if not self._device._uuid:
            return None
        return DeviceInfo(identifiers={(DOMAIN, self._device._uuid)})

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def is_on(self) -> bool | None:
        data = self._device._sound_statdata
        if not isinstance(data, dict) or self._yamaha_key not in data:
            return None
        val = data[self._yamaha_key]
        if isinstance(val, bool):
            return val
        try:
            return bool(int(val))
        except (TypeError, ValueError):
            return None

    async def async_turn_on(self, **kwargs) -> None:
        await self._send("1")

    async def async_turn_off(self, **kwargs) -> None:
        await self._send("0")

    async def _send(self, value: str) -> None:
        encoded_key = self._yamaha_key.replace(" ", "%20")
        cmd = f'YAMAHA_DATA_SET:{{%22{encoded_key}%22:%22{value}%22}}'
        result = await self._device.async_call_yamaha_httpapi(cmd, None)
        if result != "OK":
            _LOGGER.warning(
                "Failed to set %s for %s: %s",
                self._yamaha_key, self._device.entity_id, result,
            )
            return
        if isinstance(self._device._sound_statdata, dict):
            self._device._sound_statdata[self._yamaha_key] = value
        self.async_write_ha_state()
