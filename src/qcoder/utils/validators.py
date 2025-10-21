"""Input validation utilities for QCoder CLI.

Provides reusable validation functions for common input types
across the application.
"""

import re
from typing import Any, Optional


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def validate_api_key(api_key: str) -> str:
    """Validate API key format.

    Args:
        api_key: The API key to validate.

    Returns:
        The validated and sanitized API key.

    Raises:
        ValidationError: If API key is invalid.
    """
    if not api_key:
        raise ValidationError("API key cannot be empty")

    # Strip whitespace
    api_key = api_key.strip()

    if not api_key:
        raise ValidationError("API key cannot be empty or whitespace only")

    # Check minimum length
    if len(api_key) < 20:
        raise ValidationError(
            f"API key is too short (got {len(api_key)} characters, expected at least 20)"
        )

    # Check for suspicious characters
    if any(char.isspace() for char in api_key):
        raise ValidationError("API key contains whitespace characters")

    return api_key


def validate_temperature(temperature: float) -> float:
    """Validate temperature parameter for AI models.

    Args:
        temperature: Temperature value to validate.

    Returns:
        The validated temperature.

    Raises:
        ValidationError: If temperature is out of valid range.
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError(
            f"Temperature must be a number, got {type(temperature).__name__}"
        )

    if not 0.0 <= temperature <= 2.0:
        raise ValidationError(
            f"Temperature must be between 0.0 and 2.0, got {temperature}"
        )

    return float(temperature)


def validate_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """Validate chat messages structure.

    Args:
        messages: List of message dictionaries to validate.

    Returns:
        The validated messages.

    Raises:
        ValidationError: If messages structure is invalid.
    """
    if not messages:
        raise ValidationError("Messages list cannot be empty")

    if not isinstance(messages, list):
        raise ValidationError(
            f"Messages must be a list, got {type(messages).__name__}"
        )

    valid_roles = {"system", "user", "assistant"}

    for i, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValidationError(
                f"Message at index {i} must be a dictionary, got {type(message).__name__}"
            )

        if "role" not in message:
            raise ValidationError(f"Message at index {i} is missing 'role' field")

        if "content" not in message:
            raise ValidationError(f"Message at index {i} is missing 'content' field")

        role = message["role"]
        if role not in valid_roles:
            raise ValidationError(
                f"Message at index {i} has invalid role '{role}'. "
                f"Valid roles are: {', '.join(sorted(valid_roles))}"
            )

        if not isinstance(message["content"], str):
            raise ValidationError(
                f"Message at index {i} content must be a string, "
                f"got {type(message['content']).__name__}"
            )

    return messages


def validate_glob_pattern(pattern: str) -> str:
    """Validate glob pattern syntax.

    Args:
        pattern: Glob pattern to validate.

    Returns:
        The validated pattern.

    Raises:
        ValidationError: If pattern is invalid.
    """
    if not pattern:
        raise ValidationError("Glob pattern cannot be empty")

    if not isinstance(pattern, str):
        raise ValidationError(
            f"Glob pattern must be a string, got {type(pattern).__name__}"
        )

    # Check for dangerous patterns
    dangerous_patterns = ["/../", "\\..\\", ".."]
    if any(danger in pattern for danger in dangerous_patterns):
        raise ValidationError(
            f"Glob pattern contains potentially dangerous path traversal: {pattern}"
        )

    # Basic syntax validation
    # Check for unmatched brackets
    bracket_count = 0
    brace_count = 0

    for i, char in enumerate(pattern):
        if char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1
            if bracket_count < 0:
                raise ValidationError(
                    f"Unmatched closing bracket ']' at position {i} in pattern: {pattern}"
                )
        elif char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count < 0:
                raise ValidationError(
                    f"Unmatched closing brace '}}' at position {i} in pattern: {pattern}"
                )

    if bracket_count > 0:
        raise ValidationError(f"Unmatched opening bracket '[' in pattern: {pattern}")

    if brace_count > 0:
        raise ValidationError(f"Unmatched opening brace '{{' in pattern: {pattern}")

    return pattern


def validate_github_repo(repo: str) -> str:
    """Validate GitHub repository name format.

    Expected format: owner/repo

    Args:
        repo: Repository name to validate.

    Returns:
        The validated repository name.

    Raises:
        ValidationError: If repository name format is invalid.
    """
    if not repo:
        raise ValidationError("Repository name cannot be empty")

    if not isinstance(repo, str):
        raise ValidationError(
            f"Repository name must be a string, got {type(repo).__name__}"
        )

    # Strip whitespace
    repo = repo.strip()

    # Check format: owner/repo
    if "/" not in repo:
        raise ValidationError(
            f"Repository name must be in 'owner/repo' format, got '{repo}'"
        )

    parts = repo.split("/")
    if len(parts) != 2:
        raise ValidationError(
            f"Repository name must have exactly one '/', got '{repo}'"
        )

    owner, repo_name = parts

    if not owner:
        raise ValidationError("Repository owner cannot be empty")

    if not repo_name:
        raise ValidationError("Repository name cannot be empty")

    # Validate characters (GitHub allows alphanumeric, hyphens, underscores)
    valid_pattern = re.compile(r"^[a-zA-Z0-9._-]+$")

    if not valid_pattern.match(owner):
        raise ValidationError(
            f"Invalid repository owner '{owner}'. "
            "Only alphanumeric characters, hyphens, underscores, and dots are allowed."
        )

    if not valid_pattern.match(repo_name):
        raise ValidationError(
            f"Invalid repository name '{repo_name}'. "
            "Only alphanumeric characters, hyphens, underscores, and dots are allowed."
        )

    return f"{owner}/{repo_name}"


def validate_timeout(
    timeout: Optional[int], default: int = 300, maximum: int = 3600
) -> int:
    """Validate timeout value with default and maximum limits.

    Args:
        timeout: Timeout value in seconds, or None for default.
        default: Default timeout if None is provided.
        maximum: Maximum allowed timeout.

    Returns:
        The validated timeout value.

    Raises:
        ValidationError: If timeout is invalid.
    """
    if timeout is None:
        return default

    if not isinstance(timeout, int):
        raise ValidationError(
            f"Timeout must be an integer, got {type(timeout).__name__}"
        )

    if timeout <= 0:
        raise ValidationError(f"Timeout must be positive, got {timeout}")

    if timeout > maximum:
        raise ValidationError(
            f"Timeout exceeds maximum of {maximum} seconds, got {timeout}"
        )

    return timeout


def validate_file_path(path: str, must_exist: bool = False) -> str:
    """Validate file path.

    Args:
        path: File path to validate.
        must_exist: Whether the path must exist.

    Returns:
        The validated path.

    Raises:
        ValidationError: If path is invalid.
    """
    if not path:
        raise ValidationError("File path cannot be empty")

    if not isinstance(path, str):
        raise ValidationError(f"File path must be a string, got {type(path).__name__}")

    # Strip whitespace
    path = path.strip()

    if not path:
        raise ValidationError("File path cannot be empty or whitespace only")

    # Check for null bytes (security)
    if "\0" in path:
        raise ValidationError("File path contains null byte")

    if must_exist:
        from pathlib import Path

        if not Path(path).exists():
            raise ValidationError(f"Path does not exist: {path}")

    return path


def validate_positive_integer(value: Any, name: str = "value") -> int:
    """Validate that a value is a positive integer.

    Args:
        value: Value to validate.
        name: Name of the value for error messages.

    Returns:
        The validated integer.

    Raises:
        ValidationError: If value is not a positive integer.
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value).__name__}")

    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")

    return value
