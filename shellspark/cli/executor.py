"""
executor.py — Command display, safety confirmation, and execution for ShellSpark.

Default policy: display only (dry-run).
Pass run=True to actually execute.
"""

import platform
import subprocess
import sys
from typing import Optional

from shellspark.engine.safety import SafetyResult, classify, Risk
from .ui import (
    console,
    print_command,
    print_safety_status,
    print_error,
    print_warning,
    print_success,
    print_unknown,
    print_unsafe,
    print_blocked,
    print_info,
    prompt_execute,
    prompt_confirm_warning,
)


def _is_windows() -> bool:
    """Check if running on Windows (native, not WSL)."""
    return platform.system() == "Windows"


def confirm_and_run(
    command: str, run: bool = False, safety_result: Optional[SafetyResult] = None
) -> int:
    """
    Display the command and its safety classification.
    If run=True, ask for confirmation (stronger for WARNING) and execute.
    If run=False (default), display only — never execute.

    Returns an exit code (0 = ok, 1 = blocked/cancelled, 130 = interrupted).
    """

    # ── Model sentinels ───────────────────────────────────────
    if command == "UNSAFE":
        print_unsafe()
        return 1

    if command == "UNKNOWN":
        print_unknown()
        return 1

    # ── Safety classification ─────────────────────────────────
    if safety_result is None:
        safety_result = classify(command)

    if safety_result.is_blocked:
        print_blocked(safety_result.reason)
        return 1

    # ── Dry-run mode (default) ────────────────────────────────
    if not run:
        print_info("Add --run to execute this command.")
        return 0

    # ── Confirmation ──────────────────────────────────────────
    if safety_result.is_warning:
        return _confirm_warning(command)

    return _confirm_safe(command)


def _confirm_safe(command: str) -> int:
    """Standard Y/n confirmation for SAFE commands."""
    try:
        answer = input("Execute? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[red]🚫 Cancelled.[/]")
        return 130

    if answer not in ("", "y", "yes"):
        console.print("[red]🚫 Cancelled.[/]")
        return 0

    return _execute(command)


def _confirm_warning(command: str) -> int:
    """Stronger confirmation for WARNING commands — requires typing 'yes'."""
    console.print("[yellow]   Type 'yes' to confirm, anything else to cancel.[/]")
    try:
        answer = input("Confirm: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[red]🚫 Cancelled.[/]")
        return 130

    if answer != "yes":
        console.print("[red]🚫 Cancelled.[/]")
        return 0

    return _execute(command)


def _execute(command: str) -> int:
    """Run the command in a shell and return its exit code."""
    try:
        if _is_windows():
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                check=False,
                capture_output=False,
            )
            return result.returncode
        else:
            result = subprocess.run(command, shell=True, check=False)
            return result.returncode
    except KeyboardInterrupt:
        print("\n🚫 Interrupted.")
        return 130
