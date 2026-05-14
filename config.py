import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".worklog" / "config.json"


def load() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}


def save(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_api_key() -> str:
    return load().get("anthropic_api_key", "")


def set_api_key(key: str):
    cfg = load()
    cfg["anthropic_api_key"] = key
    save(cfg)
