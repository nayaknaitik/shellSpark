#!/usr/bin/env python3
"""
ShellSpark — Your Intelligent Terminal Companion
Converts natural language into distribution-specific bash commands.
"""

import sys

from .config import (
    VERSION,
    GROQ_MODEL,
    CONFIG_FILE,
    HISTORY_FILE,
    ensure_dirs,
    setup_api_key,
)
from .system import get_distro_info, get_package_manager, get_shell
from .history import append_history, clear_history, show_history
from .chat import detect_conversational
from .ai import generate_command, explain_command
from .safety import classify
from .executor import confirm_and_run
from .explainer import explain_last_or_query
from .logger import log_event
from .navigator import is_navigation_query, resolve_navigation_command
from .ui import (
    console,
    print_command,
    print_safety_status,
    print_error,
    print_warning,
    print_success,
    print_info,
    print_generating,
    print_explaining,
    print_explanation,
    print_unknown,
    print_unsafe,
    print_blocked,
    set_plain_mode,
)


def show_help() -> None:
    print(f"""
ShellSpark v{VERSION} — Your Intelligent Terminal Companion

USAGE:
  shellspark <query>
  shellspark [option]

OPTIONS:
  -h, --help                Show this help message
  -v, --version             Show version
  --config                  Set or update your Groq API key
  --model                   Show the current AI model
  --history                 View recent command history
  --clear-history           Delete all history
  --run <query>             Generate AND execute the command
  --dry-run <query>         Generate and display only (same as default)
  --explain <query>         Explain what the generated command does
  --no-history <query>      Run without using conversation context

EXAMPLES:
  shellspark update my system
  shellspark find files larger than 100MB in /home
  shellspark install and start nginx
  shellspark which process is using port 8080
  shellspark --run compress logs/ to tar.gz
  shellspark --explain delete all .tmp files here
  shellspark --dry-run remove old docker images
  shellspark --no-history list open ports

SAFETY:
  Commands are classified as SAFE / WARNING / BLOCKED before execution.
  BLOCKED commands are never executed.
  WARNING commands require explicit confirmation (type 'yes').
  Default mode shows the command only — use --run to execute.

CONFIG:
  Key file : {CONFIG_FILE}
  History  : {HISTORY_FILE}
  Model    : {GROQ_MODEL}

  Free API key: https://console.groq.com
""")


def main() -> None:
    ensure_dirs()
    args = sys.argv[1:]

    # ── Flags with no query ───────────────────────────────────────────────────
    if not args or args[0] in ("-h", "--help"):
        show_help()
        sys.exit(0)

    if args[0] in ("-v", "--version"):
        print(f"shellspark {VERSION}")
        sys.exit(0)

    if args[0] == "--config":
        setup_api_key()
        sys.exit(0)

    if args[0] == "--model":
        print(f"Model: {GROQ_MODEL}")
        sys.exit(0)

    if args[0] == "--history":
        show_history()
        sys.exit(0)

    if args[0] == "--clear-history":
        clear_history()
        sys.exit(0)

    # ── Query-level flags ─────────────────────────────────────────────────────
    run = False  # default: display only
    explain = False
    use_history = True
    plain = False

    if args[0] == "--run":
        run = True
        args = args[1:]

    elif args[0] == "--dry-run":
        # explicit dry-run flag (same as default, kept for clarity)
        args = args[1:]

    elif args[0] == "--plain":
        plain = True
        args = args[1:]

    if args and args[0] == "--explain":
        explain = True
        args = args[1:]

    if args and args[0] == "--no-history":
        use_history = False
        args = args[1:]

    # Apply plain mode
    if plain:
        set_plain_mode(True)

    if not args:
        print_error("No query provided. See: shellspark --help")
        sys.exit(1)

    query = " ".join(args)

    # ── Navigation query detection ─────────────────────────────────────────────
    if is_navigation_query(query):
        command = resolve_navigation_command(query)
        print(command)
        sys.exit(0)

    # ── Conversational short-circuit (no API key needed) ──────────────────────
    chat_reply = detect_conversational(query)
    if chat_reply is not None:
        console.print(chat_reply)
        sys.exit(0)

    # ── Detect system ─────────────────────────────────────────────────────────
    distro_name, distro_id = get_distro_info()
    package_manager = get_package_manager(distro_id)
    shell = get_shell()

    if package_manager == "unknown":
        print_warning(
            f"Unrecognised distro '{distro_id}' — commands may be inaccurate."
        )

    # ── Generate command ──────────────────────────────────────────────────────
    print_generating()

    command = generate_command(
        query, distro_name, distro_id, package_manager, shell, use_history
    )

    # ── Explain mode ──────────────────────────────────────────────────────────
    if explain:
        print_command(command)
        print_explaining()
        explanation = explain_command(command)
        print_explanation(command, explanation)
        sys.exit(0)

    # ── Safety classification (for logging) ───────────────────────────────────
    safety_result = classify(command)

    # ── Display command with safety ────────────────────────────────────────────
    print_safety_status(safety_result.risk.value, safety_result.reason)
    print_command(command)

    # ── Confirm and optionally run ────────────────────────────────────────────
    return_code = confirm_and_run(command, run=run, safety_result=safety_result)

    # ── Log event ─────────────────────────────────────────────────────────────
    log_event(
        query=query,
        command=command,
        risk=safety_result.risk.value,
        exit_code=return_code if run else None,
    )

    # ── Save to history on clean run ──────────────────────────────────────────
    if run and return_code == 0 and command not in ("UNSAFE", "UNKNOWN"):
        append_history(query, command)

    # ── Exit feedback ─────────────────────────────────────────────────────────
    if run:
        if return_code == 0:
            print_success("Done.")
        elif return_code not in (130, 1):
            print_warning(f"Exited with code {return_code}.")

    sys.exit(return_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]👋 Goodbye![/]")
        sys.exit(130)
