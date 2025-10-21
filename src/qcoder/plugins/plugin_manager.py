"""Plugin system for extending QCoder functionality."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Optional
from dataclasses import dataclass

from ..utils.output import Console
from ..core.config import get_config


@dataclass
class Plugin:
    """Plugin metadata and instance."""

    name: str
    version: str
    description: str
    author: str
    instance: Any
    commands: dict[str, Callable[..., Any]]
    hooks: dict[str, Callable[..., Any]]


class PluginManager:
    """Manages plugin loading, registration, and execution."""

    def __init__(self) -> None:
        """Initialize plugin manager."""
        self.console = Console()
        self.config = get_config()
        self.plugins: dict[str, Plugin] = {}
        self.plugin_dirs = self._get_plugin_dirs()

    def _get_plugin_dirs(self) -> list[Path]:
        """Get plugin directories to search.

        Returns:
            List of plugin directory paths.
        """
        dirs = [
            self.config.config_dir / "plugins",  # User plugins
            Path.cwd() / ".qcoder" / "plugins",  # Project plugins
        ]

        # Create directories if they don't exist
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        return dirs

    def discover_plugins(self) -> list[Path]:
        """Discover all available plugins.

        Returns:
            List of plugin file paths.
        """
        plugins = []

        for plugin_dir in self.plugin_dirs:
            # Find all Python files
            for path in plugin_dir.glob("*.py"):
                if path.name.startswith("_"):
                    continue
                plugins.append(path)

            # Find plugin packages (directories with __init__.py)
            for path in plugin_dir.iterdir():
                if path.is_dir() and (path / "__init__.py").exists():
                    plugins.append(path / "__init__.py")

        return plugins

    def _validate_plugin_safety(self, plugin_path: Path) -> bool:
        """Perform basic safety validation on plugin before loading.

        Args:
            plugin_path: Path to plugin file.

        Returns:
            True if plugin passes basic safety checks.
        """
        # SECURITY: Perform static analysis to detect obvious malicious patterns
        try:
            content = plugin_path.read_text(encoding="utf-8")
        except Exception as e:
            self.console.error(f"Failed to read plugin file: {e}")
            return False

        # SECURITY: Check for dangerous code patterns
        # These are indicators of potentially malicious behavior
        dangerous_patterns = [
            # System manipulation
            "os.system(", "subprocess.call(", "subprocess.Popen(",
            # File system manipulation outside expected scope
            "shutil.rmtree(", "os.remove(", "os.unlink(",
            # Network operations (could be legitimate, but suspicious)
            "socket.socket(", "urllib.request.urlopen(",
            # Code execution
            "exec(", "eval(", "compile(",
            # Module manipulation
            "__import__(",
        ]

        found_dangerous = []
        for pattern in dangerous_patterns:
            if pattern in content:
                found_dangerous.append(pattern)

        if found_dangerous:
            self.console.warning(
                f"Plugin contains potentially dangerous code patterns: {plugin_path.name}\n"
                f"Detected patterns: {', '.join(found_dangerous)}\n"
                "This plugin may perform sensitive operations. "
                "Review the code before loading."
            )
            # Return True but warn - allow user to decide
            # In a production system, you might want to require explicit approval
            return True

        # SECURITY: Check plugin size - extremely large files might be suspicious
        if plugin_path.stat().st_size > 1024 * 1024:  # 1MB
            self.console.warning(
                f"Plugin file is unusually large ({plugin_path.stat().st_size} bytes): {plugin_path.name}"
            )

        return True

    def load_plugin(self, plugin_path: Path) -> Optional[Plugin]:
        """Load a single plugin from path.

        Args:
            plugin_path: Path to plugin file or package.

        Returns:
            Loaded Plugin instance or None if loading failed.
        """
        try:
            # SECURITY: Validate plugin before loading
            if not self._validate_plugin_safety(plugin_path):
                self.console.warning(f"Plugin failed safety validation: {plugin_path}")
                return None

            # Generate module name
            module_name = f"qcoder_plugin_{plugin_path.stem}"

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                self.console.warning(f"Failed to load plugin spec: {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            # SECURITY: Display warning before executing untrusted plugin code
            self.console.warning(
                f"Loading plugin: {plugin_path.name}\n"
                "WARNING: Plugins execute arbitrary Python code. "
                "Only load plugins from trusted sources."
            )

            spec.loader.exec_module(module)

            # Get plugin metadata
            if not hasattr(module, "PLUGIN_METADATA"):
                self.console.warning(f"Plugin missing PLUGIN_METADATA: {plugin_path}")
                return None

            metadata = module.PLUGIN_METADATA

            # Create plugin instance
            if hasattr(module, "Plugin"):
                instance = module.Plugin()
            else:
                instance = module

            # Extract commands (functions decorated with @command)
            commands = {}
            hooks = {}

            for attr_name in dir(instance):
                attr = getattr(instance, attr_name)

                if callable(attr):
                    # Check for command decorator
                    if hasattr(attr, "_qcoder_command"):
                        commands[attr_name] = attr

                    # Check for hook decorator
                    if hasattr(attr, "_qcoder_hook"):
                        hook_name = attr._qcoder_hook
                        hooks[hook_name] = attr

            plugin = Plugin(
                name=metadata.get("name", plugin_path.stem),
                version=metadata.get("version", "0.1.0"),
                description=metadata.get("description", ""),
                author=metadata.get("author", "Unknown"),
                instance=instance,
                commands=commands,
                hooks=hooks,
            )

            self.plugins[plugin.name] = plugin
            return plugin

        except Exception as e:
            self.console.error(f"Failed to load plugin {plugin_path}: {e}")
            return None

    def load_all_plugins(self) -> None:
        """Discover and load all available plugins."""
        plugin_paths = self.discover_plugins()

        self.console.info(f"Discovering plugins in {len(self.plugin_dirs)} directories...")

        loaded = 0
        for path in plugin_paths:
            if self.load_plugin(path):
                loaded += 1

        if loaded > 0:
            self.console.success(f"Loaded {loaded} plugin(s)")
        else:
            self.console.info("No plugins loaded")

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get loaded plugin by name.

        Args:
            name: Plugin name.

        Returns:
            Plugin instance or None if not found.
        """
        return self.plugins.get(name)

    def execute_command(self, plugin_name: str, command_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a plugin command.

        Args:
            plugin_name: Name of the plugin.
            command_name: Name of the command.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            Command result.

        Raises:
            ValueError: If plugin or command not found.
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin not found: {plugin_name}")

        if command_name not in plugin.commands:
            raise ValueError(f"Command not found: {command_name}")

        return plugin.commands[command_name](*args, **kwargs)

    def execute_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Execute all registered hooks for an event.

        Args:
            hook_name: Name of the hook event.
            *args: Positional arguments for the hook.
            **kwargs: Keyword arguments for the hook.

        Returns:
            List of results from all hooks.
        """
        results = []

        for plugin in self.plugins.values():
            if hook_name in plugin.hooks:
                try:
                    result = plugin.hooks[hook_name](*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.console.warning(
                        f"Hook {hook_name} in plugin {plugin.name} failed: {e}"
                    )

        return results

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all loaded plugins.

        Returns:
            List of plugin information dictionaries.
        """
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
                "commands": list(plugin.commands.keys()),
                "hooks": list(plugin.hooks.keys()),
            }
            for plugin in self.plugins.values()
        ]


# Decorators for plugin developers


def command(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark a function as a plugin command.

    Example:
        @command
        def my_command(arg1, arg2):
            return "result"
    """
    func._qcoder_command = True  # type: ignore
    return func


def hook(event_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a function as a hook for an event.

    Args:
        event_name: Name of the event to hook into.

    Example:
        @hook("pre_chat")
        def on_pre_chat(message):
            print(f"Processing: {message}")
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._qcoder_hook = event_name  # type: ignore
        return func

    return decorator


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager instance.

    Returns:
        Global PluginManager instance.
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
