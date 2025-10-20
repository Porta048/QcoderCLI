# QCoder CLI - Project Summary

## Overview

QCoder CLI is a production-ready, AI-powered command-line interface that replicates and extends the functionality of Gemini CLI. Built with Python 3.10+ and powered by Qwen3-Coder (free), it provides comprehensive code assistance, automation, and GitHub integration.

## ✅ Implemented Features

### Core Functionality

1. **Interactive AI Chat** (`src/qcoder/modules/chat.py`)
   - Conversational terminal interface
   - Context-aware responses
   - Command history and auto-suggestions
   - Built-in commands (/help, /save, /clear, etc.)
   - Session persistence

2. **Configuration Management** (`src/qcoder/core/config.py`)
   - Multi-level configuration (global, project, environment)
   - QCODER.md context files for custom project context
   - YAML-based configuration
   - Environment variable support

3. **Conversation Management** (`src/qcoder/core/conversation.py`)
   - Save/resume conversations (checkpoints)
   - Context trimming for token management
   - Conversation history tracking
   - Metadata and timestamps

### AI Integration

4. **AI Client** (`src/qcoder/core/ai_client.py`)
   - OpenRouter API integration
   - Qwen3-Coder free model support
   - Streaming and non-streaming responses
   - Token counting and management
   - Multi-model support

### File Operations

5. **File Manipulation** (`src/qcoder/modules/file_ops.py`)
   - Read/write/analyze files
   - AI-powered code transformation
   - Search across files
   - Directory traversal with ignore patterns
   - Batch file processing

### Shell Integration

6. **Shell Command Execution** (`src/qcoder/modules/shell.py`)
   - Execute shell commands with AI assistance
   - Command explanation
   - Dangerous command detection
   - Error analysis and fix suggestions
   - Interactive command builder

### GitHub Integration

7. **GitHub Operations** (`src/qcoder/modules/github_integration.py`)
   - Pull request reviews with AI
   - Issue analysis and triage
   - Automated PR creation
   - Commit message generation
   - GitHub CLI integration
   - GitPython for repository operations

### Web Search

8. **Web Grounding** (`src/qcoder/modules/web_search.py`)
   - DuckDuckGo search (no API key required)
   - Google Custom Search support
   - Search result summarization
   - Fact-checking capabilities
   - Grounded AI responses with sources

### Extensibility

9. **Plugin System** (`src/qcoder/plugins/plugin_manager.py`)
   - Dynamic plugin loading
   - Command registration
   - Hook system for events
   - Plugin discovery from multiple directories
   - Example plugin provided

10. **MCP Server** (`src/qcoder/plugins/mcp_server.py`)
    - Model Context Protocol implementation
    - Built-in context providers (file tree, git status, recent files)
    - Custom context provider registration
    - Tool registration system
    - Configuration persistence

### Automation

11. **Workflow System** (`src/qcoder/modules/workflow.py`)
    - YAML/JSON workflow definitions
    - Multiple step types (shell, ai_chat, file_operation, conditional)
    - Batch processing capabilities
    - Error handling and logging
    - Non-interactive execution

### Utilities

12. **Rich Terminal Output** (`src/qcoder/utils/output.py`)
    - Colored terminal output
    - Markdown rendering
    - Syntax highlighting
    - Tables and panels
    - Progress indicators
    - User prompts

13. **Logging** (`src/qcoder/utils/logger.py`)
    - File-based logging
    - Configurable log levels
    - Daily log rotation
    - Error tracking

### CLI Interface

14. **Main CLI** (`src/qcoder/cli.py`)
    - Click-based command interface
    - Multiple commands: chat, ask, file, shell, github, config, init, conversations
    - Short alias: `qc` in addition to `qcoder`
    - Help system
    - Version information

## Project Structure

```
QcoderCLI/
├── src/qcoder/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── ai_client.py           # AI API client
│   │   └── conversation.py        # Conversation handling
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── chat.py                # Interactive chat
│   │   ├── file_ops.py            # File operations
│   │   ├── shell.py               # Shell execution
│   │   ├── github_integration.py  # GitHub features
│   │   ├── web_search.py          # Web grounding
│   │   └── workflow.py            # Automation
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── plugin_manager.py      # Plugin system
│   │   └── mcp_server.py          # MCP implementation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── output.py              # Terminal output
│   │   └── logger.py              # Logging
│   ├── __init__.py
│   └── cli.py                     # Main CLI entrypoint
├── examples/
│   ├── example_plugin.py          # Example plugin
│   └── workflow_example.yaml      # Example workflow
├── .qcoder/
│   ├── config.example.yaml        # Configuration example
│   └── QCODER.example.md         # Context file example
├── pyproject.toml                 # Project metadata
├── setup.py                       # Setup script
├── requirements.txt               # Dependencies
├── .env.example                   # Environment variables
├── .gitignore                     # Git ignore rules
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                        # MIT License
└── PROJECT_SUMMARY.md            # This file
```

## Technical Specifications

### Dependencies

**Core Dependencies:**
- `openai>=1.50.0` - OpenRouter API client
- `click>=8.1.7` - CLI framework
- `rich>=13.7.0` - Terminal output formatting
- `prompt-toolkit>=3.0.43` - Interactive prompts
- `pygments>=2.17.2` - Syntax highlighting
- `pyyaml>=6.0.1` - YAML configuration
- `httpx>=0.27.0` - HTTP client
- `gitpython>=3.1.40` - Git operations
- `python-dotenv>=1.0.0` - Environment variables
- `tiktoken>=0.7.0` - Token counting

**Development Dependencies:**
- `pytest>=7.4.3` - Testing framework
- `black>=23.12.1` - Code formatting
- `ruff>=0.1.9` - Linting
- `mypy>=1.8.0` - Type checking

### Requirements

- Python 3.10 or higher
- OpenRouter API key (free tier available)
- Optional: GitHub CLI for GitHub features
- Optional: Git for repository operations

### Architecture Patterns

1. **Modular Design**: Clear separation between core, modules, plugins, and utilities
2. **Singleton Pattern**: Global instances for config, AI client, logger
3. **Plugin Architecture**: Extensible via decorators and dynamic loading
4. **Configuration Hierarchy**: Environment > Project > Global > Defaults
5. **Error Handling**: Comprehensive try-except blocks with logging
6. **Type Safety**: Full type hints throughout codebase

## Usage Examples

### Basic Chat
```bash
qcoder chat
```

### Code Analysis
```bash
qcoder file main.py --prompt "Explain this code"
```

### Shell Commands
```bash
qcoder shell --explain "git rebase -i HEAD~3"
```

### GitHub Integration
```bash
qcoder github --pr 123
qcoder github --create-pr
```

### Workflow Automation
```bash
qcoder workflow run analysis.yaml
```

## Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_key_here
DEFAULT_MODEL=qwen/qwen3-coder:free
GITHUB_TOKEN=your_github_token
MAX_CONTEXT_LENGTH=8000
LOG_LEVEL=INFO
```

### Config Files
- Global: `~/.qcoder/config.yaml`
- Project: `.qcoder/config.yaml`
- Context: `.qcoder/QCODER.md`

## Key Features Comparison

| Feature | QCoder CLI | Gemini CLI |
|---------|-----------|------------|
| Interactive Chat | ✅ | ✅ |
| Code Understanding | ✅ | ✅ |
| File Manipulation | ✅ | ✅ |
| Shell Integration | ✅ | ✅ |
| GitHub Integration | ✅ | ✅ |
| Web Grounding | ✅ | ✅ |
| Conversation Checkpoints | ✅ | ✅ |
| Custom Context Files | ✅ (QCODER.md) | ✅ (GEMINI.md) |
| Plugin System | ✅ | ✅ |
| MCP Server | ✅ | ✅ |
| Workflow Automation | ✅ | ✅ |
| Free Model Option | ✅ (Qwen3-Coder) | ❌ |
| Multi-Model Support | ✅ | ✅ |
| Rich Terminal Output | ✅ | ✅ |

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/qcoder-cli.git
cd qcoder-cli

# Install dependencies
pip install -r requirements.txt

# Install QCoder
pip install -e .

# Configure API key
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

## Testing

Currently, the test suite needs to be implemented. Test structure should follow:

```
tests/
├── core/
│   ├── test_config.py
│   ├── test_ai_client.py
│   └── test_conversation.py
├── modules/
│   ├── test_chat.py
│   ├── test_file_ops.py
│   ├── test_shell.py
│   ├── test_github_integration.py
│   ├── test_web_search.py
│   └── test_workflow.py
├── plugins/
│   ├── test_plugin_manager.py
│   └── test_mcp_server.py
└── utils/
    ├── test_output.py
    └── test_logger.py
```

## Future Enhancements

1. **Testing**: Comprehensive test suite with >80% coverage
2. **Performance**: Caching, async operations, parallel processing
3. **Security**: Enhanced input validation, sandboxed execution
4. **UI**: Terminal UI with panels and splits
5. **Features**:
   - Voice input/output
   - Multi-language support
   - IDE integrations
   - Docker support
   - Cloud sync
   - Team collaboration

## Known Limitations

1. Tests not yet implemented
2. Web search uses basic HTML parsing (no BeautifulSoup yet)
3. Plugin system could be extended with more hooks
4. Documentation could include video tutorials
5. Performance profiling not done

## Maintenance

- **Logs**: `~/.qcoder/logs/`
- **Cache**: `~/.qcoder/cache/`
- **Conversations**: `~/.qcoder/conversations/`
- **Config**: `~/.qcoder/config.yaml`

## Support

- GitHub Issues: Report bugs and request features
- Documentation: README.md, QUICKSTART.md, CONTRIBUTING.md
- Examples: `examples/` directory

## License

MIT License - See LICENSE file

## Credits

Developed as an open-source alternative to Gemini CLI, powered by:
- Qwen3-Coder for free, high-quality AI responses
- OpenRouter for multi-model API access
- Rich ecosystem of Python libraries

---

**Status**: ✅ Production-Ready (pending tests)

**Version**: 0.1.0

**Last Updated**: 2025-10-20
