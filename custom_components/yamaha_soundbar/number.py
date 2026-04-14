import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, signal_device_updated

_LOGGER = logging.getLogger(__name__)


class _YamahaSoundbarNumberBase(NumberEntity):
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device = hass.data[DOMAIN].get(entry.entry_id)
    if device is None:
        return

    async_add_entities([
        YamahaSoundbarSubwooferVolume(device, entry),
        YamahaSoundbarVolume(device, entry),
    ])


class YamahaSoundbarSubwooferVolume(_YamahaSoundbarNumberBase):
    _attr_has_entity_name = True
    _attr_name = "Subwoofer Volume"
    _attr_icon = "mdi:volume-vibrate"
    _attr_native_min_value = -4
    _attr_native_max_value = 4
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, device, entry):
        self._device = device
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_subwoofer_volume"

    @property
    def device_info(self) -> DeviceInfo | None:
        if not self._device._uuid:
            return None
        return DeviceInfo(identifiers={(DOMAIN, self._device._uuid)})

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def native_value(self) -> float | None:
        data = self._device._sound_statdata
        if not isinstance(data, dict) or 'subwoofer volume' not in data:
            return None
        try:
            return int(data['subwoofer volume'])
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        int_val = int(value)
        cmd = f'YAMAHA_DATA_SET:{{%22subwoofer%20volume%22:%22{int_val}%22}}'
        result = await self._device.async_call_yamaha_httpapi(cmd, None)
        if result != "OK":
            _LOGGER.warning(
                "Failed to set subwoofer volume for %s: %s",
                self._device.entity_id, result,
            )
            return
        if isinstance(self._device._sound_statdata, dict):
            self._device._sound_statdata['subwoofer volume'] = str(int_val)
        self.async_write_ha_state()


class YamahaSoundbarVolume(_YamahaSoundbarNumberBase):
    _attr_has_entity_name = True
    _attr_name = "Volume"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, device, entry):
        self._device = device
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_volume"

    @property
    def device_info(self) -> DeviceInfo | None:
        if not self._device._uuid:
            return None
        return DeviceInfo(identifiers={(DOMAIN, self._device._uuid)})

    @property
    def available(self) -> bool:
        return self._device.available

    @property
    def native_value(self) -> float | None:
        try:
            return int(self._device._volume)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        vol = str(int(value))
        result = await self._device.async_call_yamaha_httpapi(
            f"setPlayerCmd:vol:{vol}", None
        )
        if result != "OK":
            _LOGGER.warning(
                "Failed to set volume for %s: %s",
                self._device.entity_id, result,
            )
            return
        self._device._volume = vol
        self.async_write_ha_state()
