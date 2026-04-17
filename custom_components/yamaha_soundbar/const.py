DOMAIN = 'yamaha_soundbar'


def signal_device_updated(entry_id: str) -> str:
    return f'{DOMAIN}_device_updated_{entry_id}'
PLATFORMS = ['media_player', 'switch', 'number', 'select']

SERVICE_JOIN = 'join'
SERVICE_UNJOIN = 'unjoin'
SERVICE_PRESET = 'preset'
SERVICE_CMD = 'command'
SERVICE_SNAP = 'snapshot'
SERVICE_REST = 'restore'
SERVICE_LIST = 'get_tracks'
SERVICE_PLAY = 'play_track'
SERVICE_SOUND = 'sound_settings'

ATTR_MASTER = 'master'
ATTR_PRESET = 'preset'
ATTR_CMD = 'command'
ATTR_NOTIF = 'notify'
ATTR_SNAP = 'switchinput'
ATTR_SELECT = 'input_select'
ATTR_SOURCE = 'source'
ATTR_TRACK = 'track'
ATTR_SOUND = 'sound_program'
ATTR_SUB = 'subwoofer_volume'
ATTR_SURROUND = 'surround'
ATTR_VOICE = 'clear_voice'
ATTR_BASS = 'bass_extension'
ATTR_MUTE = 'mute'
ATTR_POWER_SAVING = 'power_saving'

ATTR_SLAVE = 'slave'
ATTR_YAMAHA_GROUP = 'yamaha_group'
ATTR_FWVER = 'firmware'
ATTR_TRCNT = 'tracks_local'
ATTR_TRCRT = 'track_current'
ATTR_UUID = 'uuid'
ATTR_TTS = 'tts_active'
ATTR_SNAPSHOT = 'snapshot_active'
ATTR_SNAPSPOT = 'snapshot_spotify'
ATTR_DEBUG = 'debug_info'
ATTR_MASS_POSITION = 'media_position_mass'
ATTR_SOUND_PROGRAM = 'sound_program'
ATTR_SUBWOOFER_VOLUME = 'subwoofer_volume'
ATTR_CLEAR_VOICE = 'clear_voice'
ATTR_BASS_EXTENSION = 'bass_extension'

CONF_NAME = 'name'
CONF_SOURCE_IGNORE = 'source_ignore'
CONF_LASTFM_API_KEY = 'lastfm_api_key'
CONF_SOURCES = 'sources'
CONF_COMMONSOURCES = 'common_sources'
CONF_ICECAST_METADATA = 'icecast_metadata'
CONF_MULTIROOM_WIFIDIRECT = 'multiroom_wifidirect'
CONF_VOLUME_STEP = 'volume_step'
CONF_LEDOFF = 'led_off'
CONF_UUID = 'uuid'
CONF_ANNOUNCE_VOLUME_INCREASE = 'announce_volume_increase'
CONF_CERT_FILENAME = 'client.pem'

DEFAULT_ICECAST_UPDATE = 'StationName'
DEFAULT_MULTIROOM_WIFIDIRECT = False
DEFAULT_LEDOFF = False
DEFAULT_VOLUME_STEP = 5
DEFAULT_ANNOUNCE_VOLUME_INCREASE = 15
