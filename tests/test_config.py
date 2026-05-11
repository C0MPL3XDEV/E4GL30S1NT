import importlib
import json
import os
import sys
from unittest.mock import MagicMock, mock_open, patch

def _reload_config(env: dict | None = None):
    """Re-import eagleosint.config with a clean env and a fake empty config file."""
    fake_json = "{}"
    m = mock_open(read_data=fake_json)
    env = env or ()
    with (
        patch.dict(os.environ, env, clear=False),
        patch("os.makedirs"),
        patch("os.path.exists", return_value=True),
        patch("builtins.open", m),
        patch("logging.handlers.RotatingFileHandler"),
    ):
        if "eagleosint.config" in sys.modules:
            del sys.modules["eagleosint.config"]
        import eagleosint.config as cfg
    return cfg

class TestConfigPaths:
    def test_config_under_home(self):
        cfg = _reload_config()
        assert cfg.CONFIG_DIR.endswith(os.path.join(".config", "E4GL30S1NT"))

    def test_config_path_ends_with_json(self):
        cfg = _reload_config()
        assert cfg.CONFIG_PATH.endswith("config.json")

    def test_log_path_ends_with_log(self):
        cfg = _reload_config()
        assert cfg.LOG_PATH.endswith("eagleosint.log")

    def test_cookie_file_under_home(self):
        cfg = _reload_config()
        assert cfg.COOKIE_FILE == os.path.join(os.path.expanduser("~"), ".cookies")


class TestEnvOverrides:
    def test_realemail_key_loaded_from_env(self):
        cfg = _reload_config(env={"E4GL30S1NT_REALEMAIL_KEY": "test-re-key"})
        assert cfg.CONFIGS.get("real-email-api-key") == "test-re-key"

    def test_veriphone_key_loaded_from_env(self):
        cfg = _reload_config(env={"E4GL30S1NT_VERIPHONE_KEY": "test-vp-key"})
        assert cfg.CONFIGS.get("veriphone-api-key") == "test-vp-key"

    def test_missing_env_var_leaves_key_absent(self):
        cfg = _reload_config()
        # env isn't set — key must not be injected with a real value
        assert cfg.CONFIGS.get("real-email-api-key") in (None, "")

class TestSaveConfig:
    def test_save_config_writes_then_replaces(self, tmp_path):
        import eagleosint.config as cfg

        cfg.CONFIG_PATH = str(tmp_path / "config.json")
        cfg.CONFIGS = {"real-email-api-key": "saved"}
        cfg.save_config()

        with open(cfg.CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        assert data["real-email-api-key"] == "saved"

    def test_save_config_atomic_no_tmp_left(self, tmp_path):
        import eagleosint.config as cfg

        cfg.CONFIG_PATH = str(tmp_path / "config.json")
        cfg.CONFIGS = {}
        cfg.save_config()

        assert not os.path.exists(cfg.CONFIG_PATH + ".tmp")