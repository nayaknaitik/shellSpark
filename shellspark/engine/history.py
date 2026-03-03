"""
history.py — Conversation history management for ShellSpark.
"""

import json
from shellspark.core.config import HISTORY_FILE, MAX_HISTORY, ensure_dirs


def load_history() -> list[dict]:
    """Load conversation history from disk. Returns [] on any failure."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data[-MAX_HISTORY:]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_history(history: list[dict]) -> None:
    """Persist history to disk, trimmed to MAX_HISTORY. Non-fatal on failure."""
    ensure_dirs()
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history[-MAX_HISTORY:], f, indent=2)
    except OSError:
        pass


def append_history(query: str, command: str) -> None:
    """Append a query/command pair to history."""
    history = load_history()
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": command})
    save_history(history)


def clear_history() -> None:
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    print("✅ History cleared.")


def show_history() -> None:
    history = load_history()
    if not history:
        print("No history yet.")
        return
    print("\n📜 Recent commands:\n")
    users = history[0::2]
    bots = history[1::2]
    for i, (u, b) in enumerate(zip(users, bots), 1):
        print(f"  [{i}] shellspark {u['content']}")
        print(f"      → {b['content']}\n")
