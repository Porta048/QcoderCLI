# QCoder CLI

An AI-powered command-line interface for code, chat, and automation - inspired by Gemini CLI.

## Features

- **Interactive AI Chat**: Conversational terminal-based AI assistant with your choice of AI model
- **Code Understanding**: Natural language code explanations and suggestions
- **File Manipulation**: AI-assisted file and directory operations
- **Shell Command Execution**: Execute and explain shell commands with AI guidance
- **GitHub Integration**: PR reviews, issue triage, and automated pull requests
- **MCP Server**: Model Context Protocol for extensible context management
- **Web Search Grounding**: Get up-to-date information through web search integration
- **Conversation Checkpoints**: Save and resume AI conversations
- **Workflow Automation**: Non-interactive script integration and batch processing
- **Plugin System**: Extend functionality with custom plugins
- **Context Files**: Project-specific AI context via QCODER.md files

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/qcoder-cli.git
cd qcoder-cli

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Using pip (once published)

```bash
pip install qcoder
```

## Quick Start

1. **Get your OpenRouter API key**:
   - Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - Sign up and create a free API key

2. **Configure your API key and model**:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure:
# OPENROUTER_API_KEY=your_api_key_here
# DEFAULT_MODEL=google/gemini-2.0-flash-exp:free
```

Available models at [https://openrouter.ai/models](https://openrouter.ai/models)

3. **Start a chat session**:

```bash
qcoder chat
# or simply
qcoder
```

4. **Initialize a project** (optional):

```bash
cd your-project
qcoder init
```

## Usage

### Interactive Chat

Start an interactive AI conversation:

```bash
qcoder chat
qcoder chat --model google/gemini-2.0-flash-exp:free
qcoder chat --model openai/gpt-4-turbo
qcoder chat --resume my_session
```

Chat commands:
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/save [name]` - Save conversation checkpoint
- `/summary` - Show conversation summary
- `/exit` or `/quit` - Exit chat

### Quick Questions

Ask a single question without interactive mode:

```bash
qcoder ask "How do I read a file in Python?"
qcoder ask "Explain this error" --output explanation.txt
```

### File Operations

Analyze or manipulate files with AI:

```bash
# Analyze code
qcoder file main.py --prompt "Explain this code"

# Find patterns
qcoder file . --prompt "Find all TODO comments"

# Transform code
qcoder file script.py --prompt "Add docstrings" --output improved.py
```

### Shell Commands

Execute shell commands with AI assistance:

```bash
# Execute directly
qcoder shell git status

# Get explanation first
qcoder shell --explain git rebase -i HEAD~3

# Auto-approve execution
qcoder shell npm install --auto-approve
```

### GitHub Integration

```bash
# Review a pull request
qcoder github --pr 123
qcoder github owner/repo --pr 456

# Analyze an issue
qcoder github --issue 789

# Create a PR with AI-generated description
qcoder github --create-pr
```

### Conversation Management

```bash
# List all saved conversations
qcoder conversations

# Resume a conversation
qcoder chat --resume conversation_name
```

### Configuration

```bash
# View project configuration
qcoder config

# View global configuration
qcoder config --global

# Set configuration values
qcoder config --set model=qwen/qwen3-coder:free
qcoder config --global --set max_context_length=16000
```

## Configuration Files

### Global Configuration

Located at `~/.qcoder/config.yaml` (Linux/Mac) or `%USERPROFILE%\.qcoder\config.yaml` (Windows):

```yaml
model: qwen/qwen3-coder:free
max_context_length: 8000
api_key: your_openrouter_api_key  # Optional, can use env var
```

### Project Configuration

Create `.qcoder/config.yaml` in your project:

```yaml
model: qwen/qwen3-coder:free
max_context_length: 8000
custom_setting: value
```

### Context Files

Create `.qcoder/QCODER.md` to provide project-specific context:

```markdown
# Project Context

This project is a web application built with React and FastAPI.

## Coding Standards

- Use TypeScript for all React components
- Follow PEP 8 for Python code
- Write unit tests for all API endpoints

## Important Notes

- Database migrations are in `backend/migrations/`
- API routes are defined in `backend/api/routes/`
```

## Workflow Automation

Create workflow YAML files for automated tasks:

```yaml
name: Code Analysis Workflow
description: Analyze all Python files in the project
stop_on_error: true

steps:
  - name: List Python Files
    type: shell
    command: find . -name "*.py" -type f

  - name: Analyze Code Quality
    type: ai_chat
    prompt: "Review the Python files and identify code quality issues"
    temperature: 0.3

  - name: Generate Report
    type: file_operation
    operation: write
    path: analysis_report.md
    content: "Analysis completed"
```

Execute workflows:

```bash
qcoder workflow run my_workflow.yaml
```

## Plugin System

Create custom plugins in `~/.qcoder/plugins/` or `.qcoder/plugins/`:

```python
# my_plugin.py

PLUGIN_METADATA = {
    "name": "my_plugin",
    "version": "1.0.0",
    "description": "My custom plugin",
    "author": "Your Name"
}

from qcoder.plugins.plugin_manager import command, hook

@command
def my_command(arg1, arg2):
    """Custom command implementation."""
    return f"Executed with {arg1} and {arg2}"

@hook("pre_chat")
def on_pre_chat(message):
    """Hook that runs before each chat message."""
    print(f"Processing: {message}")
```

## MCP Server Integration

QCoder includes a built-in MCP (Model Context Protocol) server for extending AI context:

```python
from qcoder.plugins.mcp_server import get_mcp_server

# Get MCP server instance
mcp = get_mcp_server()

# Use built-in context providers
file_tree = mcp.get_context("file_tree", root_path=".", max_depth=3)
git_status = mcp.get_context("git_status")
recent_files = mcp.get_context("recent_files", days=7)

# Register custom context provider
def my_context_provider(**kwargs):
    return "Custom context data"

mcp.register_context_provider(
    "my_context",
    my_context_provider,
    "Provides custom context"
)
```

## Environment Variables

- `OPENROUTER_API_KEY` - OpenRouter API key (required)
- `DEFAULT_MODEL` - Default AI model (default: qwen/qwen3-coder:free)
- `GITHUB_TOKEN` - GitHub personal access token (for GitHub integration)
- `SEARCH_API_KEY` - Search API key for web grounding (optional)
- `MAX_CONTEXT_LENGTH` - Maximum context length in tokens (default: 8000)
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)

## Available Models

QCoder uses OpenRouter API, which provides access to many models. Recommended free option:

- `qwen/qwen3-coder:free` - Free, optimized for coding tasks, multimodal support

Other options (may require payment):
- `anthropic/claude-3-sonnet`
- `openai/gpt-4-turbo`
- `google/gemini-pro`

## Development

### Project Structure

```
qcoder-cli/
├── src/qcoder/
│   ├── core/           # Core functionality
│   │   ├── config.py
│   │   ├── ai_client.py
│   │   └── conversation.py
│   ├── modules/        # Feature modules
│   │   ├── chat.py
│   │   ├── file_ops.py
│   │   ├── shell.py
│   │   ├── github_integration.py
│   │   ├── web_search.py
│   │   └── workflow.py
│   ├── plugins/        # Plugin system
│   │   ├── plugin_manager.py
│   │   └── mcp_server.py
│   ├── utils/          # Utilities
│   │   ├── output.py
│   │   └── logger.py
│   └── cli.py          # Main CLI entrypoint
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── pyproject.toml      # Project metadata
└── README.md          # This file
```

### Running Tests

```bash
pytest tests/
pytest --cov=qcoder tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## Troubleshooting

### API Key Issues

If you see "OpenRouter API key not found":

1. Create a `.env` file in your project or home directory
2. Add: `OPENROUTER_API_KEY=your_key_here`
3. Or export as environment variable: `export OPENROUTER_API_KEY=your_key`

### GitHub Integration Issues

For GitHub features, install GitHub CLI:

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Linux
sudo apt install gh  # Debian/Ubuntu
```

Authenticate with:

```bash
gh auth login
```

### Import Errors

If you see module import errors:

```bash
# Ensure you're in the project root
cd qcoder-cli

# Reinstall in development mode
pip install -e .
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

Inspired by Gemini CLI and powered by:
- [OpenRouter](https://openrouter.ai/) - Multi-model API access
- [Qwen3-Coder](https://huggingface.co/Qwen) - Free coding-optimized LLM
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - CLI framework
- [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/) - Interactive prompts

## Support

- GitHub Issues: https://github.com/yourusername/qcoder-cli/issues
- Documentation: https://github.com/yourusername/qcoder-cli#readme

---

Made with ❤️ for developers who love the terminal.
