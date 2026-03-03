"""
ai.py — Groq API integration for ShellSpark.

Handles command generation and explain mode.
"""

import sys
import re
import requests

from shellspark.core.config import GROQ_MODEL, GROQ_API_URL, MAX_RETRIES, TIMEOUT
from shellspark.engine.history import load_history

# ── Prompts ───────────────────────────────────────────────────────────────────

_CMD_SYSTEM = """\
You are a deterministic shell command generator.

Environment:
System: {distro_name} ({distro_id})
Shell: {shell}
Package Manager: {package_manager}

STRICT OUTPUT RULES:
- Output ONLY a valid executable shell command for the specified shell.
- No explanations, no comments, no markdown, no backticks.
- No surrounding text of any kind.
- Output must be directly runnable in {shell}.

BEHAVIOR RULES:

1. Prefer the SAFEST possible command that fulfills the request.
2. Never generate destructive or irreversible commands unless explicitly required.
3. If the request is clearly destructive, dangerous, or system-breaking,
   output EXACTLY: UNSAFE

Examples of UNSAFE scenarios include (not exhaustive):
- Filesystem wipes or recursive deletion of critical paths
- Disk formatting, partitioning, raw device writes
- Fork bombs or resource exhaustion
- Privilege manipulation or security bypass
- Commands that could cause major data loss

4. If the request lacks enough clarity, choose the most conservative interpretation.
5. Use the detected package manager ONLY when package operations are requested.
6. Use non-interactive flags where appropriate (-y, --noconfirm, etc.).
7. Include sudo ONLY when strictly required.
8. Avoid unnecessary flags or verbosity.
9. Prefer widely compatible commands over distro-specific edge cases.
10. Chain commands only when logically required.
11. Use PowerShell syntax on Windows, bash/zsh syntax on Unix.

FALLBACK RULES:

- If the request is valid but cannot be mapped confidently → output: UNKNOWN
- If the request implies unsafe behavior → output: UNSAFE

QUALITY CONSTRAINTS:

- Do not invent commands, flags, paths, or package names.
- Do not assume files or directories exist unless specified.
- Do not generate placeholder values.
- Commands must be minimal, correct, and practical.

Generate the shell command for the user request.
"""

_EXPLAIN_SYSTEM = """\
You are a beginner-friendly shell command explainer.

Task:
Explain the provided shell command in clear, simple English.

STRICT RULES:

1. Explain ONLY what the command does.
2. Do NOT suggest improvements, alternatives, or warnings.
3. Do NOT rewrite the command.
4. Do NOT add security advice.
5. Do NOT mention best practices.
6. Keep explanation concise and factual.
7. Length: 3–6 sentences maximum.
8. Avoid jargon unless absolutely necessary.
9. If technical terms are used, explain them briefly.
10. Maintain a neutral, instructional tone.

Your explanation must help a beginner understand the command’s effect.
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
    from shellspark.core.config import get_api_key

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
    shell: str = "bash",
    use_history: bool = True,
) -> str:
    """
    Generate a shell command for the given natural-language query.
    Returns the command string, or sentinel "UNSAFE" / "UNKNOWN".
    """
    system_prompt = _CMD_SYSTEM.format(
        distro_name=distro_name,
        distro_id=distro_id,
        shell=shell,
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
