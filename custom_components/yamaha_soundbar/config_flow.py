import asyncio
import logging
import os
import ssl

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from http import HTTPStatus

from .const import (
    DOMAIN,
    CONF_CERT_FILENAME,
    CONF_ICECAST_METADATA,
    CONF_MULTIROOM_WIFIDIRECT,
    CONF_LEDOFF,
    CONF_VOLUME_STEP,
    CONF_ANNOUNCE_VOLUME_INCREASE,
    CONF_LASTFM_API_KEY,
    CONF_SOURCE_IGNORE,
    CONF_SOURCES,
    CONF_COMMONSOURCES,
    CONF_UUID,
    DEFAULT_ICECAST_UPDATE,
    DEFAULT_MULTIROOM_WIFIDIRECT,
    DEFAULT_LEDOFF,
    DEFAULT_VOLUME_STEP,
    DEFAULT_ANNOUNCE_VOLUME_INCREASE,
)

_LOGGER = logging.getLogger(__name__)


async def _async_test_connection(host: str) -> dict | None:
    loop = asyncio.get_event_loop()
    dirname = os.path.dirname(__file__)
    certpath = os.path.join(dirname, CONF_CERT_FILENAME)
    ssl_ctx = await loop.run_in_executor(
        None, ssl.create_default_context, ssl.Purpose.SERVER_AUTH
    )
    await loop.run_in_executor(None, ssl_ctx.load_cert_chain, certpath)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    conn = aiohttp.TCPConnector(ssl_context=ssl_ctx)

    try:
        async with aiohttp.ClientSession(connector=conn) as session:
            url = f"https://{host}/httpapi.asp?command=getStatusEx"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == HTTPStatus.OK:
                    return await resp.json(content_type=None)
    except (asyncio.TimeoutError, aiohttp.ClientError, OSError):
        return None
    return None


def _parse_sources(raw: str) -> dict:
    result = {}
    if not raw or not raw.strip():
        return result
    for pair in raw.split(","):
        pair = pair.strip()
        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def _serialize_sources(sources: dict | list | None) -> str:
    if not sources:
        return ""
    if isinstance(sources, list):
        merged = {}
        for item in sources:
            if isinstance(item, dict):
                merged.update(item)
        sources = merged
    return ", ".join(f"{k}:{v}" for k, v in sources.items())


class YamahaSoundbarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return YamahaSoundbarOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME, "").strip()

            data = await _async_test_connection(host)
            if data is None:
                errors["base"] = "cannot_connect"
            else:
                uuid = data.get("uuid", "")
                if not name:
                    name = data.get("DeviceName", host)

                if uuid:
                    await self.async_set_unique_id(uuid)
                    self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                        CONF_UUID: uuid,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=""): str,
                }
            ),
            errors=errors,
        )


class YamahaSoundbarOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            sources_raw = user_input.pop(CONF_SOURCES, "")
            common_sources_raw = user_input.pop(CONF_COMMONSOURCES, "")
            ignore_raw = user_input.pop(CONF_SOURCE_IGNORE, "")

            user_input[CONF_SOURCES] = _parse_sources(sources_raw)
            user_input[CONF_COMMONSOURCES] = _parse_sources(common_sources_raw)
            user_input[CONF_SOURCE_IGNORE] = [
                s.strip() for s in ignore_raw.split(",") if s.strip()
            ]

            return self.async_create_entry(title="", data=user_input)

        opts = self._config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SOURCES,
                        default=_serialize_sources(opts.get(CONF_SOURCES)),
                    ): str,
                    vol.Optional(
                        CONF_COMMONSOURCES,
                        default=_serialize_sources(opts.get(CONF_COMMONSOURCES)),
                    ): str,
                    vol.Optional(
                        CONF_SOURCE_IGNORE,
                        default=", ".join(opts.get(CONF_SOURCE_IGNORE, [])),
                    ): str,
                    vol.Optional(
                        CONF_ICECAST_METADATA,
                        default=opts.get(CONF_ICECAST_METADATA, DEFAULT_ICECAST_UPDATE),
                    ): vol.In(["Off", "StationName", "StationNameSongTitle"]),
                    vol.Optional(
                        CONF_MULTIROOM_WIFIDIRECT,
                        default=opts.get(CONF_MULTIROOM_WIFIDIRECT, DEFAULT_MULTIROOM_WIFIDIRECT),
                    ): bool,
                    vol.Optional(
                        CONF_LEDOFF,
                        default=opts.get(CONF_LEDOFF, DEFAULT_LEDOFF),
                    ): bool,
                    vol.Optional(
                        CONF_VOLUME_STEP,
                        default=opts.get(CONF_VOLUME_STEP, DEFAULT_VOLUME_STEP),
                    ): vol.All(int, vol.Range(min=1, max=25)),
                    vol.Optional(
                        CONF_ANNOUNCE_VOLUME_INCREASE,
                        default=opts.get(CONF_ANNOUNCE_VOLUME_INCREASE, DEFAULT_ANNOUNCE_VOLUME_INCREASE),
                    ): vol.All(int, vol.Range(min=0, max=50)),
                    vol.Optional(
                        CONF_LASTFM_API_KEY,
                        default=opts.get(CONF_LASTFM_API_KEY, ""),
                    ): str,
                }
            ),
        )
