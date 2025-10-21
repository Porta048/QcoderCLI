# QCoder CLI Test Suite

## Quick Start

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage report
pytest --cov=qcoder --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

## Test Files

### conftest.py
Shared pytest configuration and fixtures used across all test files.

**Key Fixtures:**
- `temp_config_dir` - Temporary configuration directory
- `temp_project_dir` - Temporary project directory
- `mock_config` - Mock Config object with test data
- `mock_ai_client` - Mock AI client with predefined responses
- `sample_python_file` - Sample Python code file
- `sample_json_file` - Sample JSON data file
- `sample_checkpoint_data` - Sample conversation checkpoint
- `saved_checkpoint` - Saved checkpoint file for loading
- `env_setup` - Test environment variable setup
- Singleton reset fixtures for isolated tests

### test_config.py (69 tests)
Configuration management tests covering:
- Configuration initialization and directory creation
- YAML configuration file loading and parsing
- Environment variable precedence and priority chains
- Configuration getter with fallback logic
- Configuration properties (api_key, model, github_token, etc.)
- Directory path management and creation
- Configuration saving and persistence
- Context file loading and combination

**Test Classes:**
- `TestConfigInitialization` - Config setup and defaults
- `TestConfigGet` - Getter method with priorities
- `TestConfigProperties` - Property accessors
- `TestConfigContext` - Context file handling
- `TestConfigSave` - Configuration persistence
- `TestConfigValidation` - Input validation
- `TestGlobalConfigSingleton` - Singleton pattern
- `TestPathResolution` - Path handling

### test_conversation.py (38 tests)
Conversation management tests covering:
- Message creation with role-based system
- Message formatting and serialization
- Conversation lifecycle management
- Context trimming within token limits
- Checkpoint creation and restoration
- Checkpoint listing and sorting
- Conversation clearing and reset
- Metadata tracking and timestamps
- Conversation summaries and statistics

**Test Classes:**
- `TestMessage` - Message dataclass functionality
- `TestConversationInitialization` - Setup and defaults
- `TestConversationAddMessage` - Message addition
- `TestConversationGetMessagesForAPI` - API formatting
- `TestConversationTrimContext` - Context management
- `TestConversationClear` - Conversation reset
- `TestConversationCheckpoint` - Persistence layer
- `TestConversationListCheckpoints` - Checkpoint discovery
- `TestConversationSummary` - Statistics generation

### test_ai_client.py (25 tests)
AI client integration tests covering:
- Client initialization with credentials
- Chat completion requests (sync and async)
- Model listing and retrieval
- Response extraction and parsing
- Token counting and estimation
- System prompt construction
- Error handling for API failures
- Header injection for tracking
- Global client singleton pattern

**Test Classes:**
- `TestAIClientInitialization` - Client setup
- `TestAIClientChat` - Sync chat operations
- `TestAIClientAsync` - Async operations
- `TestAIClientGetModels` - Model retrieval
- `TestAIClientExtractResponse` - Response parsing
- `TestAIClientTokenCounting` - Token estimation
- `TestAIClientSystemPrompt` - Prompt construction
- `TestGlobalAIClientSingleton` - Singleton pattern

### test_file_ops.py (32 tests)
File operations tests covering:
- File reading with encoding handling
- File writing with directory creation
- Ignore pattern matching (git, cache, venv, etc.)
- File collection with limits and patterns
- Recursive vs non-recursive file traversal
- File searching with line numbers
- Code block cleaning for AI output
- Unicode and binary file handling
- Error handling for missing or invalid files

**Test Classes:**
- `TestFileOperationsInitialization` - Setup
- `TestFileOperationsReadFile` - File reading
- `TestFileOperationsWriteFile` - File writing
- `TestFileOperationsShouldIgnore` - Pattern matching
- `TestFileOperationsCollectFiles` - File collection
- `TestFileOperationsCleanCodeBlocks` - Formatting
- `TestFileOperationsSearchInFiles` - File searching
- `TestFileOperationsProcessWithAI` - AI processing
- `TestFileOperationsEdgeCases` - Edge cases

### test_shell.py (30 tests)
Shell execution tests covering:
- Shell executor initialization
- Dangerous command pattern detection
- Command execution with mocking
- Timeout handling and limits
- Platform-specific execution (Windows vs Unix)
- User confirmation for dangerous operations
- Command explanation via AI
- Command suggestion via AI
- Error analysis and fix suggestions
- Output capture and formatting

**Test Classes:**
- `TestShellExecutorInitialization` - Setup
- `TestShellExecutorDangerousCommands` - Pattern detection
- `TestShellExecutorExecution` - Command execution
- `TestShellExecutorExplainCommand` - AI explanations
- `TestShellExecutorSuggestCommand` - AI suggestions
- `TestShellExecutorAnalysis` - AI analysis
- `TestShellExecutorEdgeCases` - Edge cases

### test_security.py (19 tests)
Security-focused tests covering:
- Path traversal attack prevention
- Command injection detection
- Dangerous pattern blocking
- Credential handling safety
- Unsafe eval() and exec() detection
- Input validation and sanitization
- Environment isolation
- Secure error handling

**Test Classes:**
- `TestPathTraversalPrevention` - Path security
- `TestCommandInjectionPrevention` - Command safety
- `TestCredentialHandling` - Secret management
- `TestNoUnsafeEval` - Code safety
- `TestInputValidation` - Input checks
- `TestEnvironmentIsolation` - Execution safety
- `TestErrorHandling` - Error safety

### test_validators.py
Additional validation tests for utility functions.

## Test Statistics

**Total Tests:** 230
**Passing:** 213 (92.6%)
**Failing:** 17 (7.4%)
**Execution Time:** ~4.2 seconds
**Code Coverage:** 39% overall

## Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| conversation.py | 100% | Complete |
| config.py | 90% | Excellent |
| ai_client.py | 86% | Excellent |
| shell.py | 74% | Good |
| file_ops.py | 68% | Good |

## Running Tests

### All Tests
```bash
pytest tests/
```

### With Verbose Output
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=qcoder --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_config.py -v
```

### Specific Test Class
```bash
pytest tests/test_config.py::TestConfigGet -v
```

### Specific Test
```bash
pytest tests/test_config.py::TestConfigGet::test_get_from_environment_variable -v
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Parallel Execution (requires pytest-xdist)
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### Generate HTML Report
```bash
pytest tests/ --html=report.html --self-contained-html
```

## Test Patterns

### Using Fixtures
```python
def test_something(temp_config_dir, mock_config, sample_python_file):
    """Test using multiple fixtures"""
    # Test code here
```

### Mocking External Calls
```python
def test_ai_call(mock_ai_client):
    """Test with mocked AI client"""
    with patch("module.get_ai_client", return_value=mock_ai_client):
        # Test code
```

### Testing Errors
```python
def test_error_handling():
    """Test error handling"""
    with pytest.raises(FileNotFoundError):
        read_file("nonexistent.py")
```

### Testing with Environment Variables
```python
def test_env_var(monkeypatch):
    """Test with environment variables"""
    monkeypatch.setenv("KEY", "value")
    # Test code
```

## Debugging Tests

### Verbose Output with Traceback
```bash
pytest tests/test_config.py::TestConfigGet::test_get_from_environment_variable -vv --tb=long
```

### Drop into Debugger on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables
```bash
pytest tests/ -vv --showlocals
```

### Capture Output
```bash
pytest tests/ --capture=no
```

## Common Issues

### Module Not Found
```bash
pip install -e ".[dev]"
```

### Coverage Report Not Generated
```bash
pytest tests/ --cov=qcoder --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### Tests Fail with Different Python Version
Check `pyproject.toml` for Python version requirements (3.10+)

### Singleton State Pollution
Tests include auto-use fixtures to reset singletons between tests

## Contributing Tests

1. Follow existing test structure and naming
2. Use appropriate test file (or create new one)
3. Utilize existing fixtures
4. Add docstrings explaining purpose
5. Include positive, negative, and edge cases
6. Run `pytest tests/ --cov=qcoder` to verify coverage
7. Ensure no linting issues with `black` and `ruff`

## Test Organization Philosophy

- **One fixture per concern**: temp dirs, mocks, data
- **Clear naming**: Test names explain what they test
- **Comprehensive coverage**: Happy path, errors, edges
- **Security focus**: Dedicated security tests
- **Fast execution**: No unnecessary external calls
- **Maintainable**: Well-documented, reusable fixtures

## CI/CD Integration

Tests are designed for CI/CD pipelines:

```yaml
- name: Run Tests
  run: |
    pip install -e ".[dev]"
    pytest tests/ --cov=qcoder --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Documentation

- See `TESTING.md` for comprehensive testing guide
- See `TEST_SUMMARY.md` for detailed metrics and analysis

## Performance

- **Startup:** ~1 second (Python import overhead)
- **Per Test:** ~18ms average
- **Total Suite:** ~4.2 seconds
- **Memory:** ~50MB
- **Parallelizable:** Yes (with pytest-xdist)

## Future Improvements

1. Add integration tests with real API calls
2. Add performance benchmarking
3. Add visual regression tests
4. Add property-based testing with Hypothesis
5. Add mutation testing
6. Add fuzz testing

## Questions?

See the main project README or TESTING.md for more information.
