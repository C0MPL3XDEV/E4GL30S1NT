"""Configuration management: paths, loading, env overrides, logger, save."""
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from platformdirs import user_config_dir

CONFIG_DIR = user_config_dir("E4GL30S1NT", appauthor=False)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
LOG_PATH    = os.path.join(CONFIG_DIR, "eagleosint.log")
COOKIE_FILE = os.path.join(os.path.expanduser("~"), ".cookies")
PINGUTIL_API_CONFIG_KEY = "pingutil-api-key"
VERIPHONE_API_CONFIG_KEY = "veriphone-api-key"

os.makedirs(CONFIG_DIR, exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w", encoding="utf-8") as _f:
        _f.write("{}\n")

with open(CONFIG_PATH, "r", encoding="utf-8") as _cfg:
    CONFIGS: dict = json.load(_cfg)

_ENV_KEY_MAP = {
    PINGUTIL_API_CONFIG_KEY:  "E4GL30S1NT_PINGUTIL_KEY",
    VERIPHONE_API_CONFIG_KEY: "E4GL30S1NT_VERIPHONE_KEY",
}
for _k, _v in _ENV_KEY_MAP.items():
    _val = os.getenv(_v)
    if _val:
        CONFIGS[_k] = _val


# --------------------------------------------------------------
# Settings model
# --------------------------------------------------------------

from pydantic import BaseModel, ConfigDict, SecretStr

class Settings(BaseModel):
    """
    Typed, validated, secrets-masked application configuration.

    Secrets are stored as SecretStr - they appear as '*********' in
    logs and repr, never as plaintext.
    Adding a new provider key = one new field here.
    """
    model_config = ConfigDict(extra="ignore")

    pingutil_api_key: SecretStr | None = None
    veriphone_api_key: SecretStr | None = None

    def get_key(self, name: str) -> str | None:
        """Return a secret value by its dash-separated key name."""
        val = getattr(self, name.replace("-", "_"), None)
        return val.get_secret_value() if isinstance(val, SecretStr) else None

    def set_key(self, name: str, value: str) -> None:
        """Update a key in-place, Raises KeyError for unknown keys."""
        attr = name.replace("-", "_")
        if attr not in self.model_fields:
            raise KeyError(f"unknown config key: {name!r}")
        setattr(self, attr, SecretStr(value) if value else None)

    def to_file_dict(self) -> dict[str, str]:
        """Non-null keys as plaintext dict - for JSON persistence only"""
        out = {}
        for field_name in self.model_fields:
            val = getattr(self, field_name)
            if isinstance(val, SecretStr):
                out[field_name.replace("_", "-")] = val.get_secret_value()

        return out

    def display_items(self) -> dict[str, str]:
       """All keys with partially masked values - for the settings UI"""
       out = {}
       for field_name in self.model_fields:
           val = getattr(self, field_name)
           dash_name = field_name.replace("_", "-")
           if isinstance(val, SecretStr):
               raw = val.get_secret_value()
               out[dash_name] = f"{raw[:4]}{'*' * 8}" if raw else "(empty)"
           else:
               out[dash_name] = "(not set)"
       return out

# --------------------------------------------------------------
# Load settings: JSON file -> env var overrides
# --------------------------------------------------------------

def _to_secret(val: str | None) -> SecretStr | None:
    return SecretStr(val) if val else None

def _load_settings() -> Settings:
    data: dict[str, str] = {}

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    _env_map = {
        "pingutil-api-key": "E4GL30S1NT_PINGUTIL_KEY",
        "veriphone-api-key": "E4GL30S1NT_VERIPHONE_KEY",
    }
    for key_name, env_var in _env_map.items():
        val = os.getenv(env_var)
        if val:
            data[key_name] = val

    return Settings(
        pingutil_api_key=_to_secret(data.get("pingutil-api-key")),
        veriphone_api_key=_to_secret(data.get("veriphone-api-key")),
    )

settings = _load_settings()

def _setup_logger() -> logging.Logger:
    _logger = logging.getLogger("eagleosint")
    if _logger.handlers:
        return _logger
    _logger.setLevel(logging.DEBUG)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        _handler = RotatingFileHandler(
            LOG_PATH, maxBytes=500_000, backupCount=2, encoding="utf-8"
        )
        _handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-8s %(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        _logger.addHandler(_handler)
    except OSError as e:
        print(f"[warn] Could not create log file at {LOG_PATH}: {e}")
    return _logger


logger = _setup_logger()
logger.info("session started")


def save_config() -> None:
    """Persist settings to JSON file atomically."""
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings.to_file_dict(), f, indent=2)
    os.replace(tmp, CONFIG_PATH)
    logger.debug("Config saved to %s", CONFIG_PATH)
