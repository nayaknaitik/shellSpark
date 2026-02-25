"""
explainer.py — --explain mode for ShellSpark.

Fetches a plain-English explanation of the last generated command.
"""

from .ai import explain_command
from .history import load_history


def explain_last_or_query(query: str | None = None) -> None:
    """
    If query is given, generate a command from it and explain it.
    If no query, explain the most recent command from history.
    """
    if query:
        # The caller already has the generated command; explain it directly
        _print_explanation(query)
        return

    # Fall back to most recent history entry
    history = load_history()
    if not history:
        print("❓ No command history found. Run a command first, or provide a query.")
        return

    # Last assistant message is the most recent command
    bot_messages = [m["content"] for m in history if m["role"] == "assistant"]
    if not bot_messages:
        print("❓ No commands found in history.")
        return

    last_command = bot_messages[-1]
    print(f"\n  Explaining: \033[97m{last_command}\033[0m\n")
    _print_explanation(last_command)


def _print_explanation(command: str) -> None:
    print("⏳ Fetching explanation...")
    explanation = explain_command(command)
    print(f"\n📖 {explanation}\n")
