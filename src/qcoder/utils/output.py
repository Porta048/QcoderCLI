"""Console output utilities using Rich for beautiful terminal output."""

from typing import Any, Optional
from rich.console import Console as RichConsole
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm


class Console:
    """Enhanced console output with Rich formatting."""

    def __init__(self) -> None:
        """Initialize console."""
        self.console = RichConsole()

    def print(self, text: str, **kwargs: Any) -> None:
        """Print plain text.

        Args:
            text: Text to print.
            **kwargs: Additional Rich console print arguments.
        """
        self.console.print(text, **kwargs)

    def print_markdown(self, text: str) -> None:
        """Print formatted markdown text.

        Args:
            text: Markdown text to print.
        """
        md = Markdown(text)
        self.console.print(md)

    def print_code(
        self,
        code: str,
        language: str = "python",
        line_numbers: bool = True,
        theme: str = "monokai",
    ) -> None:
        """Print syntax-highlighted code.

        Args:
            code: Code to print.
            language: Programming language for syntax highlighting.
            line_numbers: Whether to show line numbers.
            theme: Color theme for syntax highlighting.
        """
        syntax = Syntax(code, language, line_numbers=line_numbers, theme=theme)
        self.console.print(syntax)

    def print_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        title: Optional[str] = None,
    ) -> None:
        """Print a formatted table.

        Args:
            headers: Column headers.
            rows: Table rows.
            title: Optional table title.
        """
        table = Table(title=title, show_header=True, header_style="bold cyan")

        for header in headers:
            table.add_column(header)

        for row in rows:
            table.add_row(*row)

        self.console.print(table)

    def print_dict(self, data: dict[str, Any], title: Optional[str] = None) -> None:
        """Print a dictionary as formatted output.

        Args:
            data: Dictionary to print.
            title: Optional title.
        """
        if title:
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")

        for key, value in data.items():
            self.console.print(f"  [yellow]{key}:[/yellow] {value}")

    def print_panel(
        self,
        text: str,
        title: Optional[str] = None,
        border_style: str = "blue",
    ) -> None:
        """Print text in a bordered panel.

        Args:
            text: Text to display in panel.
            title: Optional panel title.
            border_style: Border color style.
        """
        panel = Panel(text, title=title, border_style=border_style)
        self.console.print(panel)

    def success(self, text: str) -> None:
        """Print success message.

        Args:
            text: Success message.
        """
        self.console.print(f"[bold green]✓[/bold green] {text}")

    def error(self, text: str) -> None:
        """Print error message.

        Args:
            text: Error message.
        """
        self.console.print(f"[bold red]✗[/bold red] {text}", style="red")

    def warning(self, text: str) -> None:
        """Print warning message.

        Args:
            text: Warning message.
        """
        self.console.print(f"[bold yellow]⚠[/bold yellow] {text}")

    def info(self, text: str) -> None:
        """Print info message.

        Args:
            text: Info message.
        """
        self.console.print(f"[bold blue]ℹ[/bold blue] {text}")

    def prompt(self, text: str, default: str = "") -> str:
        """Prompt user for input.

        Args:
            text: Prompt text.
            default: Default value.

        Returns:
            User input string.
        """
        return Prompt.ask(text, default=default, console=self.console)

    def confirm(self, text: str, default: bool = False) -> bool:
        """Prompt user for yes/no confirmation.

        Args:
            text: Confirmation question.
            default: Default answer.

        Returns:
            True if user confirms, False otherwise.
        """
        return Confirm.ask(text, default=default, console=self.console)

    def spinner(self, text: str = "Processing...") -> Progress:
        """Create a spinner progress indicator.

        Args:
            text: Text to display with spinner.

        Returns:
            Progress context manager.
        """
        return Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            console=self.console,
            transient=True,
        )

    def rule(self, text: str = "", style: str = "blue") -> None:
        """Print a horizontal rule.

        Args:
            text: Optional text to display in the rule.
            style: Rule color style.
        """
        self.console.rule(text, style=style)

    def clear(self) -> None:
        """Clear the console screen."""
        self.console.clear()

    def print_user_message(self, message: str) -> None:
        """Print a user message in chat format.

        Args:
            message: User message content.
        """
        self.console.print(f"\n[bold cyan]You:[/bold cyan] {message}")

    def print_assistant_message(self, message: str) -> None:
        """Print an assistant message in chat format.

        Args:
            message: Assistant message content.
        """
        self.console.print(f"\n[bold green]QCoder:[/bold green]")
        self.print_markdown(message)

    def print_system_message(self, message: str) -> None:
        """Print a system message.

        Args:
            message: System message content.
        """
        self.console.print(f"\n[dim italic]{message}[/dim italic]")
