# QCoder CLI - Installation Guide

## Quick Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Step 1: Get the Code

```bash
# Clone from GitHub
git clone https://github.com/yourusername/qcoder-cli.git
cd qcoder-cli

# Or download and extract the ZIP
# Then navigate to the directory
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install QCoder

```bash
# Install in development mode (recommended for now)
pip install -e .
```

This will install two commands:
- `qcoder` - Full command name
- `qc` - Short alias

### Step 4: Get API Key

1. Visit [OpenRouter API Keys](https://openrouter.ai/keys)
2. Sign up for a free account
3. Create an API key from the dashboard

### Step 5: Configure API Key and Model

Create a `.env` file in the project directory:

```bash
# Copy the example
cp .env.example .env

# Edit and configure:
# OPENROUTER_API_KEY=your_actual_key_here
# DEFAULT_MODEL=google/gemini-2.0-flash-exp:free
```

Choose your preferred model from [OpenRouter Models](https://openrouter.ai/models)

Or set as environment variable:

```bash
# Linux/macOS
export OPENROUTER_API_KEY=your_key_here

# Windows PowerShell
$env:OPENROUTER_API_KEY="your_key_here"

# Windows CMD
set OPENROUTER_API_KEY=your_key_here
```

### Step 6: Verify Installation

```bash
# Check version
qcoder --version

# Start chat
qcoder chat
```

You should see the interactive chat interface!

## Installation Methods

### Method 1: Development Install (Recommended)

Best for testing and contributing:

```bash
cd qcoder-cli
pip install -e .
```

Changes to the code are immediately reflected without reinstalling.

### Method 2: Regular Install

For production use:

```bash
cd qcoder-cli
pip install .
```

### Method 3: From PyPI (Coming Soon)

Once published:

```bash
pip install qcoder
```

## Virtual Environment (Recommended)

Use a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install QCoder
pip install -e .
```

## Post-Installation Setup

### Initialize Your First Project

```bash
cd your-project-directory
qcoder init
```

This creates:
- `.qcoder/config.yaml` - Project configuration
- `.qcoder/QCODER.md` - Project context

### Test the Installation

```bash
# Ask a simple question
qcoder ask "What is Python?"

# Start interactive chat
qcoder chat

# Check configuration
qcoder config
```

## Optional Components

### GitHub CLI (for GitHub integration)

**macOS:**
```bash
brew install gh
gh auth login
```

**Windows:**
```bash
winget install GitHub.cli
gh auth login
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora
sudo dnf install gh

# Authenticate
gh auth login
```

### Git (for repository operations)

Most systems have Git installed. If not:

**macOS:**
```bash
brew install git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/)

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install git

# Fedora
sudo dnf install git
```

## Configuration Files

### Global Configuration

Located at:
- **Linux/macOS**: `~/.qcoder/config.yaml`
- **Windows**: `%USERPROFILE%\.qcoder\config.yaml`

Create manually or use:

```bash
mkdir -p ~/.qcoder
cat > ~/.qcoder/config.yaml << EOF
model: qwen/qwen3-coder:free
max_context_length: 8000
log_level: INFO
EOF
```

### Environment Variables

All available environment variables:

```bash
# Required
OPENROUTER_API_KEY=your_key_here

# Optional
DEFAULT_MODEL=qwen/qwen3-coder:free
MAX_CONTEXT_LENGTH=8000
LOG_LEVEL=INFO
GITHUB_TOKEN=your_github_token
SEARCH_API_KEY=your_search_key
```

## Troubleshooting Installation

### "Command not found: qcoder"

```bash
# Ensure installation succeeded
pip show qcoder

# Try reinstalling
pip uninstall qcoder
pip install -e .

# Check if in PATH
which qcoder  # Linux/macOS
where qcoder  # Windows
```

### Import Errors

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

### Permission Errors

```bash
# Linux/macOS - Use user install
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -e .
```

### API Key Issues

```bash
# Verify .env file exists and has correct content
cat .env  # Should show OPENROUTER_API_KEY=...

# Or set as system environment variable
export OPENROUTER_API_KEY=your_key  # Linux/macOS
$env:OPENROUTER_API_KEY="your_key"  # Windows PS
```

### Windows-Specific Issues

If you encounter errors on Windows:

1. **Use Command Prompt or PowerShell as Administrator**
2. **Install Visual C++ Build Tools** if prompted
3. **Update pip**: `python -m pip install --upgrade pip`

### Module Not Found Errors

```bash
# Ensure you're in the correct directory
cd qcoder-cli

# Reinstall in development mode
pip install -e .

# Check installed packages
pip list | grep qcoder
```

## Updating QCoder

### Development Install

```bash
cd qcoder-cli
git pull origin main
pip install -e .
```

### Regular Install

```bash
cd qcoder-cli
git pull origin main
pip install --upgrade .
```

## Uninstallation

```bash
# Uninstall package
pip uninstall qcoder

# Remove configuration (optional)
rm -rf ~/.qcoder  # Linux/macOS
rmdir /s %USERPROFILE%\.qcoder  # Windows
```

## Platform-Specific Notes

### Linux

Works out of the box on most distributions. Ensure Python 3.10+ is installed:

```bash
python3 --version
sudo apt install python3.10  # If needed
```

### macOS

Use Homebrew for dependencies:

```bash
brew install python@3.10
brew install gh  # For GitHub features
```

### Windows

1. Install Python from [python.org](https://www.python.org/)
2. Ensure "Add Python to PATH" is checked during installation
3. Use PowerShell or Command Prompt
4. Some features may require Windows Subsystem for Linux (WSL)

## Docker Installation (Alternative)

Coming soon: Docker image for isolated execution.

```bash
# Build image (when Dockerfile is available)
docker build -t qcoder .

# Run container
docker run -it -e OPENROUTER_API_KEY=your_key qcoder chat
```

## Verification Checklist

After installation, verify these work:

- [ ] `qcoder --version` shows version number
- [ ] `qcoder chat` starts interactive session
- [ ] `qcoder ask "test"` returns AI response
- [ ] `qcoder config` shows configuration
- [ ] `qcoder init` creates .qcoder directory
- [ ] Environment variables are set correctly
- [ ] No import errors when running commands

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Search [GitHub Issues](https://github.com/yourusername/qcoder-cli/issues)
4. Create a new issue with:
   - Your OS and Python version
   - Installation method used
   - Complete error message
   - Steps to reproduce

## Next Steps

Once installed:

1. Read [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Explore [README.md](README.md) for all features
3. Try examples in `examples/` directory
4. Customize `.qcoder/QCODER.md` for your projects

Happy coding with QCoder! 🚀
