"""Tests for input validation utilities."""

import pytest
from src.qcoder.utils.validators import (
    ValidationError,
    validate_api_key,
    validate_temperature,
    validate_messages,
    validate_glob_pattern,
    validate_github_repo,
    validate_timeout,
    validate_file_path,
    validate_positive_integer,
)


class TestValidateApiKey:
    """Tests for API key validation."""

    def test_valid_api_key(self):
        """Test validation of valid API keys."""
        valid_key = "sk-or-v1-1234567890abcdefghijklmnopqrstuvwxyz"
        result = validate_api_key(valid_key)
        assert result == valid_key

    def test_empty_api_key(self):
        """Test that empty API key raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_key("")

    def test_whitespace_only_api_key(self):
        """Test that whitespace-only API key raises error."""
        with pytest.raises(ValidationError, match="cannot be empty or whitespace"):
            validate_api_key("   ")

    def test_short_api_key(self):
        """Test that short API key raises error."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_key("short123")

    def test_api_key_with_whitespace(self):
        """Test that API key with internal whitespace raises error."""
        with pytest.raises(ValidationError, match="contains whitespace"):
            validate_api_key("sk-or-v1-1234567890 abcdefghij")

    def test_api_key_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        key_with_spaces = "  sk-or-v1-1234567890abcdefghijklmnopqrstuvwxyz  "
        result = validate_api_key(key_with_spaces)
        assert result == key_with_spaces.strip()


class TestValidateTemperature:
    """Tests for temperature validation."""

    def test_valid_temperature(self):
        """Test validation of valid temperature values."""
        assert validate_temperature(0.0) == 0.0
        assert validate_temperature(0.7) == 0.7
        assert validate_temperature(1.0) == 1.0
        assert validate_temperature(2.0) == 2.0

    def test_temperature_below_range(self):
        """Test that temperature below 0.0 raises error."""
        with pytest.raises(ValidationError, match="between 0.0 and 2.0"):
            validate_temperature(-0.1)

    def test_temperature_above_range(self):
        """Test that temperature above 2.0 raises error."""
        with pytest.raises(ValidationError, match="between 0.0 and 2.0"):
            validate_temperature(2.1)

    def test_temperature_as_integer(self):
        """Test that integer temperature is converted to float."""
        result = validate_temperature(1)
        assert result == 1.0
        assert isinstance(result, float)

    def test_invalid_temperature_type(self):
        """Test that non-numeric temperature raises error."""
        with pytest.raises(ValidationError, match="must be a number"):
            validate_temperature("0.7")  # type: ignore


class TestValidateMessages:
    """Tests for messages validation."""

    def test_valid_messages(self):
        """Test validation of valid messages."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = validate_messages(messages)
        assert result == messages

    def test_empty_messages_list(self):
        """Test that empty messages list raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_messages([])

    def test_messages_not_list(self):
        """Test that non-list messages raises error."""
        with pytest.raises(ValidationError, match="must be a list"):
            validate_messages({"role": "user", "content": "test"})  # type: ignore

    def test_message_not_dict(self):
        """Test that non-dict message raises error."""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            validate_messages([["role", "user"]])  # type: ignore

    def test_message_missing_role(self):
        """Test that message missing role raises error."""
        with pytest.raises(ValidationError, match="missing 'role' field"):
            validate_messages([{"content": "test"}])  # type: ignore

    def test_message_missing_content(self):
        """Test that message missing content raises error."""
        with pytest.raises(ValidationError, match="missing 'content' field"):
            validate_messages([{"role": "user"}])  # type: ignore

    def test_invalid_role(self):
        """Test that invalid role raises error."""
        with pytest.raises(ValidationError, match="invalid role"):
            validate_messages([{"role": "admin", "content": "test"}])

    def test_non_string_content(self):
        """Test that non-string content raises error."""
        with pytest.raises(ValidationError, match="content must be a string"):
            validate_messages([{"role": "user", "content": 123}])  # type: ignore


class TestValidateGlobPattern:
    """Tests for glob pattern validation."""

    def test_valid_glob_patterns(self):
        """Test validation of valid glob patterns."""
        assert validate_glob_pattern("*.py") == "*.py"
        assert validate_glob_pattern("**/*.txt") == "**/*.txt"
        assert validate_glob_pattern("src/**/*.{py,js}") == "src/**/*.{py,js}"

    def test_empty_pattern(self):
        """Test that empty pattern raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_glob_pattern("")

    def test_pattern_not_string(self):
        """Test that non-string pattern raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_glob_pattern(123)  # type: ignore

    def test_path_traversal_patterns(self):
        """Test that path traversal patterns raise error."""
        with pytest.raises(ValidationError, match="path traversal"):
            validate_glob_pattern("../../../etc/passwd")

    def test_unmatched_opening_bracket(self):
        """Test that unmatched opening bracket raises error."""
        with pytest.raises(ValidationError, match="Unmatched opening bracket"):
            validate_glob_pattern("test[abc")

    def test_unmatched_closing_bracket(self):
        """Test that unmatched closing bracket raises error."""
        with pytest.raises(ValidationError, match="Unmatched closing bracket"):
            validate_glob_pattern("test]abc")

    def test_unmatched_opening_brace(self):
        """Test that unmatched opening brace raises error."""
        with pytest.raises(ValidationError, match="Unmatched opening brace"):
            validate_glob_pattern("test{py,js")

    def test_unmatched_closing_brace(self):
        """Test that unmatched closing brace raises error."""
        with pytest.raises(ValidationError, match="Unmatched closing brace"):
            validate_glob_pattern("testpy,js}")


class TestValidateGithubRepo:
    """Tests for GitHub repository name validation."""

    def test_valid_repo_names(self):
        """Test validation of valid repository names."""
        assert validate_github_repo("owner/repo") == "owner/repo"
        assert validate_github_repo("my-org/my-project") == "my-org/my-project"
        assert validate_github_repo("user_123/repo.name") == "user_123/repo.name"

    def test_empty_repo_name(self):
        """Test that empty repo name raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_github_repo("")

    def test_repo_name_not_string(self):
        """Test that non-string repo name raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_github_repo(123)  # type: ignore

    def test_missing_slash(self):
        """Test that repo name without slash raises error."""
        with pytest.raises(ValidationError, match="must be in 'owner/repo' format"):
            validate_github_repo("myrepo")

    def test_multiple_slashes(self):
        """Test that repo name with multiple slashes raises error."""
        with pytest.raises(ValidationError, match="must have exactly one '/'"):
            validate_github_repo("owner/repo/extra")

    def test_empty_owner(self):
        """Test that empty owner raises error."""
        with pytest.raises(ValidationError, match="owner cannot be empty"):
            validate_github_repo("/repo")

    def test_empty_repo(self):
        """Test that empty repo raises error."""
        with pytest.raises(ValidationError, match="name cannot be empty"):
            validate_github_repo("owner/")

    def test_invalid_owner_characters(self):
        """Test that invalid owner characters raise error."""
        with pytest.raises(ValidationError, match="Invalid repository owner"):
            validate_github_repo("owner@invalid/repo")

    def test_invalid_repo_characters(self):
        """Test that invalid repo characters raise error."""
        with pytest.raises(ValidationError, match="Invalid repository name"):
            validate_github_repo("owner/repo@invalid")

    def test_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_github_repo("  owner/repo  ") == "owner/repo"


class TestValidateTimeout:
    """Tests for timeout validation."""

    def test_valid_timeout(self):
        """Test validation of valid timeout values."""
        assert validate_timeout(60) == 60
        assert validate_timeout(300) == 300

    def test_default_timeout(self):
        """Test that None returns default timeout."""
        assert validate_timeout(None, default=300) == 300

    def test_timeout_exceeds_maximum(self):
        """Test that timeout exceeding maximum raises error."""
        with pytest.raises(ValidationError, match="exceeds maximum"):
            validate_timeout(5000, maximum=3600)

    def test_negative_timeout(self):
        """Test that negative timeout raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_timeout(-10)

    def test_zero_timeout(self):
        """Test that zero timeout raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_timeout(0)

    def test_non_integer_timeout(self):
        """Test that non-integer timeout raises error."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_timeout(60.5)  # type: ignore


class TestValidateFilePath:
    """Tests for file path validation."""

    def test_valid_file_path(self):
        """Test validation of valid file paths."""
        assert validate_file_path("/path/to/file.txt") == "/path/to/file.txt"
        assert validate_file_path("relative/path.txt") == "relative/path.txt"

    def test_empty_path(self):
        """Test that empty path raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_path("")

    def test_whitespace_only_path(self):
        """Test that whitespace-only path raises error."""
        with pytest.raises(ValidationError, match="cannot be empty or whitespace"):
            validate_file_path("   ")

    def test_path_not_string(self):
        """Test that non-string path raises error."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_file_path(123)  # type: ignore

    def test_path_with_null_byte(self):
        """Test that path with null byte raises error."""
        with pytest.raises(ValidationError, match="contains null byte"):
            validate_file_path("/path/to\x00/file.txt")

    def test_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_file_path("  /path/to/file.txt  ") == "/path/to/file.txt"


class TestValidatePositiveInteger:
    """Tests for positive integer validation."""

    def test_valid_positive_integer(self):
        """Test validation of valid positive integers."""
        assert validate_positive_integer(1) == 1
        assert validate_positive_integer(100) == 100

    def test_zero_not_positive(self):
        """Test that zero raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_integer(0)

    def test_negative_not_positive(self):
        """Test that negative number raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_integer(-5)

    def test_non_integer(self):
        """Test that non-integer raises error."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer(5.5)  # type: ignore

    def test_custom_name_in_error(self):
        """Test that custom name appears in error message."""
        with pytest.raises(ValidationError, match="max_count must be positive"):
            validate_positive_integer(-1, name="max_count")
