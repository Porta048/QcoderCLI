"""Workflow automation for non-interactive script integration."""

import json
import subprocess
from pathlib import Path
from typing import Any, Optional
import yaml

from ..core.ai_client import get_ai_client
from ..core.conversation import Conversation
from ..utils.output import Console
from ..utils.logger import get_logger


class WorkflowAutomation:
    """Handles workflow automation and non-interactive execution."""

    def __init__(self) -> None:
        """Initialize workflow automation."""
        self.ai_client = get_ai_client()
        self.console = Console()
        self.logger = get_logger()

    def execute_workflow(self, workflow_path: Path) -> dict[str, Any]:
        """Execute a workflow from a YAML or JSON file.

        Args:
            workflow_path: Path to workflow definition file.

        Returns:
            Workflow execution results.

        Raises:
            FileNotFoundError: If workflow file doesn't exist.
        """
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

        # Load workflow definition
        if workflow_path.suffix in [".yaml", ".yml"]:
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow = yaml.safe_load(f)
        elif workflow_path.suffix == ".json":
            with open(workflow_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
        else:
            raise ValueError(f"Unsupported workflow file format: {workflow_path.suffix}")

        self.logger.info(f"Executing workflow: {workflow.get('name', 'Unnamed')}")

        # Execute workflow steps
        results = {
            "workflow": workflow.get("name", "Unnamed"),
            "steps": [],
            "success": True,
        }

        for i, step in enumerate(workflow.get("steps", []), 1):
            step_name = step.get("name", f"Step {i}")
            self.logger.info(f"Executing step: {step_name}")

            try:
                step_result = self._execute_step(step)
                results["steps"].append(
                    {
                        "name": step_name,
                        "status": "success",
                        "result": step_result,
                    }
                )
            except Exception as e:
                self.logger.error(f"Step failed: {step_name}", exc_info=True)
                results["steps"].append(
                    {
                        "name": step_name,
                        "status": "failed",
                        "error": str(e),
                    }
                )
                results["success"] = False

                # Stop on error if configured
                if workflow.get("stop_on_error", True):
                    break

        return results

    def _execute_step(self, step: dict[str, Any]) -> Any:
        """Execute a single workflow step.

        Args:
            step: Step definition.

        Returns:
            Step execution result.
        """
        step_type = step.get("type")

        if step_type == "shell":
            return self._execute_shell_step(step)
        elif step_type == "ai_chat":
            return self._execute_ai_chat_step(step)
        elif step_type == "file_operation":
            return self._execute_file_operation_step(step)
        elif step_type == "conditional":
            return self._execute_conditional_step(step)
        else:
            raise ValueError(f"Unknown step type: {step_type}")

    def _execute_shell_step(self, step: dict[str, Any]) -> str:
        """Execute shell command step.

        Args:
            step: Step definition.

        Returns:
            Command output.
        """
        command = step.get("command")
        if not command:
            raise ValueError("Shell step missing 'command' field")

        # SECURITY: Never use shell=True to prevent command injection
        # Parse command into argument list safely
        import shlex
        import platform

        try:
            # Use shlex to safely split command into arguments
            # This prevents shell injection attacks
            if isinstance(command, str):
                # Platform-specific command splitting
                if platform.system() == "Windows":
                    # Windows: Use list mode or split carefully
                    # For Windows, recommend using list format in workflows
                    args = shlex.split(command, posix=False)
                else:
                    # Unix-like systems: POSIX-compliant splitting
                    args = shlex.split(command)
            elif isinstance(command, list):
                # Already in safe list format
                args = command
            else:
                raise ValueError("Command must be a string or list")

            # SECURITY: Execute without shell=True
            result = subprocess.run(
                args,
                shell=False,  # Critical: prevents command injection
                capture_output=True,
                text=True,
                timeout=step.get("timeout", 300),
            )

            if result.returncode != 0 and step.get("fail_on_error", True):
                raise RuntimeError(f"Command failed: {result.stderr}")

            return result.stdout

        except ValueError as e:
            raise ValueError(f"Invalid command format: {e}")
        except FileNotFoundError:
            raise RuntimeError(f"Command not found. Ensure the executable is in PATH.")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command timed out after {step.get('timeout', 300)} seconds")

    def _execute_ai_chat_step(self, step: dict[str, Any]) -> str:
        """Execute AI chat step.

        Args:
            step: Step definition.

        Returns:
            AI response.
        """
        prompt = step.get("prompt")
        if not prompt:
            raise ValueError("AI chat step missing 'prompt' field")

        system_prompt = step.get("system_prompt", "You are QCoder, an AI assistant.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        response = self.ai_client.chat(
            messages,
            temperature=step.get("temperature", 0.7),
        )

        return self.ai_client.extract_text_response(response)

    def _execute_file_operation_step(self, step: dict[str, Any]) -> str:
        """Execute file operation step.

        Args:
            step: Step definition.

        Returns:
            Operation result.
        """
        operation = step.get("operation")
        path = Path(step.get("path", ""))

        if operation == "read":
            return path.read_text(encoding="utf-8")

        elif operation == "write":
            content = step.get("content", "")
            path.write_text(content, encoding="utf-8")
            return f"Written to {path}"

        elif operation == "delete":
            path.unlink()
            return f"Deleted {path}"

        else:
            raise ValueError(f"Unknown file operation: {operation}")

    def _execute_conditional_step(self, step: dict[str, Any]) -> Any:
        """Execute conditional step.

        Args:
            step: Step definition.

        Returns:
            Result from executed branch.
        """
        condition = step.get("condition")
        if not condition:
            raise ValueError("Conditional step missing 'condition' field")

        # SECURITY: Use safe condition evaluation instead of eval()
        # Only support simple boolean literals and basic comparisons
        condition_met = self._evaluate_safe_condition(condition)

        if condition_met:
            return self._execute_step(step.get("then", {}))
        else:
            else_step = step.get("else")
            if else_step:
                return self._execute_step(else_step)
            return None

    def _evaluate_safe_condition(self, condition: str) -> bool:
        """Safely evaluate a condition string without using eval().

        Args:
            condition: Condition string to evaluate.

        Returns:
            Boolean result of condition evaluation.

        Raises:
            ValueError: If condition contains unsafe operations.
        """
        # SECURITY: Whitelist approach - only allow safe literal values
        # Strip whitespace for comparison
        condition = condition.strip().lower()

        # Allow simple boolean literals
        if condition == "true":
            return True
        elif condition == "false":
            return False

        # For more complex conditions, recommend using step results or environment variables
        # This prevents arbitrary code execution while maintaining workflow functionality
        raise ValueError(
            f"Unsafe or unsupported condition: '{condition}'. "
            "Only 'true' and 'false' boolean literals are supported for security. "
            "For complex conditions, use step results or environment checks in your workflow."
        )

    def run_batch_processing(
        self,
        input_items: list[Any],
        process_func: str,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Run batch processing on multiple items.

        Args:
            input_items: List of items to process.
            process_func: Function to apply ('ai_analyze', 'ai_transform', etc.).
            **kwargs: Additional arguments for the processing function.

        Returns:
            List of processing results.
        """
        results = []

        for i, item in enumerate(input_items, 1):
            self.logger.info(f"Processing item {i}/{len(input_items)}")

            try:
                if process_func == "ai_analyze":
                    result = self._ai_analyze(item, **kwargs)
                elif process_func == "ai_transform":
                    result = self._ai_transform(item, **kwargs)
                else:
                    raise ValueError(f"Unknown process function: {process_func}")

                results.append(
                    {
                        "index": i,
                        "item": item,
                        "status": "success",
                        "result": result,
                    }
                )

            except Exception as e:
                self.logger.error(f"Failed to process item {i}", exc_info=True)
                results.append(
                    {
                        "index": i,
                        "item": item,
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return results

    def _ai_analyze(self, item: Any, prompt_template: str = "") -> str:
        """Analyze item with AI.

        Args:
            item: Item to analyze.
            prompt_template: Prompt template with {item} placeholder.

        Returns:
            AI analysis.
        """
        prompt = prompt_template.format(item=item) if prompt_template else f"Analyze: {item}"

        messages = [
            {"role": "system", "content": "You are an expert analyzer."},
            {"role": "user", "content": prompt},
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def _ai_transform(self, item: Any, transformation: str = "") -> str:
        """Transform item with AI.

        Args:
            item: Item to transform.
            transformation: Transformation description.

        Returns:
            Transformed result.
        """
        prompt = f"{transformation}\n\nInput: {item}"

        messages = [
            {"role": "system", "content": "You are an expert at transforming data."},
            {"role": "user", "content": prompt},
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)

    def create_workflow_template(self, output_path: Path) -> None:
        """Create a workflow template file.

        Args:
            output_path: Path to save template.
        """
        template = {
            "name": "Example Workflow",
            "description": "A sample workflow for QCoder automation",
            "stop_on_error": True,
            "steps": [
                {
                    "name": "Shell Command Example",
                    "type": "shell",
                    "command": "echo 'Hello from workflow'",
                    "timeout": 30,
                },
                {
                    "name": "AI Analysis Example",
                    "type": "ai_chat",
                    "prompt": "Analyze the current project structure and suggest improvements.",
                    "temperature": 0.7,
                },
                {
                    "name": "File Operation Example",
                    "type": "file_operation",
                    "operation": "write",
                    "path": "output.txt",
                    "content": "Workflow completed successfully",
                },
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        self.console.success(f"Workflow template created: {output_path}")
