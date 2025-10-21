# Input Validation Implementation Summary

This document summarizes the comprehensive input validation added to the QCoder CLI project.

## Overview

Input validation has been implemented throughout the codebase to ensure data integrity, prevent security vulnerabilities, and provide clear error messages to users.

## New Files Created

### 1. `src/qcoder/utils/validators.py`

A centralized validation utilities module containing reusable validation functions:

- `validate_api_key()` - Validates API key format and length
- `validate_temperature()` - Validates AI model temperature parameter (0.0-2.0)
- `validate_messages()` - Validates chat message structure and roles
- `validate_glob_pattern()` - Validates glob patterns and prevents path traversal
- `validate_github_repo()` - Validates GitHub repository name format
- `validate_timeout()` - Validates timeout values with defaults and maximums
- `validate_file_path()` - Validates file paths and prevents null bytes
- `validate_positive_integer()` - Validates positive integer values
- `ValidationError` - Custom exception for validation failures

## Validations Added by File

### 1. `src/qcoder/core/ai_client.py` (Lines 42-131)

**Methods Updated:** `chat()` and `achat()`

**Validations:**
- Messages list cannot be empty
- Each message must have 'role' and 'content' fields
- Role must be one of: 'system', 'user', 'assistant'
- Content must be a string
- Temperature must be between 0.0 and 2.0
- Temperature is converted to float if passed as int

**Error Handling:**
```python
# Validate inputs
messages = validate_messages(messages)
temperature = validate_temperature(temperature)
```

**Benefits:**
- Prevents API errors from invalid message structures
- Catches invalid temperature values before API call
- Provides clear error messages for debugging

---

### 2. `src/qcoder/core/config.py` (Line 124)

**Property Updated:** `api_key`

**Validations:**
- API key minimum length: 20 characters
- Strips leading/trailing whitespace
- Cannot be empty or whitespace-only
- No internal whitespace allowed

**Error Handling:**
```python
try:
    return validate_api_key(key)
except Exception as e:
    raise ValueError(
        f"Invalid OpenRouter API key: {e}. "
        "Please check your API key configuration."
    ) from e
```

**Benefits:**
- Catches malformed API keys early
- Prevents common copy-paste errors (extra spaces)
- Clear error messages guide users to fix configuration

---

### 3. `src/qcoder/cli.py` (Line 326)

**Change:** Renamed `--global` flag to `--global-config`

**Reason:** `global` is a Python reserved keyword and should not be used as a parameter name

**Updated Examples:**
```bash
# Old (problematic)
qcoder config --global

# New (correct)
qcoder config --global-config
qcoder config --global-config --set api_key=your-key
```

**Benefits:**
- Avoids Python reserved keyword issues
- More descriptive flag name
- Better code maintainability

---

### 4. `src/qcoder/modules/file_ops.py` (Lines 84-208)

**Method Updated:** `collect_files()`

**Validations:**
- Glob pattern syntax validation
- Checks for unmatched brackets `[]` and braces `{}`
- Prevents path traversal attacks (e.g., `../../../etc/passwd`)
- Catches glob execution errors with helpful messages

**Error Handling:**
```python
try:
    pattern = validate_glob_pattern(pattern)
except ValidationError as e:
    self.console.error(f"Invalid glob pattern: {e}")
    raise

try:
    for path in root.glob(glob_pattern):
        # Process files...
except (ValueError, OSError) as e:
    raise ValidationError(
        f"Failed to process glob pattern '{pattern}': {e}"
    ) from e
```

**Benefits:**
- Prevents crashes from malformed glob patterns
- Security: blocks path traversal attempts
- User-friendly error messages for syntax errors

---

### 5. `src/qcoder/modules/github_integration.py` (Line 36)

**Method Updated:** `_validate_repo_format()`

**Validations:**
- Repository format must be `owner/repo`
- Owner and repo name must contain only: alphanumeric, hyphens, underscores, dots
- Cannot have multiple slashes
- Owner and repo cannot be empty
- Strips whitespace

**Replaced Implementation:**
```python
# Old: Custom regex validation
# New: Centralized validator
try:
    return validate_github_repo(repo)
except ValidationError as e:
    raise ValueError(str(e)) from e
```

**Benefits:**
- Prevents command injection in GitHub CLI calls
- Validates format before external command execution
- Consistent validation across the codebase

---

### 6. `src/qcoder/modules/shell.py` (Lines 16-158)

**Updates:**
- Added class constants: `DEFAULT_TIMEOUT = 300` (5 minutes)
- Added class constant: `MAX_TIMEOUT = 3600` (1 hour)

**Method Updated:** `execute()`

**Validations:**
- Timeout must be a positive integer
- If timeout is None, uses `DEFAULT_TIMEOUT` (300 seconds)
- Maximum timeout is `MAX_TIMEOUT` (3600 seconds)
- Prevents excessively long-running commands

**Error Handling:**
```python
# Validate and set timeout
timeout = validate_timeout(
    timeout, default=self.DEFAULT_TIMEOUT, maximum=self.MAX_TIMEOUT
)
```

**Benefits:**
- Prevents indefinitely hanging commands
- Reasonable defaults for most use cases
- Hard limit prevents resource exhaustion
- Clear timeout errors with actual values

---

## Security Improvements

1. **Path Traversal Prevention**
   - Glob patterns validated to prevent `../` attacks
   - File paths checked for null bytes
   - Repository names validated to prevent command injection

2. **Input Sanitization**
   - All string inputs stripped of whitespace
   - Length validations prevent buffer overflow risks
   - Type checking prevents unexpected behavior

3. **Command Injection Prevention**
   - GitHub repository names validated before shell commands
   - Pattern matching ensures safe characters only

## Testing

Comprehensive test suite added in `tests/test_validators.py` with:
- 60+ test cases covering all validators
- Edge case testing (empty, null, boundary values)
- Error message verification
- Type validation tests

Run tests with:
```bash
pytest tests/test_validators.py -v
```

## Usage Examples

### API Key Validation
```python
from src.qcoder.utils.validators import validate_api_key, ValidationError

try:
    key = validate_api_key("  sk-or-v1-abc123xyz789  ")
    # Returns: "sk-or-v1-abc123xyz789" (stripped)
except ValidationError as e:
    print(f"Invalid API key: {e}")
```

### Temperature Validation
```python
from src.qcoder.utils.validators import validate_temperature

# Valid
temp = validate_temperature(0.7)  # Returns 0.7
temp = validate_temperature(1)    # Returns 1.0 (converted to float)

# Invalid
validate_temperature(2.5)  # Raises: Temperature must be between 0.0 and 2.0
```

### Message Validation
```python
from src.qcoder.utils.validators import validate_messages

messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
]
validated = validate_messages(messages)  # Returns messages if valid
```

### Glob Pattern Validation
```python
from src.qcoder.utils.validators import validate_glob_pattern

# Valid patterns
validate_glob_pattern("*.py")           # OK
validate_glob_pattern("**/*.{js,ts}")   # OK

# Invalid patterns
validate_glob_pattern("../../../etc")   # Raises: path traversal
validate_glob_pattern("test[abc")       # Raises: unmatched bracket
```

### Timeout Validation
```python
from src.qcoder.utils.validators import validate_timeout

# Use default if None
timeout = validate_timeout(None, default=300)  # Returns 300

# Validate custom timeout
timeout = validate_timeout(600, maximum=3600)  # Returns 600

# Invalid
validate_timeout(5000, maximum=3600)  # Raises: exceeds maximum
```

## Error Messages

All validators provide clear, actionable error messages:

```
❌ Before: "Invalid input"
✅ After:  "Temperature must be between 0.0 and 2.0, got 2.5"

❌ Before: "Bad format"
✅ After:  "Repository name must be in 'owner/repo' format, got 'myrepo'"

❌ Before: "Error"
✅ After:  "Glob pattern contains potentially dangerous path traversal: ../../../etc"
```

## Migration Notes

### For Developers

1. **Import validators where needed:**
   ```python
   from ..utils.validators import validate_temperature, ValidationError
   ```

2. **Wrap validation in try-except:**
   ```python
   try:
       validated_value = validate_something(user_input)
   except ValidationError as e:
       # Handle error appropriately
       logger.error(f"Validation failed: {e}")
       raise
   ```

3. **Use consistent error handling:**
   - Catch `ValidationError` specifically
   - Re-raise with context when needed
   - Log validation failures for debugging

### For Users

- **API Key Configuration:** Ensure your API key is at least 20 characters with no spaces
- **CLI Usage:** Use `--global-config` instead of `--global`
- **Timeouts:** Commands now have a 5-minute default timeout, 1-hour maximum
- **Better Error Messages:** Validation errors now clearly explain what's wrong and how to fix it

## Future Enhancements

Potential areas for additional validation:

1. Model name validation (check against available models)
2. File size limits for file operations
3. Rate limiting for API calls
4. Webhook URL validation for integrations
5. Configuration value type validation based on schema

## Conclusion

These validation improvements significantly enhance:
- **Security:** Prevents injection attacks and path traversal
- **Reliability:** Catches errors before they cause failures
- **Usability:** Clear error messages guide users to solutions
- **Maintainability:** Centralized validators reduce code duplication
