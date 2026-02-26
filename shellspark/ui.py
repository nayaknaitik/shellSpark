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


console = Console()


def print_command(command: str, syntax: str = "bash") -> None:
    """Display generated command in a Rich Panel."""
    syntax_obj = Syntax(command, syntax, theme="monokai", word_wrap=True)
    panel = Panel(
        syntax_obj,
        title="Generated Command",
        border_style="blue",
        expand=False,
    )
    console.print(panel)


def print_safety_status(risk: str, reason: str = "") -> None:
    """Display safety classification with appropriate styling."""
    if risk == "safe":
        style = "green"
        icon = "✅"
    elif risk == "warning":
        style = "yellow"
        icon = "⚠️"
    elif risk == "blocked":
        style = "red"
        icon = "🚫"
    else:
        style = "dim"
        icon = "❓"

    if reason:
        console.print(f"{icon} [{style}]{risk.upper()}[/]: {reason}")
    else:
        console.print(f"{icon} [{style}]{risk.upper()}[/]")


def print_error(message: str) -> None:
    """Display error message."""
    console.print(f"[red]❌ {message}[/]")


def print_warning(message: str) -> None:
    """Display warning message."""
    console.print(f"[yellow]⚠️  {message}[/]")


def print_success(message: str) -> None:
    """Display success message."""
    console.print(f"[green]✅ {message}[/]")


def print_info(message: str) -> None:
    """Display info message."""
    console.print(f"[blue]ℹ️  {message}[/]")


def print_generating() -> None:
    """Display generating message."""
    console.print("[dim]⏳ Generating...[/]")


def print_explaining() -> None:
    """Display explaining message."""
    console.print("[dim]⏳ Explaining...[/]")


def prompt_execute() -> bool:
    """Prompt user for execution confirmation. Returns True if confirmed."""
    return Confirm.ask("[cyan]Execute?[/]", default=True)


def prompt_confirm_warning() -> bool:
    """Prompt for WARNING confirmation. Returns True if confirmed with 'yes'."""
    answer = Prompt.ask("[yellow]Type 'yes' to confirm[/]", default="")
    return answer.lower() == "yes"


def print_explanation(command: str, explanation: str) -> None:
    """Display command explanation in a Table."""
    table = Table(title="Command Explanation", show_header=False, box=None)
    table.add_column("Label", style="cyan", width=20)
    table.add_column("Content")

    table.add_row("Command:", f"[bold]{command}[/]")
    table.add_row("Explanation:", explanation)

    console.print(table)


def print_unknown() -> None:
    """Display unknown/error message."""
    console.print("[dim]❓ ShellSpark couldn't generate a command for that request.[/]")
    console.print("[dim]   Try rephrasing with more detail.[/]")


def print_unsafe() -> None:
    """Display unsafe message."""
    console.print("[red]⚠️  The AI flagged this request as unsafe.[/]")
    console.print("[red]   Please rephrase to be more specific.[/]")


def print_blocked(reason: str) -> None:
    """Display blocked message."""
    console.print(f"[red]🚫 BLOCKED: {reason}[/]")
    console.print("[red]   ShellSpark will not execute this command.[/]")
    console.print(
        "[dim]   If you need to run this, do it manually with full awareness.[/]"
    )
