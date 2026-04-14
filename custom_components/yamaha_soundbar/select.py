import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, signal_device_updated

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device = hass.data[DOMAIN].get(entry.entry_id)
    if device is None:
        return

    async_add_entities([YamahaSoundbarInputSelect(device, entry)])


class YamahaSoundbarInputSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Input Source"
    _attr_icon = "mdi:import"

    def __init__(self, device, entry):
        self._device = device
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_input_source"
        self._last_valid_option = None

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
    def options(self) -> list[str]:
        if len(self._device._source_list) > 0:
            return list(self._device._source_list.values())
        return []

    @property
    def current_option(self) -> str | None:
        src = self._device._source
        opts = self.options
        if src and src in opts:
            self._last_valid_option = src
            return src
        if self._last_valid_option and self._last_valid_option in opts:
            return self._last_valid_option
        return opts[0] if opts else None

    async def async_select_option(self, option: str) -> None:
        await self._device.async_select_source(option)
        self._last_valid_option = option
        self.async_write_ha_state()
