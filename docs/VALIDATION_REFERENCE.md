# Validation Reference Guide

Quick reference for all validation functions in QCoder CLI.

## Import

```python
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
```

## Functions

### validate_api_key(api_key: str) -> str

Validates OpenRouter API key format.

**Rules:**
- Minimum length: 20 characters
- No leading/trailing whitespace (auto-stripped)
- No internal whitespace
- Cannot be empty

**Example:**
```python
key = validate_api_key("sk-or-v1-1234567890abcdefghij")
# Returns: "sk-or-v1-1234567890abcdefghij"

validate_api_key("short")  # Raises: API key is too short
```

---

### validate_temperature(temperature: float) -> float

Validates AI model temperature parameter.

**Rules:**
- Must be between 0.0 and 2.0 (inclusive)
- Accepts int, converts to float
- Must be numeric type

**Example:**
```python
temp = validate_temperature(0.7)  # Returns: 0.7
temp = validate_temperature(1)    # Returns: 1.0

validate_temperature(2.5)  # Raises: Temperature must be between 0.0 and 2.0
```

---

### validate_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]

Validates chat message structure.

**Rules:**
- Must be a non-empty list
- Each item must be a dict
- Each dict must have 'role' and 'content' keys
- Role must be: 'system', 'user', or 'assistant'
- Content must be a string

**Example:**
```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
]
validated = validate_messages(messages)

validate_messages([])  # Raises: Messages list cannot be empty
validate_messages([{"role": "admin"}])  # Raises: Invalid role + missing content
```

---

### validate_glob_pattern(pattern: str) -> str

Validates glob pattern syntax.

**Rules:**
- Must be a non-empty string
- Brackets `[]` must be balanced
- Braces `{}` must be balanced
- No path traversal (`../`, `..\\`)

**Example:**
```python
pattern = validate_glob_pattern("*.py")           # OK
pattern = validate_glob_pattern("**/*.{js,ts}")   # OK

validate_glob_pattern("test[abc")      # Raises: Unmatched opening bracket
validate_glob_pattern("../../../etc")  # Raises: path traversal
```

---

### validate_github_repo(repo: str) -> str

Validates GitHub repository name format.

**Rules:**
- Format: `owner/repo`
- Exactly one slash `/`
- Only alphanumeric, hyphens, underscores, dots
- Owner and repo cannot be empty
- Whitespace is stripped

**Example:**
```python
repo = validate_github_repo("owner/repo")        # Returns: "owner/repo"
repo = validate_github_repo("my-org/my.project") # Returns: "my-org/my.project"

validate_github_repo("myrepo")      # Raises: must be in 'owner/repo' format
validate_github_repo("owner/")      # Raises: repo name cannot be empty
validate_github_repo("own@r/repo")  # Raises: Invalid characters
```

---

### validate_timeout(timeout: Optional[int], default: int = 300, maximum: int = 3600) -> int

Validates timeout value with defaults.

**Rules:**
- Must be a positive integer (if provided)
- If None, returns `default`
- Cannot exceed `maximum`

**Example:**
```python
timeout = validate_timeout(None, default=300)     # Returns: 300
timeout = validate_timeout(600, maximum=3600)     # Returns: 600
timeout = validate_timeout(60)                    # Returns: 60 (default max=3600)

validate_timeout(0)       # Raises: must be positive
validate_timeout(-10)     # Raises: must be positive
validate_timeout(5000, maximum=3600)  # Raises: exceeds maximum
```

---

### validate_file_path(path: str, must_exist: bool = False) -> str

Validates file path.

**Rules:**
- Must be a non-empty string
- No null bytes
- Whitespace is stripped
- Optionally checks if path exists

**Example:**
```python
path = validate_file_path("/path/to/file.txt")      # OK
path = validate_file_path("  relative/path.txt  ")  # Returns: "relative/path.txt"

validate_file_path("")              # Raises: cannot be empty
validate_file_path("/path\x00/to")  # Raises: contains null byte
validate_file_path("/nonexistent", must_exist=True)  # Raises: Path does not exist
```

---

### validate_positive_integer(value: Any, name: str = "value") -> int

Validates positive integer.

**Rules:**
- Must be an integer
- Must be greater than 0

**Example:**
```python
count = validate_positive_integer(10)              # Returns: 10
count = validate_positive_integer(100, name="max") # Returns: 100

validate_positive_integer(0)       # Raises: value must be positive
validate_positive_integer(-5)      # Raises: value must be positive
validate_positive_integer(5.5)     # Raises: value must be an integer
validate_positive_integer(-1, name="count")  # Raises: count must be positive
```

---

## ValidationError Exception

Custom exception raised by all validators.

**Usage:**
```python
from src.qcoder.utils.validators import ValidationError, validate_temperature

try:
    temp = validate_temperature(user_input)
except ValidationError as e:
    print(f"Invalid input: {e}")
    # Handle error appropriately
```

---

## Common Patterns

### Basic Validation
```python
try:
    validated_value = validate_something(user_input)
    # Use validated_value
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
```

### Validation with Default
```python
# Use default if None provided
timeout = validate_timeout(user_timeout, default=300, maximum=3600)
```

### Chaining Validations
```python
try:
    messages = validate_messages(raw_messages)
    temperature = validate_temperature(temp_value)
    response = ai_client.chat(messages, temperature)
except ValidationError as e:
    console.error(f"Invalid parameters: {e}")
    sys.exit(1)
```

### Converting to Different Error Type
```python
try:
    repo = validate_github_repo(repo_string)
except ValidationError as e:
    raise ValueError(f"Invalid repository: {e}") from e
```

---

## Where Validations Are Used

| Module | Function | Validator |
|--------|----------|-----------|
| `ai_client.py` | `chat()`, `achat()` | `validate_messages()`, `validate_temperature()` |
| `config.py` | `api_key` property | `validate_api_key()` |
| `file_ops.py` | `collect_files()` | `validate_glob_pattern()` |
| `github_integration.py` | `_validate_repo_format()` | `validate_github_repo()` |
| `shell.py` | `execute()` | `validate_timeout()` |

---

## Testing

Run validation tests:
```bash
pytest tests/test_validators.py -v
```

Run specific test class:
```bash
pytest tests/test_validators.py::TestValidateApiKey -v
```

Run with coverage:
```bash
pytest tests/test_validators.py --cov=src.qcoder.utils.validators
```

---

## Error Message Examples

**Before (generic):**
```
Error: Invalid input
Error: Bad value
Error: Cannot proceed
```

**After (specific):**
```
ValidationError: API key is too short (got 10 characters, expected at least 20)
ValidationError: Temperature must be between 0.0 and 2.0, got 2.5
ValidationError: Message at index 0 has invalid role 'admin'. Valid roles are: assistant, system, user
ValidationError: Glob pattern contains potentially dangerous path traversal: ../../../etc
ValidationError: Repository name must be in 'owner/repo' format, got 'myrepo'
ValidationError: Timeout exceeds maximum of 3600 seconds, got 5000
```

---

## Best Practices

1. **Always validate user input** before passing to external APIs or commands
2. **Use try-except** blocks to handle ValidationError gracefully
3. **Provide context** in error messages (what failed and why)
4. **Log validation failures** for debugging
5. **Validate early** - catch errors before expensive operations
6. **Use centralized validators** instead of duplicating validation logic
7. **Write tests** for new validation rules

---

## Adding New Validators

Template for adding a new validator:

```python
def validate_something(value: SomeType) -> SomeType:
    """Validate something.

    Args:
        value: The value to validate.

    Returns:
        The validated value.

    Raises:
        ValidationError: If value is invalid.
    """
    # Check type
    if not isinstance(value, SomeType):
        raise ValidationError(
            f"Value must be SomeType, got {type(value).__name__}"
        )

    # Check constraints
    if not meets_constraint(value):
        raise ValidationError(
            f"Value must meet constraint, got {value}"
        )

    # Sanitize if needed
    value = sanitize(value)

    return value
```

Then add tests in `tests/test_validators.py`:

```python
class TestValidateSomething:
    """Tests for something validation."""

    def test_valid_something(self):
        """Test validation of valid values."""
        assert validate_something(valid_value) == valid_value

    def test_invalid_something(self):
        """Test that invalid value raises error."""
        with pytest.raises(ValidationError, match="constraint"):
            validate_something(invalid_value)
```

---

## Performance Considerations

- **Validators are fast** - O(1) or O(n) where n is input size
- **No network calls** - all validation is local
- **Minimal overhead** - typical validation takes < 1ms
- **Safe for hot paths** - can be called frequently

**Benchmark:**
```python
import timeit

# Fast validators (< 0.001ms)
timeit.timeit(lambda: validate_temperature(0.7), number=10000)
timeit.timeit(lambda: validate_timeout(300), number=10000)

# String validators (< 0.01ms)
timeit.timeit(lambda: validate_api_key("sk-or-v1-" + "x"*30), number=10000)
timeit.timeit(lambda: validate_github_repo("owner/repo"), number=10000)

# Pattern validators (< 0.1ms)
timeit.timeit(lambda: validate_glob_pattern("**/*.py"), number=10000)
```
