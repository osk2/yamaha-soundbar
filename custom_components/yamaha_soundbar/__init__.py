"""
Support for Yamaha Linkplay A118 based devices

For more details about this platform, please refer to the documentation at
https://github.com/osk2/yamaha_soundbar
"""
import asyncio
import logging
import os
import ssl

import aiohttp
import voluptuous as vol
from http import HTTPStatus

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, STATE_IDLE, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_UUID,
    CONF_SOURCES,
    CONF_COMMONSOURCES,
    CONF_ICECAST_METADATA,
    CONF_MULTIROOM_WIFIDIRECT,
    CONF_LEDOFF,
    CONF_VOLUME_STEP,
    CONF_ANNOUNCE_VOLUME_INCREASE,
    CONF_LASTFM_API_KEY,
    CONF_CERT_FILENAME,
    DEFAULT_ICECAST_UPDATE,
    DEFAULT_MULTIROOM_WIFIDIRECT,
    DEFAULT_LEDOFF,
    DEFAULT_VOLUME_STEP,
    DEFAULT_ANNOUNCE_VOLUME_INCREASE,
    SERVICE_JOIN,
    SERVICE_UNJOIN,
    SERVICE_PRESET,
    SERVICE_CMD,
    SERVICE_SNAP,
    SERVICE_REST,
    SERVICE_PLAY,
    SERVICE_SOUND,
    ATTR_MASTER,
    ATTR_PRESET,
    ATTR_CMD,
    ATTR_NOTIF,
    ATTR_SNAP,
    ATTR_TRACK,
    ATTR_SOUND,
    ATTR_SUB,
    ATTR_SURROUND,
    ATTR_VOICE,
    ATTR_BASS,
    ATTR_MUTE,
    ATTR_POWER_SAVING,
)

SERVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.comp_entity_ids
})

JOIN_SERVICE_SCHEMA = SERVICE_SCHEMA.extend({
    vol.Required(ATTR_MASTER): cv.entity_id
})

PRESET_BUTTON_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_PRESET): cv.positive_int
})

CMND_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_CMD): cv.string,
    vol.Optional(ATTR_NOTIF, default=True): cv.boolean
})

REST_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids
})

SNAP_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Optional(ATTR_SNAP, default=True): cv.boolean
})

PLYTRK_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Required(ATTR_TRACK): cv.template
})

SOUND_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_id,
    vol.Optional(ATTR_SOUND): cv.string,
    vol.Optional(ATTR_SUB): int,
    vol.Optional(ATTR_SURROUND): cv.boolean,
    vol.Optional(ATTR_VOICE): cv.boolean,
    vol.Optional(ATTR_BASS): cv.boolean,
    vol.Optional(ATTR_MUTE): cv.boolean,
    vol.Optional(ATTR_POWER_SAVING): cv.boolean
})

_LOGGER = logging.getLogger(__name__)


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_JOIN):
        return

    async def async_service_handle(service):
        _LOGGER.debug("DOMAIN: %s, entities: %s", DOMAIN, str(hass.data[DOMAIN]["entities"]))
        _LOGGER.debug("Service_handle from id: %s", service.data.get(ATTR_ENTITY_ID))
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        entities = hass.data[DOMAIN]["entities"]

        if entity_ids:
            if entity_ids == 'all':
                entity_ids = [e.entity_id for e in entities]
            entities = [e for e in entities if e.entity_id in entity_ids]

        if service.service == SERVICE_JOIN:
            master = [e for e in hass.data[DOMAIN]["entities"]
                      if e.entity_id == service.data[ATTR_MASTER]]
            if master:
                client_entities = [e for e in entities
                                   if e.entity_id != master[0].entity_id]
                _LOGGER.debug("**JOIN** set clients %s for master %s",
                              [e.entity_id for e in client_entities],
                              master[0].entity_id)
                await master[0].async_join(client_entities)

        elif service.service == SERVICE_UNJOIN:
            _LOGGER.debug("**UNJOIN** entities: %s", entities)
            masters = [ent for ent in entities if ent.is_master]
            if masters:
                for master in masters:
                    await master.async_unjoin_all()
            else:
                for entity in entities:
                    await entity.async_unjoin_me()

        elif service.service == SERVICE_PRESET:
            preset = service.data.get(ATTR_PRESET)
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**PRESET** entity: %s; preset: %s", device.entity_id, preset)
                    await device.async_preset_button(preset)

        elif service.service == SERVICE_CMD:
            command = service.data.get(ATTR_CMD)
            notify = service.data.get(ATTR_NOTIF)
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**COMMAND** entity: %s; command: %s", device.entity_id, command)
                    await device.async_execute_command(command, notify)

        elif service.service == SERVICE_SNAP:
            switchinput = service.data.get(ATTR_SNAP)
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**SNAPSHOT** entity: %s;", device.entity_id)
                    await device.async_snapshot(switchinput)

        elif service.service == SERVICE_REST:
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**RESTORE** entity: %s;", device.entity_id)
                    await device.async_restore()

        elif service.service == SERVICE_PLAY:
            track = service.data.get(ATTR_TRACK)
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**PLAY TRACK** entity: %s; track: %s", device.entity_id, track)
                    await device.async_play_track(track)

        elif service.service == SERVICE_SOUND:
            settings = {key: service.data.get(key) for key in [ATTR_SOUND,
                                                          ATTR_SUB,
                                                          ATTR_SURROUND,
                                                          ATTR_VOICE,
                                                          ATTR_BASS,
                                                          ATTR_POWER_SAVING,
                                                          ATTR_MUTE]}
            for device in entities:
                if device.entity_id in entity_ids:
                    _LOGGER.debug("**SET SOUND** entity: %s; settings: %s", device.entity_id,
                                  settings)
                    await device.async_set_sound(settings)

    hass.services.async_register(
        DOMAIN, SERVICE_JOIN, async_service_handle, schema=JOIN_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_UNJOIN, async_service_handle, schema=SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_PRESET, async_service_handle, schema=PRESET_BUTTON_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_CMD, async_service_handle, schema=CMND_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_SNAP, async_service_handle, schema=SNAP_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_REST, async_service_handle, schema=REST_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY, async_service_handle, schema=PLYTRK_SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_SOUND, async_service_handle, schema=SOUND_SERVICE_SCHEMA)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {"entities": []})
    _register_services(hass)

    from .media_player import YamahaDevice

    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, host)
    uuid = entry.data.get(CONF_UUID, "")

    opts = entry.options
    sources = opts.get(CONF_SOURCES)
    common_sources = opts.get(CONF_COMMONSOURCES)
    icecast_metadata = opts.get(CONF_ICECAST_METADATA, DEFAULT_ICECAST_UPDATE)
    multiroom_wifidirect = opts.get(CONF_MULTIROOM_WIFIDIRECT, DEFAULT_MULTIROOM_WIFIDIRECT)
    led_off = opts.get(CONF_LEDOFF, DEFAULT_LEDOFF)
    volume_step = opts.get(CONF_VOLUME_STEP, DEFAULT_VOLUME_STEP)
    announce_volume_increase = opts.get(CONF_ANNOUNCE_VOLUME_INCREASE, DEFAULT_ANNOUNCE_VOLUME_INCREASE)
    lastfm_api_key = opts.get(CONF_LASTFM_API_KEY)

    state = STATE_IDLE
    loop = asyncio.get_event_loop()
    initurl = f"https://{host}/httpapi.asp?command=getStatusEx"
    dirname = os.path.dirname(__file__)
    certpath = os.path.join(dirname, CONF_CERT_FILENAME)
    ssl_ctx = await loop.run_in_executor(None, ssl.create_default_context, ssl.Purpose.SERVER_AUTH)
    await loop.run_in_executor(None, ssl_ctx.load_cert_chain, certpath)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    conn = aiohttp.TCPConnector(ssl_context=ssl_ctx)

    try:
        async with aiohttp.ClientSession(connector=conn) as websession:
            response = await websession.get(initurl)
            if response.status == HTTPStatus.OK:
                data = await response.json(content_type=None)
                if not uuid:
                    uuid = data.get('uuid', '')
                if not name or name == host:
                    name = data.get('DeviceName', host)
            else:
                state = STATE_UNAVAILABLE
    except (asyncio.TimeoutError, aiohttp.ClientError):
        state = STATE_UNAVAILABLE

    device = YamahaDevice(
        name, host, sources, common_sources,
        icecast_metadata, multiroom_wifidirect, led_off,
        volume_step, announce_volume_increase, lastfm_api_key,
        uuid, state, hass, entry,
    )

    if state != STATE_UNAVAILABLE:
        sound_data = await device.async_call_yamaha_httpapi("YAMAHA_DATA_GET", True)
        if isinstance(sound_data, dict):
            device._sound_statdata = sound_data
        player_data = await device.async_call_yamaha_httpapi("getPlayerStatus", True)
        if isinstance(player_data, dict):
            device._player_statdata = player_data
            device._volume = player_data.get('vol', 0)
            device._muted = bool(int(player_data.get('mute', 0)))

    hass.data[DOMAIN][entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        hass.data[DOMAIN]["entities"] = [
            e for e in hass.data[DOMAIN]["entities"]
            if getattr(e, "_entry", None) is not entry
        ]
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
