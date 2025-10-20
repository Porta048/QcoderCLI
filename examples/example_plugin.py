"""Example QCoder Plugin

This demonstrates how to create a custom plugin for QCoder CLI.
Place this file in ~/.qcoder/plugins/ or .qcoder/plugins/
"""

from pathlib import Path
from typing import Any

# Required: Plugin metadata
PLUGIN_METADATA = {
    "name": "example_plugin",
    "version": "1.0.0",
    "description": "Example plugin demonstrating QCoder plugin capabilities",
    "author": "QCoder Team",
}


# Import plugin decorators
try:
    from qcoder.plugins.plugin_manager import command, hook
    from qcoder.utils.output import Console
except ImportError:
    print("Warning: QCoder not installed. Plugin decorators unavailable.")

    # Fallback decorators for development
    def command(func):
        return func

    def hook(event_name):
        def decorator(func):
            return func

        return decorator


class Plugin:
    """Main plugin class. This is optional but recommended for organization."""

    def __init__(self):
        """Initialize plugin."""
        try:
            self.console = Console()
        except:
            self.console = None

    @command
    def hello(self, name: str = "World") -> str:
        """Say hello to someone.

        Args:
            name: Name to greet.

        Returns:
            Greeting message.
        """
        message = f"Hello, {name}! This is an example plugin command."
        if self.console:
            self.console.success(message)
        return message

    @command
    def count_files(self, directory: str = ".") -> dict[str, Any]:
        """Count files in a directory by extension.

        Args:
            directory: Directory path to analyze.

        Returns:
            Dictionary of file counts by extension.
        """
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return {"error": f"Invalid directory: {directory}"}

        counts: dict[str, int] = {}
        for file in path.rglob("*"):
            if file.is_file():
                ext = file.suffix or "no_extension"
                counts[ext] = counts.get(ext, 0) + 1

        if self.console:
            self.console.print_dict(counts, title=f"File counts in {directory}")

        return counts

    @command
    def generate_project_summary(self) -> str:
        """Generate a summary of the current project.

        Returns:
            Project summary as markdown.
        """
        cwd = Path.cwd()
        summary_parts = [
            f"# Project Summary: {cwd.name}\n",
            f"**Location**: {cwd}\n",
        ]

        # Count files
        file_counts = {}
        total_files = 0
        for file in cwd.rglob("*"):
            if file.is_file() and not any(part.startswith(".") for part in file.parts):
                total_files += 1
                ext = file.suffix or "no_extension"
                file_counts[ext] = file_counts.get(ext, 0) + 1

        summary_parts.append(f"\n**Total Files**: {total_files}\n")
        summary_parts.append("\n**File Types**:\n")
        for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary_parts.append(f"- {ext}: {count}\n")

        # Check for common project files
        common_files = [
            "README.md",
            "setup.py",
            "pyproject.toml",
            "package.json",
            "Cargo.toml",
            "go.mod",
        ]
        found_files = [f for f in common_files if (cwd / f).exists()]

        if found_files:
            summary_parts.append("\n**Project Files Found**:\n")
            for file in found_files:
                summary_parts.append(f"- {file}\n")

        summary = "".join(summary_parts)

        if self.console:
            self.console.print_markdown(summary)

        return summary

    @hook("pre_chat")
    def on_pre_chat(self, message: str) -> None:
        """Hook that runs before each chat message.

        Args:
            message: User's chat message.
        """
        # Example: Log the message or perform preprocessing
        if self.console:
            self.console.info(f"[Plugin] Processing message of length: {len(message)}")

    @hook("post_chat")
    def on_post_chat(self, response: str) -> None:
        """Hook that runs after each AI response.

        Args:
            response: AI's response.
        """
        # Example: Post-process the response or log analytics
        word_count = len(response.split())
        if self.console:
            self.console.info(f"[Plugin] AI response word count: {word_count}")

    @hook("on_file_operation")
    def on_file_operation(self, operation: str, path: str) -> None:
        """Hook that runs when file operations are performed.

        Args:
            operation: Type of operation (read, write, delete).
            path: File path.
        """
        if self.console:
            self.console.info(f"[Plugin] File operation: {operation} on {path}")


# Module-level functions also work (without the Plugin class)


@command
def simple_command(text: str) -> str:
    """A simple module-level command.

    Args:
        text: Text to process.

    Returns:
        Processed text.
    """
    return f"Processed: {text.upper()}"


# Example of how to use the plugin programmatically
if __name__ == "__main__":
    # Test the plugin
    plugin = Plugin()
    print(plugin.hello("Developer"))
    print(plugin.count_files("."))
    print(plugin.generate_project_summary())
