"""Shell command execution with AI assistance."""

import subprocess
import shlex
import platform
from typing import Optional

from ..core.ai_client import get_ai_client
from ..utils.output import Console


class ShellExecutor:
    """Executes shell commands with AI assistance and safety checks."""

    def __init__(self) -> None:
        """Initialize shell executor."""
        self.ai_client = get_ai_client()
        self.console = Console()
        self.is_windows = platform.system() == "Windows"

        # Dangerous commands that require extra confirmation
        self.dangerous_patterns = [
            "rm -rf",
            "del /f",
            "format",
            "mkfs",
            ":(){:|:&};:",  # Fork bomb
            "dd if=",
            "> /dev/",
        ]

    def is_dangerous(self, command: str) -> bool:
        """Check if command is potentially dangerous.

        Args:
            command: Command string to check.

        Returns:
            True if command matches dangerous patterns.
        """
        cmd_lower = command.lower()
        return any(pattern.lower() in cmd_lower for pattern in self.dangerous_patterns)

    def explain_command(self, command: str) -> str:
        """Get AI explanation of a shell command.

        Args:
            command: Shell command to explain.

        Returns:
            Explanation of the command.
        """
        messages = [
            {
                "role": "system",
                "content": "You are a shell command expert. Explain commands clearly and warn about potential risks.",
            },
            {
                "role": "user",
                "content": f"Explain this shell command:\n\n```bash\n{command}\n```\n\n"
                "Include:\n"
                "1. What it does\n"
                "2. Each flag/option explained\n"
                "3. Potential side effects or risks\n"
                "4. Expected output",
            },
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def suggest_command(self, task_description: str) -> str:
        """Get AI suggestion for command to accomplish a task.

        Args:
            task_description: Description of what to accomplish.

        Returns:
            Suggested command with explanation.
        """
        os_info = "Windows" if self.is_windows else "Unix-like"

        messages = [
            {
                "role": "system",
                "content": f"You are a shell command expert for {os_info} systems. "
                "Suggest safe, efficient commands with explanations.",
            },
            {
                "role": "user",
                "content": f"Suggest a shell command to accomplish this task:\n\n{task_description}\n\n"
                "Provide:\n"
                "1. The command\n"
                "2. Brief explanation\n"
                "3. Any important warnings",
            },
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def execute(
        self,
        command: str,
        check_dangerous: bool = True,
        timeout: Optional[int] = None,
        capture_output: bool = True,
    ) -> str:
        """Execute a shell command.

        Args:
            command: Command to execute.
            check_dangerous: Whether to check for dangerous commands.
            timeout: Command timeout in seconds.
            capture_output: Whether to capture and return output.

        Returns:
            Command output or execution status.

        Raises:
            RuntimeError: If command execution fails.
        """
        # Safety check
        if check_dangerous and self.is_dangerous(command):
            self.console.warning(f"Potentially dangerous command detected: {command}")
            if not self.console.confirm("Are you sure you want to execute this?", default=False):
                return "Command execution cancelled by user."

        try:
            # Parse command based on OS
            if self.is_windows:
                # Windows: use shell=True for proper command parsing
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            else:
                # Unix-like: use shlex for proper parsing
                args = shlex.split(command)
                result = subprocess.run(
                    args,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    check=False,
                )

            # Format output
            output_parts = []

            if capture_output:
                if result.stdout:
                    output_parts.append(result.stdout)
                if result.stderr:
                    output_parts.append(f"[STDERR]\n{result.stderr}")

            output = "\n".join(output_parts) if output_parts else ""

            # Add return code info
            if result.returncode != 0:
                status = f"\n[Exit code: {result.returncode}]"
                if output:
                    output += status
                else:
                    output = f"Command failed with exit code {result.returncode}"

            return output or "Command completed successfully."

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError(f"Command not found: {command.split()[0]}")
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}") from e

    def execute_with_ai_analysis(self, command: str) -> tuple[str, str]:
        """Execute command and get AI analysis of the output.

        Args:
            command: Command to execute.

        Returns:
            Tuple of (command_output, ai_analysis).
        """
        # Execute command
        output = self.execute(command)

        # Get AI analysis if there's output or errors
        if output and output != "Command completed successfully.":
            messages = [
                {
                    "role": "system",
                    "content": "You are a shell output analysis expert. "
                    "Analyze command output and provide actionable insights.",
                },
                {
                    "role": "user",
                    "content": f"Analyze the output of this command:\n\n"
                    f"Command: `{command}`\n\n"
                    f"Output:\n```\n{output}\n```\n\n"
                    "Provide:\n"
                    "1. Summary of what happened\n"
                    "2. Any errors or warnings explained\n"
                    "3. Suggested next steps if applicable",
                },
            ]

            response = self.ai_client.chat(messages)
            analysis = self.ai_client.extract_text_response(response)
        else:
            analysis = "Command executed successfully with no output."

        return output, analysis

    def suggest_fix_for_error(self, command: str, error_output: str) -> str:
        """Get AI suggestion to fix command error.

        Args:
            command: Command that failed.
            error_output: Error output from the command.

        Returns:
            Suggested fix.
        """
        messages = [
            {
                "role": "system",
                "content": "You are a shell troubleshooting expert. "
                "Diagnose errors and suggest clear, actionable fixes.",
            },
            {
                "role": "user",
                "content": f"This command failed:\n\n"
                f"Command: `{command}`\n\n"
                f"Error:\n```\n{error_output}\n```\n\n"
                "Please:\n"
                "1. Diagnose the problem\n"
                "2. Suggest a corrected command\n"
                "3. Explain what went wrong and how the fix addresses it",
            },
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def interactive_command_builder(self, goal: str) -> Optional[str]:
        """Interactively build a command with AI assistance.

        Args:
            goal: What the user wants to accomplish.

        Returns:
            Final command to execute, or None if cancelled.
        """
        # Get initial suggestion
        self.console.info(f"Goal: {goal}")
        suggestion = self.suggest_command(goal)
        self.console.print_markdown(suggestion)

        while True:
            choice = self.console.prompt(
                "\n[e]xecute, [m]odify, [ex]plain, or [c]ancel?", default="e"
            ).lower()

            if choice == "e" or choice == "execute":
                # Extract command from suggestion (look for code blocks)
                lines = suggestion.split("\n")
                for line in lines:
                    if line.strip() and not line.startswith("#") and not line.startswith("-"):
                        # Simple heuristic: first non-comment line might be the command
                        potential_cmd = line.strip().strip("`")
                        if potential_cmd:
                            return potential_cmd
                return self.console.prompt("Enter command to execute:")

            elif choice == "m" or choice == "modify":
                modification = self.console.prompt("What changes do you want?")
                suggestion = self.suggest_command(f"{goal}\n\nModification: {modification}")
                self.console.print_markdown(suggestion)

            elif choice == "ex" or choice == "explain":
                command = self.console.prompt("Enter command to explain:")
                explanation = self.explain_command(command)
                self.console.print_markdown(explanation)

            elif choice == "c" or choice == "cancel":
                return None

            else:
                self.console.warning("Invalid choice. Please choose e, m, ex, or c.")
