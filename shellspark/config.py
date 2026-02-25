"""
config.py — ShellSpark configuration, constants, and API key management.
"""

import sys
import os
import json
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
CONFIG_DIR  = Path.home() / ".shellspark"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR     = CONFIG_DIR / "logs"
HISTORY_FILE = CONFIG_DIR / "history.json"
ACTIVITY_LOG = LOG_DIR / "activity.log"

# ── API / Model ───────────────────────────────────────────────────────────────

GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── Tuning ────────────────────────────────────────────────────────────────────

MAX_HISTORY = 20   # conversation messages kept on disk
MAX_RETRIES = 2    # API retry attempts on transient failure
TIMEOUT     = 30   # request timeout in seconds


def ensure_dirs() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict) -> None:
    ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> str:
    """Return API key from config or GROQ_API_KEY env var; prompt if missing."""
    config = load_config()
    key = config.get("api_key") or os.environ.get("GROQ_API_KEY", "")
    if key:
        return key
    return setup_api_key()


def setup_api_key() -> str:
    """Interactive API key setup with basic format validation."""
    print("\n🔑 Groq API Key Setup")
    print("─" * 40)
    print("Get a free key at: https://console.groq.com\n")

    try:
        key = input("Enter your Groq API key: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n🚫 Setup cancelled.")
        sys.exit(1)

    if not key:
        print("🚫 No key provided.")
        sys.exit(1)

    if not key.startswith("gsk_"):
        print("⚠️  Warning: Groq keys usually start with 'gsk_'. Double-check your key.")
        try:
            confirm = input("Save anyway? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)
        if confirm not in ("y", "yes"):
            sys.exit(1)

    cfg = load_config()
    cfg["api_key"] = key
    save_config(cfg)
    print("✅ API key saved.\n")
    return key