# QCoder CLI - Quick Start Guide

Get up and running with QCoder in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qcoder-cli.git
cd qcoder-cli

# Install dependencies
pip install -r requirements.txt

# Install QCoder
pip install -e .
```

## Configuration

1. **Get an OpenRouter API key** (free):
   - Visit https://openrouter.ai/
   - Sign up and get your API key

2. **Create a `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Add your API key** to `.env`:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

## First Steps

### 1. Start a Chat

```bash
qcoder chat
```

Try asking:
- "Explain what a Python decorator is"
- "How do I read a file in Python?"
- "Write a function to reverse a string"

### 2. Initialize a Project

```bash
cd your-project
qcoder init
```

This creates:
- `.qcoder/config.yaml` - Project configuration
- `.qcoder/QCODER.md` - Project context for AI

### 3. Analyze Code

```bash
# Explain a file
qcoder file main.py --prompt "Explain this code"

# Find TODOs
qcoder file . --prompt "Find all TODO comments"

# Add documentation
qcoder file script.py --prompt "Add docstrings" --output improved.py
```

### 4. Execute Shell Commands

```bash
# Run with explanation
qcoder shell --explain git status

# Execute directly
qcoder shell ls -la
```

### 5. Ask Quick Questions

```bash
qcoder ask "How do I parse JSON in Python?"
```

## Common Commands

### Chat Commands (in interactive mode)

```
/help       - Show help
/clear      - Clear conversation
/save       - Save conversation
/summary    - Show summary
/exit       - Quit
```

### CLI Commands

```bash
# View all conversations
qcoder conversations

# Resume a conversation
qcoder chat --resume conversation_name

# Configure settings
qcoder config --set model=qwen/qwen3-coder:free

# View configuration
qcoder config
```

## Next Steps

### Customize Context

Edit `.qcoder/QCODER.md` in your project:

```markdown
# My Project

This is a Python web app using Flask.

## Standards

- Use type hints
- Write tests for all functions
- Follow PEP 8
```

### GitHub Integration

Install GitHub CLI:

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Authenticate
gh auth login
```

Use GitHub features:

```bash
# Review PR
qcoder github --pr 123

# Create PR
qcoder github --create-pr
```

### Create Plugins

Create `~/.qcoder/plugins/my_plugin.py`:

```python
PLUGIN_METADATA = {
    "name": "my_plugin",
    "version": "1.0.0",
    "description": "My custom plugin",
    "author": "Your Name"
}

from qcoder.plugins.plugin_manager import command

@command
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"
```

### Workflow Automation

Create `workflow.yaml`:

```yaml
name: Code Analysis
steps:
  - name: Analyze Code
    type: ai_chat
    prompt: "Review the code quality"

  - name: Generate Report
    type: file_operation
    operation: write
    path: report.md
    content: "Analysis complete"
```

Run it:

```bash
qcoder workflow run workflow.yaml
```

## Tips

1. **Save conversations** for later reference:
   ```bash
   /save my_session
   ```

2. **Use custom system prompts**:
   ```bash
   qcoder chat --system "You are a Python expert focused on web development"
   ```

3. **Customize context** per project with `.qcoder/QCODER.md`

4. **Set default model**:
   ```bash
   qcoder config --set model=qwen/qwen3-coder:free
   ```

5. **Check logs** if something goes wrong:
   ```
   ~/.qcoder/logs/
   ```

## Troubleshooting

### "API key not found"

Make sure `.env` exists and contains:
```
OPENROUTER_API_KEY=your_key_here
```

### "Command not found: qcoder"

Reinstall:
```bash
pip install -e .
```

### Import errors

Ensure you're in the project root:
```bash
cd qcoder-cli
pip install -e .
```

## Getting Help

- **Documentation**: See README.md
- **Examples**: Check `examples/` directory
- **Issues**: https://github.com/yourusername/qcoder-cli/issues

## What's Next?

- Explore the full README.md for all features
- Try the example plugin in `examples/example_plugin.py`
- Create custom workflows for your projects
- Contribute to the project!

Happy coding with QCoder! 🚀
