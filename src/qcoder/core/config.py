"""Configuration management for QCoder CLI."""

import os
import threading
from pathlib import Path
from typing import Any, Optional
import yaml
from dotenv import load_dotenv

from ..utils.validators import validate_api_key


class Config:
    """Manages configuration from environment variables, config files, and defaults."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize configuration manager.

        Args:
            config_dir: Optional custom config directory path.
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables
        load_dotenv()

        # Load configuration files
        self.global_config = self._load_config(self.config_dir / "config.yaml")
        self.project_config = self._load_config(Path.cwd() / ".qcoder" / "config.yaml")

        # Load custom context files
        self.global_context = self._load_context(self.config_dir / "QCODER.md")
        self.project_context = self._load_context(Path.cwd() / ".qcoder" / "QCODER.md")

    @staticmethod
    def _get_default_config_dir() -> Path:
        """Get the default configuration directory based on OS.

        Returns:
            Path to the default config directory.
        """
        home = Path.home()
        if os.name == "nt":  # Windows
            return home / ".qcoder"
        return home / ".config" / "qcoder"

    def _load_config(self, path: Path) -> dict[str, Any]:
        """Load YAML configuration file.

        Args:
            path: Path to config file.

        Returns:
            Configuration dictionary or empty dict if file doesn't exist.
        """
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            return {}

    def _load_context(self, path: Path) -> str:
        """Load markdown context file.

        Args:
            path: Path to context file.

        Returns:
            Context file contents or empty string if file doesn't exist.
        """
        if not path.exists():
            return ""

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to load context from {path}: {e}")
            return ""

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback chain.

        Priority: Environment > Project Config > Global Config > Default

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value.
        """
        # Check environment variables (uppercase with prefix)
        env_key = f"QCODER_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Check project config
        if key in self.project_config:
            return self.project_config[key]

        # Check global config
        if key in self.global_config:
            return self.global_config[key]

        return default

    def get_context(self) -> str:
        """Get combined context from global and project context files.

        Returns:
            Combined context string.
        """
        contexts = []
        if self.global_context:
            contexts.append("# Global Context\n" + self.global_context)
        if self.project_context:
            contexts.append("# Project Context\n" + self.project_context)
        return "\n\n".join(contexts)

    @property
    def api_key(self) -> str:
        """Get OpenRouter API key.

        Returns:
            Validated API key from environment or config.

        Raises:
            ValueError: If API key is not configured or invalid.
        """
        key = self.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
                "or configure it in ~/.qcoder/config.yaml"
            )

        try:
            return validate_api_key(key)
        except Exception as e:
            raise ValueError(
                f"Invalid OpenRouter API key: {e}. "
                "Please check your API key configuration."
            ) from e

    @property
    def model(self) -> str:
        """Get the AI model to use.

        Returns:
            Model identifier.
        """
        return self.get("model") or os.getenv("DEFAULT_MODEL", "qwen/qwen3-coder:free")

    @property
    def github_token(self) -> Optional[str]:
        """Get GitHub personal access token.

        Returns:
            GitHub token or None if not configured.
        """
        return self.get("github_token") or os.getenv("GITHUB_TOKEN")

    @property
    def conversation_dir(self) -> Path:
        """Get directory for storing conversation checkpoints.

        Returns:
            Path to conversation directory.
        """
        dir_path = Path(
            self.get("conversation_history_dir", str(self.config_dir / "conversations"))
        )
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @property
    def cache_dir(self) -> Path:
        """Get directory for caching data.

        Returns:
            Path to cache directory.
        """
        dir_path = self.config_dir / "cache"
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @property
    def log_dir(self) -> Path:
        """Get directory for log files.

        Returns:
            Path to log directory.
        """
        dir_path = self.config_dir / "logs"
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @property
    def max_context_length(self) -> int:
        """Get maximum context length for conversations.

        Returns:
            Maximum context length in tokens.
        """
        return int(self.get("max_context_length", 8000))

    @property
    def log_level(self) -> str:
        """Get logging level.

        Returns:
            Log level string (DEBUG, INFO, WARNING, ERROR).
        """
        return self.get("log_level", "INFO").upper()

    def save_config(self, config: dict[str, Any], global_scope: bool = False) -> None:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save.
            global_scope: If True, save to global config; otherwise save to project config.
        """
        if global_scope:
            config_path = self.config_dir / "config.yaml"
        else:
            project_dir = Path.cwd() / ".qcoder"
            project_dir.mkdir(parents=True, exist_ok=True)
            config_path = project_dir / "config.yaml"

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False)


# Global config instance with thread-safe initialization
_config: Optional[Config] = None
_config_lock = threading.Lock()


def get_config() -> Config:
    """Get or create global config instance with thread-safe initialization.

    Uses double-checked locking pattern for thread safety.

    Returns:
        Global Config instance.
    """
    global _config
    # First check (without lock for performance)
    if _config is None:
        # Acquire lock for initialization
        with _config_lock:
            # Second check (with lock to prevent race condition)
            if _config is None:
                _config = Config()
    return _config
