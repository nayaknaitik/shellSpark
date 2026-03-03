"""
chat.py — Conversational input detection for ShellSpark.

Handles greetings, identity questions, thanks, and goodbyes
without making any API calls.
"""

from shellspark.core.config import VERSION, GROQ_MODEL
from shellspark.core.system import get_distro_info, get_package_manager

# ── Trigger word sets ─────────────────────────────────────────────────────────

_GREETINGS = {
    "hello",
    "hi",
    "hey",
    "howdy",
    "hiya",
    "sup",
    "what's up",
    "whats up",
    "yo",
    "greetings",
    "good morning",
    "good afternoon",
    "good evening",
}

_WHAT_ARE_YOU = {
    "what are you",
    "who are you",
    "what is shellspark",
    "what's shellspark",
    "whats shellspark",
    "tell me about yourself",
    "about shellspark",
    "what do you do",
    "what can you do",
    "how do you work",
    "explain yourself",
}

_HOW_ARE_YOU = {
    "how are you",
    "how are you doing",
    "how's it going",
    "hows it going",
    "you ok",
    "you good",
    "how do you feel",
}

_THANKS = {
    "thanks",
    "thank you",
    "thankyou",
    "ty",
    "thx",
    "cheers",
    "appreciated",
    "nice",
    "great",
    "awesome",
    "cool",
    "perfect",
    "wonderful",
}

_GOODBYE = {
    "bye",
    "goodbye",
    "see you",
    "see ya",
    "later",
    "cya",
    "take care",
    "farewell",
}


def _matches(q: str, trigger_set: set[str]) -> bool:
    """True if q exactly matches or starts with any phrase in trigger_set."""
    return q in trigger_set or any(q.startswith(t) for t in trigger_set)


def detect_conversational(query: str) -> str | None:
    """
    Return a ready-to-print response if the query is conversational,
    or None if it should be passed to the command generator.
    """
    q = query.lower().strip().rstrip("!?.,")

    if _matches(q, _GREETINGS):
        distro_name, distro_id = get_distro_info()
        pkg = get_package_manager(distro_id)
        return (
            f"\n⚡ Hey! I'm ShellSpark — your intelligent terminal companion.\n\n"
            f"   I translate plain English into shell commands for your system.\n"
            f"   Detected: {distro_name} · {pkg}\n\n"
            f"   Try:\n"
            f"     shellspark update my system\n"
            f"     shellspark find files larger than 1GB\n"
            f"     shellspark install and start nginx\n\n"
            f"   Run 'shellspark --help' to see everything I can do.\n"
        )

    if _matches(q, _WHAT_ARE_YOU):
        return (
            f"\n⚡ ShellSpark v{VERSION}\n\n"
            f"   A CLI tool that converts natural language into\n"
            f"   distribution-specific shell commands using AI.\n\n"
            f"   Instead of memorizing syntax, just describe what you want:\n"
            f"     shellspark compress my-folder to tar.gz\n"
            f"     shellspark which process is on port 3000\n"
            f"     shellspark show disk usage by directory\n\n"
            f"   Powered by Groq · Model: {GROQ_MODEL}\n"
            f"   Free API key: https://console.groq.com\n"
        )

    if _matches(q, _HOW_ARE_YOU):
        return "\n⚡ Running fast and ready to generate commands! What do you need?\n"

    if q in _THANKS:
        return "\n⚡ Happy to help! Run another command anytime.\n"

    if q in _GOODBYE:
        return "\n👋 Goodbye! Come back when you need a command.\n"

    return None
