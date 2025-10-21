"""Main CLI entrypoint for QCoder."""

import sys
import click
from pathlib import Path
from typing import Optional

from .core.config import get_config
from .core.conversation import Conversation
from .modules.chat import ChatSession
from .modules.file_ops import FileOperations
from .modules.shell import ShellExecutor
from .modules.github_integration import GitHubIntegration
from .utils.output import Console


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit.")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """QCoder - AI-powered CLI assistant for code, chat, and automation.

    Run 'qcoder chat' to start an interactive conversation with the AI.
    """
    if version:
        from . import __version__

        click.echo(f"QCoder CLI v{__version__}")
        ctx.exit(0)

    if ctx.invoked_subcommand is None:
        # Default behavior: start chat session
        ctx.invoke(chat)


@main.command()
@click.option(
    "--resume",
    "-r",
    "checkpoint_name",
    help="Resume conversation from checkpoint.",
)
@click.option(
    "--model",
    "-m",
    help="Override default AI model.",
)
@click.option(
    "--system",
    "-s",
    help="Custom system prompt.",
)
@click.option(
    "--no-context",
    is_flag=True,
    help="Disable loading context from QCODER.md files.",
)
def chat(
    checkpoint_name: Optional[str],
    model: Optional[str],
    system: Optional[str],
    no_context: bool,
) -> None:
    """Start an interactive AI chat session.

    Examples:
        qcoder chat
        qcoder chat --model qwen/qwen3-coder:free
        qcoder chat --resume my_session
        qcoder chat --system "You are a Python expert"
    """
    console = Console()

    try:
        # Load or create conversation
        if checkpoint_name:
            try:
                conversation = Conversation.load_checkpoint(checkpoint_name)
                console.info(f"Resumed conversation: {checkpoint_name}")
            except FileNotFoundError:
                console.error(f"Checkpoint not found: {checkpoint_name}")
                sys.exit(1)
        else:
            # Build system prompt
            config = get_config()
            context = "" if no_context else config.get_context()

            system_prompt = system or "You are QCoder, an AI-powered coding assistant. Help users with code, explanations, debugging, and automation tasks."

            if context:
                system_prompt += f"\n\n# Context\n{context}"

            conversation = Conversation(system_prompt=system_prompt)

        # Start chat session
        chat_session = ChatSession(conversation=conversation, model=model)
        chat_session.start()

    except KeyboardInterrupt:
        console.info("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
@click.argument("prompt")
@click.option(
    "--model",
    "-m",
    help="Override default AI model.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Save response to file.",
)
def ask(prompt: str, model: Optional[str], output: Optional[str]) -> None:
    """Ask a single question to the AI (non-interactive).

    Examples:
        qcoder ask "How do I read a file in Python?"
        qcoder ask "Explain this error" --output explanation.txt
    """
    console = Console()

    try:
        from .core.ai_client import get_ai_client

        client = get_ai_client()
        if model:
            client.model = model

        messages = [
            {"role": "system", "content": "You are QCoder, an AI coding assistant."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat(messages)
        answer = client.extract_text_response(response)

        if output:
            Path(output).write_text(answer, encoding="utf-8")
            console.success(f"Response saved to: {output}")
        else:
            console.print_markdown(answer)

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
def conversations() -> None:
    """List all saved conversation checkpoints.

    Shows conversation ID, creation time, and message count.
    """
    console = Console()

    try:
        checkpoints = Conversation.list_checkpoints()

        if not checkpoints:
            console.info("No saved conversations found.")
            return

        console.print_table(
            headers=["Name", "Created", "Updated", "Messages"],
            rows=[
                [
                    cp["name"],
                    cp["created_at"][:19] if cp["created_at"] else "N/A",
                    cp["updated_at"][:19] if cp["updated_at"] else "N/A",
                    str(cp["message_count"]),
                ]
                for cp in checkpoints
            ],
            title="Saved Conversations",
        )

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--prompt",
    "-p",
    help="What to do with the file(s).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path.",
)
def file(path: str, prompt: Optional[str], output: Optional[str]) -> None:
    """Analyze or manipulate files using AI.

    Examples:
        qcoder file main.py --prompt "Explain this code"
        qcoder file . --prompt "Find all TODO comments"
        qcoder file script.py --prompt "Add docstrings" --output improved.py
    """
    console = Console()

    try:
        file_ops = FileOperations()
        result = file_ops.process_with_ai(
            path=Path(path),
            prompt=prompt or "Analyze this file",
            output_path=Path(output) if output else None,
        )

        console.print_markdown(result)

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
@click.argument("command", nargs=-1, required=True)
@click.option(
    "--explain",
    is_flag=True,
    help="Explain the command before executing.",
)
@click.option(
    "--auto-approve",
    "-y",
    is_flag=True,
    help="Auto-approve command execution.",
)
def shell(command: tuple[str, ...], explain: bool, auto_approve: bool) -> None:
    """Execute shell commands with AI assistance.

    Examples:
        qcoder shell git status
        qcoder shell --explain git rebase -i HEAD~3
        qcoder shell npm install --auto-approve
    """
    console = Console()

    try:
        shell_exec = ShellExecutor()
        cmd = " ".join(command)

        if explain:
            explanation = shell_exec.explain_command(cmd)
            console.print_markdown(f"**Command Explanation:**\n\n{explanation}")

            if not auto_approve:
                if not click.confirm("\nExecute this command?"):
                    console.info("Command cancelled.")
                    return

        result = shell_exec.execute(cmd)
        console.print(result)

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
@click.argument("repo", required=False)
@click.option(
    "--pr",
    type=int,
    help="Pull request number to review.",
)
@click.option(
    "--issue",
    type=int,
    help="Issue number to analyze.",
)
@click.option(
    "--create-pr",
    is_flag=True,
    help="Create a pull request from current branch.",
)
def github(
    repo: Optional[str],
    pr: Optional[int],
    issue: Optional[int],
    create_pr: bool,
) -> None:
    """GitHub integration for PR review, issue triage, and automation.

    Examples:
        qcoder github --pr 123
        qcoder github owner/repo --issue 456
        qcoder github --create-pr
    """
    console = Console()

    try:
        gh = GitHubIntegration()

        if create_pr:
            result = gh.create_pull_request()
            console.print_markdown(result)
        elif pr:
            result = gh.review_pull_request(repo, pr)
            console.print_markdown(result)
        elif issue:
            result = gh.analyze_issue(repo, issue)
            console.print_markdown(result)
        else:
            console.error("Specify --pr, --issue, or --create-pr")
            sys.exit(1)

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--global-config",
    "global_scope",
    is_flag=True,
    help="Show or modify global configuration.",
)
@click.option(
    "--set",
    "set_key",
    help="Set configuration key=value.",
)
def config(global_scope: bool, set_key: Optional[str]) -> None:
    """Manage QCoder configuration.

    Examples:
        qcoder config
        qcoder config --global-config
        qcoder config --set model=qwen/qwen3-coder:free
        qcoder config --global-config --set api_key=your-key
    """
    console = Console()

    try:
        cfg = get_config()

        if set_key:
            if "=" not in set_key:
                console.error("Invalid format. Use: key=value")
                sys.exit(1)

            key, value = set_key.split("=", 1)
            config_dict = cfg.global_config if global_scope else cfg.project_config
            config_dict[key] = value
            cfg.save_config(config_dict, global_scope)
            console.success(f"Set {key}={value}")
        else:
            # Display configuration
            config_data = cfg.global_config if global_scope else cfg.project_config
            scope = "Global" if global_scope else "Project"

            if not config_data:
                console.info(f"No {scope.lower()} configuration found.")
            else:
                console.print_dict(config_data, title=f"{scope} Configuration")

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


@main.command()
def init() -> None:
    """Initialize QCoder in the current directory.

    Creates .qcoder directory with default configuration files.
    """
    console = Console()

    try:
        project_dir = Path.cwd() / ".qcoder"
        project_dir.mkdir(exist_ok=True)

        config_file = project_dir / "config.yaml"
        context_file = project_dir / "QCODER.md"

        if not config_file.exists():
            config_file.write_text(
                "# QCoder Project Configuration\n"
                "model: qwen/qwen3-coder:free\n"
                "max_context_length: 8000\n",
                encoding="utf-8",
            )

        if not context_file.exists():
            context_file.write_text(
                "# Project Context for QCoder\n\n"
                "This file provides additional context to the AI about your project.\n\n"
                "## Project Description\n\n"
                "Describe your project here.\n\n"
                "## Coding Standards\n\n"
                "List any coding standards or conventions.\n\n"
                "## Important Notes\n\n"
                "Add any important information the AI should know.\n",
                encoding="utf-8",
            )

        console.success(f"Initialized QCoder in {project_dir}")
        console.info(f"Edit {context_file} to customize context.")

    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
