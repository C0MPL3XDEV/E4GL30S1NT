"""Configuration management: paths, loading, env overrides, logger, save."""
import json
import logging
import os
from logging.handlers import RotatingFileHandler

CONFIG_DIR  = os.path.join(os.path.expanduser("~"), ".config", "E4GL30S1NT")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
LOG_PATH    = os.path.join(CONFIG_DIR, "eagleosint.log")
COOKIE_FILE = os.path.join(os.path.expanduser("~"), ".cookies")
REALEMAIL_API_CONFIG_KEY = "real-email-api-key"
VERIPHONE_API_CONFIG_KEY = "veriphone-api-key"

os.makedirs(CONFIG_DIR, exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w", encoding="utf-8") as _f:
        _f.write("{}\n")

with open(CONFIG_PATH, "r", encoding="utf-8") as _cfg:
    CONFIGS: dict = json.load(_cfg)

_ENV_KEY_MAP = {
    REALEMAIL_API_CONFIG_KEY: "E4GL30S1NT_REALEMAIL_KEY",
    VERIPHONE_API_CONFIG_KEY: "E4GL30S1NT_VERIPHONE_KEY",
}
for _k, _v in _ENV_KEY_MAP.items():
    _val = os.getenv(_v)
    if _val:
        CONFIGS[_k] = _val


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
    """Write CONFIGS atomically — write-to-temp then os.replace()."""
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(CONFIGS, f, indent=2)
    os.replace(tmp, CONFIG_PATH)
    logger.debug("Config saved to %s", CONFIG_PATH)
