"""Setup script for QCoder CLI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="qcoder",
    version="0.1.0",
    description="AI-powered CLI assistant for code, chat, and automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="QCoder Team",
    url="https://github.com/yourusername/qcoder-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.50.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
        "pygments>=2.17.2",
        "pyyaml>=6.0.1",
        "httpx>=0.27.0",
        "gitpython>=3.1.40",
        "watchdog>=4.0.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "ruff>=0.1.9",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qcoder=qcoder.cli:main",
            "qc=qcoder.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords="ai cli code-assistant automation gemini coding terminal",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/qcoder-cli/issues",
        "Source": "https://github.com/yourusername/qcoder-cli",
    },
)
