# Contributing to QCoder CLI

Thank you for your interest in contributing to QCoder CLI! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/qcoder-cli.git
   cd qcoder-cli
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We follow strict code quality standards:

- **Python Style**: PEP 8 with Black formatting
- **Line Length**: 100 characters
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for all public functions

### Formatting and Linting

Before committing, format and lint your code:

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Running Tests

Always run tests before submitting:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=qcoder tests/

# Run specific test file
pytest tests/test_config.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure (e.g., `tests/core/test_config.py` for `src/qcoder/core/config.py`)
- Aim for >80% code coverage
- Use descriptive test names: `test_function_name_should_behavior_when_condition`

Example test:

```python
def test_config_get_should_return_env_value_when_env_var_set():
    """Test that config.get() prioritizes environment variables."""
    import os
    from qcoder.core.config import Config

    os.environ["QCODER_TEST_KEY"] = "test_value"
    config = Config()

    assert config.get("test_key") == "test_value"

    del os.environ["QCODER_TEST_KEY"]
```

## Contribution Guidelines

### Reporting Bugs

When reporting bugs, include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the bug
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (OS, Python version, QCoder version)
6. **Error messages** and stack traces

### Suggesting Features

For feature requests:

1. **Describe the problem** the feature solves
2. **Provide use cases** and examples
3. **Consider alternatives** and explain why your approach is best
4. **Be open to discussion** and feedback

### Pull Requests

#### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary dependencies added

#### PR Process

1. **Create a pull request** with a clear title and description
2. **Link related issues** using keywords (Fixes #123, Closes #456)
3. **Ensure CI checks pass**
4. **Respond to review feedback** promptly
5. **Squash commits** if requested
6. **Wait for approval** from maintainers

#### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(chat): add multi-line input support

Implements Shift+Enter for multi-line messages in chat mode.

Fixes #42
```

```
fix(config): resolve Windows path handling issue

Config files now correctly load on Windows systems.

Closes #87
```

## Project Structure

```
qcoder-cli/
├── src/qcoder/          # Source code
│   ├── core/            # Core functionality
│   ├── modules/         # Feature modules
│   ├── plugins/         # Plugin system
│   ├── utils/           # Utilities
│   └── cli.py           # Main CLI
├── tests/               # Test suite
├── examples/            # Example files
├── docs/                # Documentation
└── .qcoder/             # Example configs
```

## Adding New Features

### 1. Modules

Add new feature modules to `src/qcoder/modules/`:

```python
"""New feature module."""

from typing import Any
from ..core.ai_client import get_ai_client
from ..utils.output import Console


class NewFeature:
    """Handles new feature functionality."""

    def __init__(self) -> None:
        """Initialize feature."""
        self.ai_client = get_ai_client()
        self.console = Console()

    def process(self, input_data: Any) -> Any:
        """Process input with new feature.

        Args:
            input_data: Input to process.

        Returns:
            Processed result.
        """
        # Implementation here
        pass
```

### 2. CLI Commands

Add commands to `src/qcoder/cli.py`:

```python
@main.command()
@click.argument("arg")
@click.option("--option", help="Option description")
def newcommand(arg: str, option: Optional[str]) -> None:
    """Brief command description.

    Detailed description and examples.
    """
    try:
        # Implementation
        pass
    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)
```

### 3. Plugins

Create plugins in `examples/` with documentation:

```python
PLUGIN_METADATA = {
    "name": "plugin_name",
    "version": "1.0.0",
    "description": "Plugin description",
    "author": "Your Name"
}

from qcoder.plugins.plugin_manager import command

@command
def my_command():
    """Command implementation."""
    pass
```

### 4. Documentation

Update documentation:

- Add feature to README.md
- Create examples in `examples/`
- Update CONTRIBUTING.md if workflow changes
- Add docstrings to all new code

## Code Review Checklist

Reviewers will check:

- [ ] Code quality and style
- [ ] Test coverage
- [ ] Documentation completeness
- [ ] Performance considerations
- [ ] Security implications
- [ ] Backward compatibility
- [ ] Error handling
- [ ] Edge cases

## Getting Help

- **GitHub Issues**: Ask questions or report problems
- **Discussions**: For general questions and ideas
- **Pull Request Comments**: For code-specific questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

Thank you for contributing to QCoder CLI!
