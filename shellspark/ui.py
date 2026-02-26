"""
ui.py — Terminal UI rendering using Rich.

Provides styled output for ShellSpark CLI.
Keeps core logic modules UI-agnostic.
"""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


plain_mode = False
console = Console()


THEME = {
    "safe": {"style": "green", "icon": "✓"},
    "warning": {"style": "yellow", "icon": "⚠"},
    "blocked": {"style": "red", "icon": "✕"},
    "unknown": {"style": "dim", "icon": "?"},
    "unsafe": {"style": "red", "icon": "⚠"},
    "command_panel": {"border": "blue"},
    "info": {"style": "cyan", "icon": "ℹ"},
    "error": {"style": "red", "icon": "✕"},
    "success": {"style": "green", "icon": "✓"},
    "dim": {"style": "dim"},
}


def set_plain_mode(enabled: bool) -> None:
    """Enable or disable plain text mode."""
    global plain_mode
    plain_mode = enabled


def _t(text: str, style_key: str = "info") -> str:
    """Apply theme style to text."""
    if plain_mode:
        return text
    theme = THEME.get(style_key, THEME["info"])
    icon = theme.get("icon", "")
    style = theme.get("style", "")
    if style:
        return f"[{style}]{icon} {text}[/]" if icon else f"[{style}]{text}[/]"
    return f"{icon} {text}" if icon else text


def _styled(text: str, style: str) -> str:
    """Apply custom style."""
    if plain_mode:
        return text
    return f"[{style}]{text}[/]"


def print_command(command: str, syntax: str = "bash") -> None:
    """Display generated command in a Rich Panel."""
    if plain_mode:
        console.print(command)
        return

    syntax_obj = Syntax(
        command,
        syntax,
        theme="monokai",
        word_wrap=True,
        indent_guides=False,
    )
    panel = Panel(
        syntax_obj,
        title="Generated Command",
        border_style=THEME["command_panel"]["border"],
        expand=False,
        padding=(0, 1),
    )
    console.print(panel)


def print_safety_status(risk: str, reason: str = "") -> None:
    """Display safety classification with appropriate styling."""
    if plain_mode:
        if reason:
            console.print(f"{risk.upper()}: {reason}")
        else:
            console.print(risk.upper())
        return

    theme = THEME.get(risk, THEME["unknown"])
    icon = theme.get("icon", "?")
    style = theme.get("style", "dim")

    if reason:
        console.print(f"{icon} [{style}]{risk.upper()}[/]: {reason}")
    else:
        console.print(f"{icon} [{style}]{risk.upper()}[/]")


def print_error(message: str) -> None:
    """Display error message."""
    console.print(_t(message, "error"))


def print_warning(message: str) -> None:
    """Display warning message."""
    console.print(_t(message, "warning"))


def print_success(message: str) -> None:
    """Display success message."""
    console.print(_t(message, "success"))


def print_info(message: str) -> None:
    """Display info message."""
    console.print(_t(message, "info"))


def print_generating() -> None:
    """Display generating message."""
    if plain_mode:
        console.print("Generating...")
    else:
        console.print("[dim]Generating...[/]")


def print_explaining() -> None:
    """Display explaining message."""
    if plain_mode:
        console.print("Explaining...")
    else:
        console.print("[dim]Explaining...[/]")


def prompt_execute() -> bool:
    """Prompt user for execution confirmation. Returns True if confirmed."""
    if plain_mode:
        answer = input("Execute? [Y/n]: ").strip().lower()
        return answer in ("", "y", "yes")
    return Confirm.ask("[cyan]Execute?[/]", default=True)


def prompt_confirm_warning() -> bool:
    """Prompt for WARNING confirmation. Returns True if confirmed with 'yes'."""
    if plain_mode:
        answer = input("Type 'yes' to confirm: ").strip().lower()
        return answer == "yes"
    answer = Prompt.ask("[yellow]Type 'yes' to confirm[/]", default="")
    return answer.lower() == "yes"


def print_explanation(command: str, explanation: str) -> None:
    """Display command explanation in structured format."""
    if plain_mode:
        console.print(f"Command: {command}")
        console.print(f"Explanation: {explanation}")
        return

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Label", style="cyan", width=20)
    table.add_column("Content")

    table.add_row("Command:", f"[bold]{command}[/]")
    table.add_row("Explanation:", explanation)

    console.print()
    console.print(table)
    console.print()


def print_unknown() -> None:
    """Display unknown/error message."""
    if plain_mode:
        console.print("ShellSpark couldn't generate a command for that request.")
        console.print("Try rephrasing with more detail.")
        return

    console.print("[dim]ShellSpark couldn't generate a command for that request.[/]")
    console.print("[dim]Try rephrasing with more detail.[/]")


def print_unsafe() -> None:
    """Display unsafe message."""
    if plain_mode:
        console.print("The AI flagged this request as unsafe.")
        console.print("Please rephrase to be more specific.")
        return

    console.print("[red]The AI flagged this request as unsafe.[/]")
    console.print("[red]Please rephrase to be more specific.[/]")


def print_blocked(reason: str) -> None:
    """Display blocked message."""
    if plain_mode:
        console.print(f"BLOCKED: {reason}")
        console.print("ShellSpark will not execute this command.")
        return

    console.print(f"[red]✕ BLOCKED: {reason}[/]")
    console.print("[red]ShellSpark will not execute this command.[/]")
