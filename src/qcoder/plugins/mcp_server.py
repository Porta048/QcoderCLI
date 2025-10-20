"""MCP (Model Context Protocol) server implementation for context extensions."""

import json
from typing import Any, Optional
from pathlib import Path

from ..utils.output import Console
from ..core.config import get_config


class MCPServer:
    """MCP Server for providing extended context to AI models.

    The Model Context Protocol allows extending the AI's context with
    external data sources, tools, and capabilities.
    """

    def __init__(self) -> None:
        """Initialize MCP server."""
        self.console = Console()
        self.config = get_config()
        self.context_providers: dict[str, Any] = {}
        self.tools: dict[str, Any] = {}

    def register_context_provider(
        self,
        name: str,
        provider: Any,
        description: str = "",
    ) -> None:
        """Register a context provider.

        Args:
            name: Provider name.
            provider: Provider callable that returns context string.
            description: Provider description.
        """
        self.context_providers[name] = {
            "provider": provider,
            "description": description,
        }

    def register_tool(
        self,
        name: str,
        tool: Any,
        description: str = "",
        parameters: Optional[dict[str, Any]] = None,
    ) -> None:
        """Register a tool that the AI can use.

        Args:
            name: Tool name.
            tool: Tool callable.
            description: Tool description.
            parameters: JSON schema for tool parameters.
        """
        self.tools[name] = {
            "tool": tool,
            "description": description,
            "parameters": parameters or {},
        }

    def get_context(self, provider_name: str, **kwargs: Any) -> str:
        """Get context from a registered provider.

        Args:
            provider_name: Name of the context provider.
            **kwargs: Arguments to pass to the provider.

        Returns:
            Context string from the provider.

        Raises:
            ValueError: If provider not found.
        """
        if provider_name not in self.context_providers:
            raise ValueError(f"Context provider not found: {provider_name}")

        provider = self.context_providers[provider_name]["provider"]
        return provider(**kwargs)

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a registered tool.

        Args:
            tool_name: Name of the tool.
            **kwargs: Tool parameters.

        Returns:
            Tool execution result.

        Raises:
            ValueError: If tool not found.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]["tool"]
        return tool(**kwargs)

    def get_available_contexts(self) -> list[dict[str, Any]]:
        """Get list of available context providers.

        Returns:
            List of context provider information.
        """
        return [
            {
                "name": name,
                "description": info["description"],
            }
            for name, info in self.context_providers.items()
        ]

    def get_available_tools(self) -> list[dict[str, Any]]:
        """Get list of available tools.

        Returns:
            List of tool information.
        """
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"],
            }
            for name, info in self.tools.items()
        ]

    def save_config(self, config_path: Optional[Path] = None) -> None:
        """Save MCP server configuration.

        Args:
            config_path: Optional path to save config. Uses default if None.
        """
        if not config_path:
            config_path = self.config.config_dir / "mcp_config.json"

        config_data = {
            "context_providers": [
                {"name": name, "description": info["description"]}
                for name, info in self.context_providers.items()
            ],
            "tools": [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"],
                }
                for name, info in self.tools.items()
            ],
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        self.console.success(f"MCP configuration saved to: {config_path}")


# Built-in context providers


def file_tree_context(root_path: str = ".", max_depth: int = 3) -> str:
    """Provide file tree context.

    Args:
        root_path: Root directory path.
        max_depth: Maximum depth to traverse.

    Returns:
        File tree as string.
    """
    from pathlib import Path

    def build_tree(path: Path, prefix: str = "", depth: int = 0) -> list[str]:
        if depth >= max_depth:
            return []

        lines = []
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return []

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            lines.append(f"{prefix}{connector}{entry.name}")

            if entry.is_dir() and not entry.name.startswith("."):
                extension = "    " if is_last else "│   "
                lines.extend(build_tree(entry, prefix + extension, depth + 1))

        return lines

    root = Path(root_path)
    tree_lines = [str(root)] + build_tree(root)
    return "\n".join(tree_lines)


def git_status_context() -> str:
    """Provide Git status context.

    Returns:
        Git status information.
    """
    import subprocess

    try:
        # Get git status
        status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Get current branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        context = f"Current Branch: {branch.stdout.strip()}\n\n"
        context += "Status:\n" + (status.stdout or "Working tree clean")

        return context

    except Exception as e:
        return f"Git context unavailable: {e}"


def recent_files_context(days: int = 7, limit: int = 20) -> str:
    """Provide context about recently modified files.

    Args:
        days: Number of days to look back.
        limit: Maximum number of files.

    Returns:
        Recent files information.
    """
    from pathlib import Path
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=days)
    recent_files = []

    for path in Path.cwd().rglob("*"):
        if path.is_file() and not any(part.startswith(".") for part in path.parts):
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime > cutoff:
                    recent_files.append((mtime, path))
            except OSError:
                continue

    recent_files.sort(reverse=True)
    recent_files = recent_files[:limit]

    if not recent_files:
        return "No recently modified files found."

    lines = [f"Files modified in the last {days} days:\n"]
    for mtime, path in recent_files:
        lines.append(f"- {path.relative_to(Path.cwd())} ({mtime.strftime('%Y-%m-%d %H:%M')})")

    return "\n".join(lines)


# Global MCP server instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get or create global MCP server instance.

    Returns:
        Global MCPServer instance.
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()

        # Register built-in context providers
        _mcp_server.register_context_provider(
            "file_tree",
            file_tree_context,
            "Provides project file tree structure",
        )

        _mcp_server.register_context_provider(
            "git_status",
            git_status_context,
            "Provides current Git repository status",
        )

        _mcp_server.register_context_provider(
            "recent_files",
            recent_files_context,
            "Provides list of recently modified files",
        )

    return _mcp_server
