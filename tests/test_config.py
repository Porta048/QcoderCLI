"""Tests for configuration management."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
import yaml

from qcoder.core.config import Config, get_config


class TestConfigInitialization:
    """Test Config initialization and setup."""

    def test_config_creates_config_dir(self, tmp_path: Path) -> None:
        """Test that Config creates config directory if it doesn't exist."""
        config_dir = tmp_path / ".qcoder"
        assert not config_dir.exists()

        config = Config(config_dir=config_dir)

        assert config_dir.exists()
        assert config.config_dir == config_dir

    def test_config_uses_provided_config_dir(self, tmp_path: Path) -> None:
        """Test that Config uses provided config directory."""
        custom_dir = tmp_path / "custom_config"
        config = Config(config_dir=custom_dir)

        assert config.config_dir == custom_dir
        assert custom_dir.exists()

    @patch("qcoder.core.config.Path.home")
    def test_default_config_dir_windows(
        self, mock_home: Mock, tmp_path: Path
    ) -> None:
        """Test default config directory on Windows."""
        mock_home.return_value = tmp_path
        with patch("os.name", "nt"):
            config = Config()
            expected = tmp_path / ".qcoder"
            assert config.config_dir == expected

    @patch("qcoder.core.config.Path.home")
    def test_default_config_dir_unix(self, mock_home: Mock, tmp_path: Path) -> None:
        """Test default config directory on Unix-like systems."""
        mock_home.return_value = tmp_path
        with patch("os.name", "posix"):
            config = Config()
            expected = tmp_path / ".config" / "qcoder"
            assert config.config_dir == expected

    def test_config_loads_yaml_files(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test that Config loads YAML configuration files."""
        config = Config(config_dir=temp_config_dir)

        assert config.global_config is not None
        assert config.global_config.get("api_key") == "config-api-key"
        assert config.global_config.get("model") == "custom-model"

    def test_config_handles_missing_yaml_files(self, temp_config_dir: Path) -> None:
        """Test that Config handles missing YAML files gracefully."""
        config = Config(config_dir=temp_config_dir)

        assert config.global_config == {}
        assert config.project_config == {}

    def test_config_loads_context_files(
        self, temp_config_dir: Path, sample_context_file: Path
    ) -> None:
        """Test that Config loads context markdown files."""
        config = Config(config_dir=temp_config_dir)

        assert config.global_context
        assert "Test context file" in config.global_context
        assert "# Key Information" in config.global_context


class TestConfigGet:
    """Test Config.get() method with priority chain."""

    def test_get_from_environment_variable(self, temp_config_dir: Path) -> None:
        """Test getting configuration from environment variables."""
        with patch.dict(os.environ, {"QCODER_API_KEY": "env-api-key"}):
            config = Config(config_dir=temp_config_dir)
            assert config.get("api_key") == "env-api-key"

    def test_get_from_project_config(
        self, temp_config_dir: Path, temp_project_dir: Path
    ) -> None:
        """Test getting configuration from project config."""
        # Create project config
        project_qcoder_dir = temp_project_dir / ".qcoder"
        project_qcoder_dir.mkdir(parents=True, exist_ok=True)

        project_config_data = {"api_key": "project-api-key"}
        project_config_file = project_qcoder_dir / "config.yaml"
        with open(project_config_file, "w", encoding="utf-8") as f:
            yaml.dump(project_config_data, f)

        # Change to project directory
        with patch("pathlib.Path.cwd", return_value=temp_project_dir):
            config = Config(config_dir=temp_config_dir)
            assert config.get("api_key") == "project-api-key"

    def test_get_from_global_config(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test getting configuration from global config."""
        config = Config(config_dir=temp_config_dir)
        assert config.get("model") == "custom-model"

    def test_get_priority_chain_env_over_project(
        self, temp_config_dir: Path, temp_project_dir: Path
    ) -> None:
        """Test that environment variables have highest priority."""
        # Create project config
        project_qcoder_dir = temp_project_dir / ".qcoder"
        project_qcoder_dir.mkdir(parents=True, exist_ok=True)

        project_config_data = {"api_key": "project-api-key"}
        project_config_file = project_qcoder_dir / "config.yaml"
        with open(project_config_file, "w", encoding="utf-8") as f:
            yaml.dump(project_config_data, f)

        with patch("pathlib.Path.cwd", return_value=temp_project_dir):
            with patch.dict(os.environ, {"QCODER_API_KEY": "env-api-key"}):
                config = Config(config_dir=temp_config_dir)
                assert config.get("api_key") == "env-api-key"

    def test_get_default_value(self, temp_config_dir: Path) -> None:
        """Test that default values are returned when key not found."""
        config = Config(config_dir=temp_config_dir)
        assert config.get("nonexistent_key", "default_value") == "default_value"

    def test_get_none_default(self, temp_config_dir: Path) -> None:
        """Test that None is returned as default when not specified."""
        config = Config(config_dir=temp_config_dir)
        assert config.get("nonexistent_key") is None

    def test_get_converts_key_to_uppercase(self, temp_config_dir: Path) -> None:
        """Test that keys are converted to uppercase for env vars."""
        with patch.dict(os.environ, {"QCODER_LOG_LEVEL": "DEBUG"}):
            config = Config(config_dir=temp_config_dir)
            assert config.get("log_level") == "DEBUG"


class TestConfigProperties:
    """Test Config properties."""

    def test_api_key_property_from_config(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test api_key property retrieves from config."""
        config = Config(config_dir=temp_config_dir)
        assert config.api_key == "config-api-key"

    def test_api_key_property_from_env(self, temp_config_dir: Path) -> None:
        """Test api_key property retrieves from environment."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-api-key"}):
            config = Config(config_dir=temp_config_dir)
            assert config.api_key == "env-api-key"

    def test_api_key_property_raises_when_missing(
        self, temp_config_dir: Path
    ) -> None:
        """Test api_key property raises ValueError when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config(config_dir=temp_config_dir)
            with pytest.raises(ValueError) as exc_info:
                _ = config.api_key
            assert "API key not found" in str(exc_info.value)

    def test_model_property(self, temp_config_dir: Path, sample_yaml_config: Path) -> None:
        """Test model property returns correct value."""
        config = Config(config_dir=temp_config_dir)
        assert config.model == "custom-model"

    def test_model_property_default(self, temp_config_dir: Path) -> None:
        """Test model property returns default when not configured."""
        with patch.dict(os.environ, {"DEFAULT_MODEL": "default-model"}):
            config = Config(config_dir=temp_config_dir)
            assert config.model == "default-model"

    def test_github_token_property(self, temp_config_dir: Path) -> None:
        """Test github_token property returns correct value."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "github-token"}):
            config = Config(config_dir=temp_config_dir)
            assert config.github_token == "github-token"

    def test_github_token_property_none(self, temp_config_dir: Path) -> None:
        """Test github_token property returns None when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config(config_dir=temp_config_dir)
            assert config.github_token is None

    def test_conversation_dir_property(self, temp_config_dir: Path) -> None:
        """Test conversation_dir property creates directory."""
        config = Config(config_dir=temp_config_dir)
        conv_dir = config.conversation_dir

        assert conv_dir.exists()
        assert conv_dir.is_dir()

    def test_cache_dir_property(self, temp_config_dir: Path) -> None:
        """Test cache_dir property creates directory."""
        config = Config(config_dir=temp_config_dir)
        cache_dir = config.cache_dir

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_log_dir_property(self, temp_config_dir: Path) -> None:
        """Test log_dir property creates directory."""
        config = Config(config_dir=temp_config_dir)
        log_dir = config.log_dir

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_max_context_length_property(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test max_context_length property."""
        config = Config(config_dir=temp_config_dir)
        assert config.max_context_length == 16000

    def test_max_context_length_property_default(
        self, temp_config_dir: Path
    ) -> None:
        """Test max_context_length property returns default."""
        config = Config(config_dir=temp_config_dir)
        # Should return default of 8000
        assert config.max_context_length == 8000

    def test_log_level_property(self, temp_config_dir: Path, sample_yaml_config: Path) -> None:
        """Test log_level property."""
        config = Config(config_dir=temp_config_dir)
        assert config.log_level == "DEBUG"

    def test_log_level_property_default(self, temp_config_dir: Path) -> None:
        """Test log_level property returns default."""
        config = Config(config_dir=temp_config_dir)
        assert config.log_level == "INFO"

    def test_log_level_converts_to_uppercase(
        self, temp_config_dir: Path
    ) -> None:
        """Test log_level is converted to uppercase."""
        with patch.dict(os.environ, {"QCODER_LOG_LEVEL": "debug"}):
            config = Config(config_dir=temp_config_dir)
            assert config.log_level == "DEBUG"


class TestConfigContext:
    """Test Config context methods."""

    def test_get_context_no_files(self, temp_config_dir: Path) -> None:
        """Test get_context returns empty string when no context files."""
        config = Config(config_dir=temp_config_dir)
        assert config.get_context() == ""

    def test_get_context_global_only(
        self, temp_config_dir: Path, sample_context_file: Path
    ) -> None:
        """Test get_context returns global context."""
        config = Config(config_dir=temp_config_dir)
        context = config.get_context()

        assert "# Global Context" in context
        assert "Test context file" in context

    def test_get_context_combines_global_and_project(
        self, temp_config_dir: Path, temp_project_dir: Path, sample_context_file: Path
    ) -> None:
        """Test get_context combines global and project context."""
        # Create project context
        project_qcoder_dir = temp_project_dir / ".qcoder"
        project_qcoder_dir.mkdir(parents=True, exist_ok=True)

        project_context_file = project_qcoder_dir / "QCODER.md"
        with open(project_context_file, "w", encoding="utf-8") as f:
            f.write("# Project Context\n\nThis is project specific context.")

        with patch("pathlib.Path.cwd", return_value=temp_project_dir):
            config = Config(config_dir=temp_config_dir)
            context = config.get_context()

            assert "# Global Context" in context
            assert "# Project Context" in context


class TestConfigSave:
    """Test Config.save_config() method."""

    def test_save_config_global_scope(self, temp_config_dir: Path) -> None:
        """Test saving configuration to global scope."""
        config = Config(config_dir=temp_config_dir)
        new_config = {"api_key": "new-api-key", "model": "new-model"}

        config.save_config(new_config, global_scope=True)

        # Verify file was created
        config_file = temp_config_dir / "config.yaml"
        assert config_file.exists()

        # Verify content
        with open(config_file, "r", encoding="utf-8") as f:
            saved = yaml.safe_load(f)
        assert saved["api_key"] == "new-api-key"
        assert saved["model"] == "new-model"

    def test_save_config_project_scope(
        self, temp_config_dir: Path, temp_project_dir: Path
    ) -> None:
        """Test saving configuration to project scope."""
        with patch("pathlib.Path.cwd", return_value=temp_project_dir):
            config = Config(config_dir=temp_config_dir)
            new_config = {"api_key": "project-api-key"}

            config.save_config(new_config, global_scope=False)

            # Verify file was created in project
            project_config_file = temp_project_dir / ".qcoder" / "config.yaml"
            assert project_config_file.exists()

            # Verify content
            with open(project_config_file, "r", encoding="utf-8") as f:
                saved = yaml.safe_load(f)
            assert saved["api_key"] == "project-api-key"

    def test_save_config_overwrites_existing(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test that save_config overwrites existing configuration."""
        config = Config(config_dir=temp_config_dir)
        original_model = config.get("model")
        assert original_model == "custom-model"

        new_config = {"model": "overwritten-model"}
        config.save_config(new_config, global_scope=True)

        # Create new config instance to reload
        config2 = Config(config_dir=temp_config_dir)
        assert config2.get("model") == "overwritten-model"


class TestConfigValidation:
    """Test configuration validation."""

    def test_max_context_length_as_int(
        self, temp_config_dir: Path, sample_yaml_config: Path
    ) -> None:
        """Test that max_context_length is converted to int."""
        config = Config(config_dir=temp_config_dir)
        value = config.max_context_length
        assert isinstance(value, int)
        assert value == 16000

    def test_config_with_invalid_yaml(self, temp_config_dir: Path) -> None:
        """Test that invalid YAML is handled gracefully."""
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content:")

        # Should not raise, but return empty dict or handle gracefully
        config = Config(config_dir=temp_config_dir)
        assert config.global_config is not None


class TestGlobalConfigSingleton:
    """Test the global config singleton."""

    def test_get_config_returns_singleton(self, temp_config_dir: Path) -> None:
        """Test that get_config returns the same instance."""
        # Reset singleton
        import qcoder.core.config as config_module
        config_module._config = None

        with patch.object(Config, "__init__", return_value=None) as mock_init:
            config1 = get_config()
            config2 = get_config()

            assert config1 is config2
            # Should only initialize once
            assert mock_init.call_count == 1

    def test_get_config_creates_instance_if_none(self, temp_config_dir: Path) -> None:
        """Test that get_config creates instance if none exists."""
        # Reset singleton
        import qcoder.core.config as config_module
        config_module._config = None

        with patch.object(Config, "__init__", return_value=None):
            config = get_config()
            assert config is not None


class TestPathResolution:
    """Test path resolution in config."""

    def test_conversation_dir_custom_path(self, temp_config_dir: Path) -> None:
        """Test custom conversation directory path."""
        custom_conv_dir = temp_config_dir / "custom_conversations"
        custom_conv_dir.mkdir(parents=True, exist_ok=True)

        config_data = {"conversation_history_dir": str(custom_conv_dir)}
        config_file = temp_config_dir / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = Config(config_dir=temp_config_dir)
        assert config.conversation_dir == custom_conv_dir

    def test_directories_are_created_automatically(self, temp_config_dir: Path) -> None:
        """Test that accessing directory properties creates them."""
        config = Config(config_dir=temp_config_dir)

        # These should all exist after accessing properties
        assert config.conversation_dir.exists()
        assert config.cache_dir.exists()
        assert config.log_dir.exists()
