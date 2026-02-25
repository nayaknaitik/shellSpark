"""
ai.py — Groq API integration for ShellSpark.

Handles command generation and explain mode.
"""

import sys
import re
import requests

from .config import GROQ_MODEL, GROQ_API_URL, MAX_RETRIES, TIMEOUT
from .history import load_history

# ── Prompts ───────────────────────────────────────────────────────────────────

_CMD_SYSTEM = """\
You are a bash command generator.

System: {distro_name} ({distro_id}) — package manager: {package_manager}

Rules:
1. Output ONLY the shell command — no explanations, no markdown fences.
2. Use {package_manager} for any package install/remove/update tasks.
3. Chain multiple commands with && or ;
4. Include sudo where the command requires root.
5. Use non-interactive flags (e.g. -y) where applicable.
6. If the request is ambiguous, generate the safest reasonable interpretation.
7. If the request is clearly dangerous (e.g. rm -rf /) output exactly: UNSAFE
8. If you genuinely cannot generate a command, output exactly: UNKNOWN
"""

_EXPLAIN_SYSTEM = """\
You are a helpful Linux command explainer for beginners.
Given a shell command, explain clearly what it does in plain English.
Keep the explanation concise (3–6 sentences max).
Do NOT suggest alternatives or improvements — only explain what the command does.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────


def _clean(raw: str) -> str:
    """Strip markdown fences the model might add."""
    raw = re.sub(r"^```(?:bash|sh|shell|zsh)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def _is_prose(text: str) -> bool:
    """Heuristic: returns True if text looks like an explanation, not a command."""
    if re.match(r"^[A-Z][a-z]+ [a-z]", text):
        return True
    if text.count("\n") > 3:
        return True
    return False


def _post(messages: list[dict], max_tokens: int = 300) -> str:
    """
    Send a chat completion request to Groq.
    Handles retries, connection errors, and HTTP error codes.
    Returns the raw model response text.
    """
    from .config import get_api_key

    api_key = get_api_key()

    last_err = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": max_tokens,
                },
                timeout=TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            print("🚫 No internet connection.")
            sys.exit(1)
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                print(f"⏱  Timeout, retrying ({attempt}/{MAX_RETRIES})...")
                continue
            print("🚫 Request timed out.")
            sys.exit(1)
        except requests.exceptions.RequestException as exc:
            print(f"🚫 Network error: {exc}")
            sys.exit(1)

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()

        if resp.status_code == 401:
            print("❌ Invalid API key. Run: shellspark --config")
            sys.exit(1)

        if resp.status_code == 429:
            print("⚠️  Rate limit reached. Please wait and try again.")
            sys.exit(1)

        if resp.status_code == 400:
            detail = resp.json().get("error", {}).get("message", resp.text[:200])
            print(f"❌ Bad request: {detail}")
            sys.exit(1)

        if resp.status_code >= 500:
            last_err = f"Server error {resp.status_code}"
            if attempt < MAX_RETRIES:
                print(f"⚠️  {last_err}, retrying ({attempt}/{MAX_RETRIES})...")
                continue
        else:
            last_err = f"HTTP {resp.status_code}"

    print(f"❌ API request failed after {MAX_RETRIES} attempts: {last_err}")
    sys.exit(1)


# ── Public API ────────────────────────────────────────────────────────────────


def generate_command(
    query: str,
    distro_name: str,
    distro_id: str,
    package_manager: str,
    use_history: bool = True,
) -> str:
    """
    Generate a shell command for the given natural-language query.
    Returns the command string, or sentinel "UNSAFE" / "UNKNOWN".
    """
    system_prompt = _CMD_SYSTEM.format(
        distro_name=distro_name,
        distro_id=distro_id,
        package_manager=package_manager,
    )

    messages = [{"role": "system", "content": system_prompt}]
    if use_history:
        messages.extend(load_history())
    messages.append({"role": "user", "content": query})

    raw = _post(messages, max_tokens=300)
    command = _clean(raw)

    # Sentinels from model
    if command in ("UNSAFE", "UNKNOWN"):
        return command

    # If model returned prose, try salvaging the first command-like line
    if _is_prose(command):
        for line in command.splitlines():
            line = line.strip()
            if line and not _is_prose(line):
                return line
        print("❌ Model returned a description instead of a command.")
        print(f"   Raw: {command[:200]}")
        sys.exit(1)

    return command


def explain_command(command: str) -> str:
    """
    Return a plain-English explanation of what a shell command does.
    """
    messages = [
        {"role": "system", "content": _EXPLAIN_SYSTEM},
        {"role": "user", "content": f"Explain this command:\n{command}"},
    ]
    return _post(messages, max_tokens=200)
