"""Tests for shell command execution."""

import subprocess
from unittest.mock import Mock, patch, MagicMock

import pytest

from qcoder.modules.shell import ShellExecutor


class TestShellExecutorInitialization:
    """Test ShellExecutor initialization."""

    def test_shell_executor_initializes(self, mock_ai_client: Mock) -> None:
        """Test that ShellExecutor initializes correctly."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()

                assert executor.ai_client is not None
                assert executor.dangerous_patterns
                assert isinstance(executor.is_windows, bool)

    def test_shell_executor_detects_windows(self, mock_ai_client: Mock) -> None:
        """Test that ShellExecutor detects Windows platform."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.platform.system", return_value="Windows"):
                    executor = ShellExecutor()
                    assert executor.is_windows is True

    def test_shell_executor_detects_non_windows(self, mock_ai_client: Mock) -> None:
        """Test that ShellExecutor detects non-Windows platforms."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.platform.system", return_value="Linux"):
                    executor = ShellExecutor()
                    assert executor.is_windows is False


class TestShellExecutorDangerousCommands:
    """Test dangerous command detection."""

    def test_detects_rm_rf(self, mock_ai_client: Mock) -> None:
        """Test detection of rm -rf command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("rm -rf /") is True

    def test_detects_del_f(self, mock_ai_client: Mock) -> None:
        """Test detection of del /f command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("del /f /s /q C:\\") is True

    def test_detects_format_command(self, mock_ai_client: Mock) -> None:
        """Test detection of format command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("format C:") is True

    def test_detects_fork_bomb(self, mock_ai_client: Mock) -> None:
        """Test detection of fork bomb."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous(":(){:|:&};:") is True

    def test_detects_dd_if(self, mock_ai_client: Mock) -> None:
        """Test detection of dd if command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("dd if=/dev/zero of=/dev/sda") is True

    def test_case_insensitive_detection(self, mock_ai_client: Mock) -> None:
        """Test that dangerous pattern detection is case-insensitive."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("RM -RF /") is True
                assert executor.is_dangerous("Format C:") is True

    def test_safe_command_not_detected(self, mock_ai_client: Mock) -> None:
        """Test that safe commands are not detected as dangerous."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                assert executor.is_dangerous("ls -la") is False
                assert executor.is_dangerous("echo hello") is False
                assert executor.is_dangerous("python script.py") is False


class TestShellExecutorExecution:
    """Test command execution."""

    def test_execute_simple_command(self, mock_ai_client: Mock) -> None:
        """Test executing a simple command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = "command output"
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("echo hello")

                    assert "command output" in output

    def test_execute_command_with_timeout(self, mock_ai_client: Mock) -> None:
        """Test executing command with timeout."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    executor = ShellExecutor()

                    executor.execute("sleep 10", timeout=5)

                    # Verify timeout was passed
                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["timeout"] == 5

    def test_execute_timeout_raises_error(self, mock_ai_client: Mock) -> None:
        """Test that timeout raises RuntimeError."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

                    executor = ShellExecutor()

                    with pytest.raises(RuntimeError) as exc_info:
                        executor.execute("slow_command", timeout=5)

                    assert "timed out" in str(exc_info.value)

    def test_execute_command_not_found(self, mock_ai_client: Mock) -> None:
        """Test that command not found raises RuntimeError."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_run.side_effect = FileNotFoundError()

                    executor = ShellExecutor()

                    with pytest.raises(RuntimeError) as exc_info:
                        executor.execute("nonexistent_command")

                    assert "not found" in str(exc_info.value)

    def test_execute_with_stderr(self, mock_ai_client: Mock) -> None:
        """Test command execution with stderr output."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = "output"
                    mock_result.stderr = "error message"
                    mock_result.returncode = 1
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("failing_command")

                    assert "[STDERR]" in output
                    assert "error message" in output

    def test_execute_no_capture(self, mock_ai_client: Mock) -> None:
        """Test command execution without capturing output."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("command", capture_output=False)

                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["capture_output"] is False

    def test_execute_dangerous_command_requires_confirmation(
        self, mock_ai_client: Mock
    ) -> None:
        """Test that dangerous commands require confirmation."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console") as mock_console_class:
                mock_console = Mock()
                mock_console_class.return_value = mock_console
                mock_console.confirm.return_value = False

                executor = ShellExecutor()
                executor.console = mock_console

                result = executor.execute("rm -rf /", check_dangerous=True)

                assert "cancelled by user" in result
                mock_console.confirm.assert_called_once()

    def test_execute_dangerous_command_with_confirmation(
        self, mock_ai_client: Mock
    ) -> None:
        """Test dangerous command execution with user confirmation."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console") as mock_console_class:
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_console = Mock()
                    mock_console_class.return_value = mock_console
                    mock_console.confirm.return_value = True

                    mock_result = Mock()
                    mock_result.stdout = "deleted"
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    executor.console = mock_console
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("rm -rf /", check_dangerous=True)

                    mock_console.confirm.assert_called_once()
                    assert "deleted" in output


class TestShellExecutorExplainCommand:
    """Test command explanation."""

    def test_explain_command(self, mock_ai_client: Mock) -> None:
        """Test getting AI explanation of a command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                mock_ai_client.extract_text_response.return_value = (
                    "This command lists all files in the current directory."
                )

                explanation = executor.explain_command("ls -la")

                assert "lists" in explanation
                mock_ai_client.chat.assert_called_once()


class TestShellExecutorSuggestCommand:
    """Test command suggestion."""

    def test_suggest_command(self, mock_ai_client: Mock) -> None:
        """Test getting AI suggestion for command."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                mock_ai_client.extract_text_response.return_value = "grep -r 'pattern' ."

                suggestion = executor.suggest_command("Find all Python files")

                assert suggestion
                mock_ai_client.chat.assert_called_once()


class TestShellExecutorAnalysis:
    """Test command analysis and fixing."""

    def test_execute_with_ai_analysis(self, mock_ai_client: Mock) -> None:
        """Test executing command with AI analysis."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = "output"
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output, analysis = executor.execute_with_ai_analysis("ls")

                    assert output
                    assert analysis
                    # Chat should be called for both command and analysis
                    assert mock_ai_client.chat.call_count >= 1

    def test_suggest_fix_for_error(self, mock_ai_client: Mock) -> None:
        """Test getting AI fix suggestion for command error."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                executor = ShellExecutor()
                mock_ai_client.extract_text_response.return_value = (
                    "The file path is incorrect. Try: find . -name 'file.txt'"
                )

                fix = executor.suggest_fix_for_error("find /invalid", "No such file or directory")

                assert fix
                assert "No such file" in mock_ai_client.chat.call_args[0][0]


class TestShellExecutorEdgeCases:
    """Test edge cases and error conditions."""

    def test_execute_empty_output(self, mock_ai_client: Mock) -> None:
        """Test command with empty output."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("true")

                    assert "successfully" in output.lower()

    def test_execute_with_non_zero_exit(self, mock_ai_client: Mock) -> None:
        """Test command with non-zero exit code."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_result.returncode = 127
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", False):
                        output = executor.execute("nonexistent")

                    assert "127" in output

    def test_execute_windows_uses_shell_true(self, mock_ai_client: Mock) -> None:
        """Test that Windows execution uses shell=True."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    mock_result = Mock()
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_result.returncode = 0
                    mock_run.return_value = mock_result

                    executor = ShellExecutor()
                    with patch.object(executor, "is_windows", True):
                        executor.execute("echo test")

                    call_kwargs = mock_run.call_args[1]
                    assert call_kwargs["shell"] is True

    def test_execute_unix_uses_shlex(self, mock_ai_client: Mock) -> None:
        """Test that Unix execution uses shlex parsing."""
        with patch("qcoder.modules.shell.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.shell.Console"):
                with patch("qcoder.modules.shell.subprocess.run") as mock_run:
                    with patch("qcoder.modules.shell.shlex.split") as mock_shlex:
                        mock_shlex.return_value = ["echo", "test"]
                        mock_result = Mock()
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        mock_result.returncode = 0
                        mock_run.return_value = mock_result

                        executor = ShellExecutor()
                        with patch.object(executor, "is_windows", False):
                            executor.execute("echo test")

                        mock_shlex.assert_called_once()
