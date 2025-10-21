"""Pytest configuration and shared fixtures for QCoder CLI tests."""

import json
import os
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Iterator[Path]:
    """Create a temporary config directory for testing.

    Args:
        tmp_path: Pytest's tmp_path fixture.

    Yields:
        Path to temporary config directory.
    """
    config_dir = tmp_path / ".qcoder"
    config_dir.mkdir(parents=True, exist_ok=True)
    yield config_dir


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Iterator[Path]:
    """Create a temporary project directory for testing.

    Args:
        tmp_path: Pytest's tmp_path fixture.

    Yields:
        Path to temporary project directory.
    """
    project_dir = tmp_path / "project"
    project_dir.mkdir(parents=True, exist_ok=True)
    yield project_dir


@pytest.fixture
def mock_config(temp_config_dir: Path, monkeypatch) -> Mock:
    """Create a mock Config object.

    Args:
        temp_config_dir: Fixture for temporary config directory.
        monkeypatch: Pytest's monkeypatch fixture.

    Returns:
        Mock Config object.
    """
    mock_cfg = Mock()
    mock_cfg.config_dir = temp_config_dir
    mock_cfg.conversation_dir = temp_config_dir / "conversations"
    mock_cfg.cache_dir = temp_config_dir / "cache"
    mock_cfg.log_dir = temp_config_dir / "logs"
    mock_cfg.api_key = "test-api-key-12345"
    mock_cfg.model = "test-model"
    mock_cfg.github_token = "test-github-token"
    mock_cfg.max_context_length = 8000
    mock_cfg.log_level = "INFO"
    mock_cfg.global_config = {}
    mock_cfg.project_config = {}
    mock_cfg.global_context = ""
    mock_cfg.project_context = ""

    # Create directories
    mock_cfg.conversation_dir.mkdir(parents=True, exist_ok=True)
    mock_cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    mock_cfg.log_dir.mkdir(parents=True, exist_ok=True)

    return mock_cfg


@pytest.fixture
def mock_ai_client() -> Mock:
    """Create a mock AIClient object.

    Returns:
        Mock AIClient object.
    """
    mock_client = Mock()
    mock_client.api_key = "test-api-key"
    mock_client.model = "test-model"

    # Mock chat response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response from AI"

    mock_client.chat.return_value = mock_response
    mock_client.extract_text_response.return_value = "Test response from AI"
    mock_client.count_tokens.return_value = 10
    mock_client.get_models.return_value = [
        {"id": "model-1", "name": "Model 1", "context_length": 4096},
        {"id": "model-2", "name": "Model 2", "context_length": 8192},
    ]

    return mock_client


@pytest.fixture
def sample_yaml_config(temp_config_dir: Path) -> Path:
    """Create a sample YAML config file.

    Args:
        temp_config_dir: Fixture for temporary config directory.

    Returns:
        Path to created config file.
    """
    config_data = {
        "api_key": "sk-or-v1-testconfigapikey12345678",
        "model": "custom-model",
        "log_level": "DEBUG",
        "max_context_length": 16000,
    }

    config_file = temp_config_dir / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    return config_file


@pytest.fixture
def sample_context_file(temp_config_dir: Path) -> Path:
    """Create a sample context markdown file.

    Args:
        temp_config_dir: Fixture for temporary config directory.

    Returns:
        Path to created context file.
    """
    context_content = """# QCoder Context

This is a test context file.

## Key Information
- Project: Test Project
- Language: Python
- Version: 1.0
"""

    context_file = temp_config_dir / "QCODER.md"
    with open(context_file, "w", encoding="utf-8") as f:
        f.write(context_content)

    return context_file


@pytest.fixture
def sample_python_file(temp_project_dir: Path) -> Path:
    """Create a sample Python file for testing.

    Args:
        temp_project_dir: Fixture for temporary project directory.

    Returns:
        Path to created Python file.
    """
    code_content = '''def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
'''

    py_file = temp_project_dir / "math_utils.py"
    with open(py_file, "w", encoding="utf-8") as f:
        f.write(code_content)

    return py_file


@pytest.fixture
def sample_json_file(temp_project_dir: Path) -> Path:
    """Create a sample JSON file for testing.

    Args:
        temp_project_dir: Fixture for temporary project directory.

    Returns:
        Path to created JSON file.
    """
    data = {
        "name": "Test Project",
        "version": "1.0.0",
        "description": "A test project",
        "tags": ["test", "sample"],
    }

    json_file = temp_project_dir / "data.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return json_file


@pytest.fixture
def sample_checkpoint_data() -> dict[str, Any]:
    """Create sample checkpoint data for testing.

    Returns:
        Dictionary containing checkpoint data.
    """
    return {
        "conversation_id": "20240101_120000_000000",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
                "timestamp": "2024-01-01T12:00:00",
                "metadata": {},
            },
            {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T12:00:01",
                "metadata": {},
            },
            {
                "role": "assistant",
                "content": "I'm doing well, thank you for asking!",
                "timestamp": "2024-01-01T12:00:02",
                "metadata": {},
            },
        ],
        "metadata": {
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:02",
        },
        "max_context_length": 8000,
    }


@pytest.fixture
def saved_checkpoint(mock_config: Mock, sample_checkpoint_data: dict) -> Path:
    """Create a saved checkpoint file.

    Args:
        mock_config: Fixture for mock config.
        sample_checkpoint_data: Fixture for sample checkpoint data.

    Returns:
        Path to saved checkpoint file.
    """
    checkpoint_path = mock_config.conversation_dir / "test_checkpoint.json"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(sample_checkpoint_data, f, indent=2)

    return checkpoint_path


@pytest.fixture
def env_setup(monkeypatch, temp_config_dir: Path) -> None:
    """Set up environment for testing.

    Args:
        monkeypatch: Pytest's monkeypatch fixture.
        temp_config_dir: Fixture for temporary config directory.
    """
    # Set test environment variables
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-env-api-key")
    monkeypatch.setenv("GITHUB_TOKEN", "test-env-github-token")
    monkeypatch.setenv("DEFAULT_MODEL", "test-model")
    monkeypatch.setenv("HOME", str(temp_config_dir.parent))


@pytest.fixture(autouse=True)
def reset_config_singleton() -> Iterator[None]:
    """Reset the global config singleton between tests.

    Yields:
        None
    """
    # Save original config
    import qcoder.core.config as config_module

    original_config = config_module._config

    yield

    # Restore original config
    config_module._config = original_config


@pytest.fixture(autouse=True)
def reset_ai_client_singleton() -> Iterator[None]:
    """Reset the global AI client singleton between tests.

    Yields:
        None
    """
    # Save original client
    import qcoder.core.ai_client as ai_client_module

    original_client = ai_client_module._ai_client

    yield

    # Restore original client
    ai_client_module._ai_client = original_client
