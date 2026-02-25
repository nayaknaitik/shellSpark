"""
executor.py — Command display, safety confirmation, and execution for ShellSpark.

Default policy: display only (dry-run).
Pass run=True to actually execute.
"""

import sys
import subprocess

from .safety import classify, display_safety, Risk


def confirm_and_run(command: str, run: bool = False) -> int:
    """
    Display the command and its safety classification.
    If run=True, ask for confirmation (stronger for WARNING) and execute.
    If run=False (default), display only — never execute.

    Returns an exit code (0 = ok, 1 = blocked/cancelled, 130 = interrupted).
    """

    # ── Model sentinels ───────────────────────────────────────
    if command == "UNSAFE":
        print("⚠️  The AI flagged this request as unsafe.")
        print("   Please rephrase to be more specific.")
        return 1

    if command == "UNKNOWN":
        print("❓ ShellSpark couldn't generate a command for that request.")
        print("   Try rephrasing with more detail.")
        return 1

    # ── Safety classification ─────────────────────────────────
    result = classify(command)
    display_safety(result)

    if result.is_blocked:
        return 1

    # ── Display command ───────────────────────────────────────
    print(f"  \033[97m{command}\033[0m\n")

    # ── Dry-run mode (default) ────────────────────────────────
    if not run:
        print("💡 Add --run to execute this command.")
        return 0

    # ── Confirmation ──────────────────────────────────────────
    if result.is_warning:
        return _confirm_warning(command)

    return _confirm_safe(command)


def _confirm_safe(command: str) -> int:
    """Standard Y/n confirmation for SAFE commands."""
    try:
        answer = input("Execute? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n🚫 Cancelled.")
        return 130

    if answer not in ("", "y", "yes"):
        print("🚫 Cancelled.")
        return 0

    return _execute(command)


def _confirm_warning(command: str) -> int:
    """Stronger confirmation for WARNING commands — requires typing 'yes'."""
    print("   Type 'yes' to confirm, anything else to cancel.")
    try:
        answer = input("Confirm: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n🚫 Cancelled.")
        return 130

    if answer != "yes":
        print("🚫 Cancelled.")
        return 0

    return _execute(command)


def _execute(command: str) -> int:
    """Run the command in a shell and return its exit code."""
    try:
        result = subprocess.run(command, shell=True, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n🚫 Interrupted.")
        return 130
