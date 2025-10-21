"""Tests for file operations."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from qcoder.modules.file_ops import FileOperations


class TestFileOperationsInitialization:
    """Test FileOperations initialization."""

    def test_file_ops_initializes_ignore_patterns(self, mock_ai_client: Mock) -> None:
        """Test that FileOperations initializes with default ignore patterns."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                assert file_ops.ignore_patterns
                assert "__pycache__" in file_ops.ignore_patterns
                assert "*.pyc" in file_ops.ignore_patterns
                assert ".git" in file_ops.ignore_patterns


class TestFileOperationsReadFile:
    """Test file reading functionality."""

    def test_read_file_success(
        self, mock_ai_client: Mock, sample_python_file: Path
    ) -> None:
        """Test reading a file successfully."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                content = file_ops.read_file(sample_python_file)

                assert "def add" in content
                assert "return a + b" in content

    def test_read_file_not_found(self, mock_ai_client: Mock, tmp_path: Path) -> None:
        """Test reading non-existent file raises error."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                nonexistent = tmp_path / "nonexistent.py"

                with pytest.raises(FileNotFoundError):
                    file_ops.read_file(nonexistent)

    def test_read_file_directory_raises_error(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test reading directory raises error."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                with pytest.raises(ValueError):
                    file_ops.read_file(temp_project_dir)

    def test_read_file_with_encoding_error(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test reading file with encoding errors is handled."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                # Create file with binary content
                binary_file = temp_project_dir / "binary.bin"
                binary_file.write_bytes(b"\x80\x81\x82\x83")

                content = file_ops.read_file(binary_file)

                # Should return decoded with errors='replace'
                assert isinstance(content, str)


class TestFileOperationsWriteFile:
    """Test file writing functionality."""

    def test_write_file_creates_file(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test writing file creates it."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                test_file = temp_project_dir / "test.txt"
                content = "Test content"

                file_ops.write_file(test_file, content)

                assert test_file.exists()
                assert test_file.read_text() == content

    def test_write_file_creates_parent_directories(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test writing file creates parent directories."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                nested_file = temp_project_dir / "deep" / "nested" / "file.txt"

                file_ops.write_file(nested_file, "content")

                assert nested_file.exists()
                assert nested_file.parent.exists()

    def test_write_file_overwrites_existing(
        self, mock_ai_client: Mock, sample_python_file: Path
    ) -> None:
        """Test writing to existing file overwrites it."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                new_content = "New content"

                file_ops.write_file(sample_python_file, new_content)

                assert sample_python_file.read_text() == new_content


class TestFileOperationsShouldIgnore:
    """Test ignore pattern matching."""

    def test_should_ignore_pycache(self, mock_ai_client: Mock) -> None:
        """Test that __pycache__ is ignored."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                path = Path("/project/__pycache__/module.cpython-310.pyc")

                assert file_ops.should_ignore(path) is True

    def test_should_ignore_pyc_files(self, mock_ai_client: Mock) -> None:
        """Test that .pyc files are ignored."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                path = Path("/project/module.pyc")

                assert file_ops.should_ignore(path) is True

    def test_should_ignore_git_directory(self, mock_ai_client: Mock) -> None:
        """Test that .git directory is ignored."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                path = Path("/project/.git/config")

                assert file_ops.should_ignore(path) is True

    def test_should_not_ignore_python_files(self, mock_ai_client: Mock) -> None:
        """Test that regular Python files are not ignored."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                path = Path("/project/module.py")

                assert file_ops.should_ignore(path) is False


class TestFileOperationsCollectFiles:
    """Test file collection."""

    def test_collect_files_returns_files(
        self, mock_ai_client: Mock, temp_project_dir: Path, sample_python_file: Path
    ) -> None:
        """Test collecting files from directory."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                files = file_ops.collect_files(temp_project_dir, pattern="*.py")

                assert len(files) > 0
                assert sample_python_file in files

    def test_collect_files_single_file(
        self, mock_ai_client: Mock, sample_python_file: Path
    ) -> None:
        """Test collecting a single file."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                files = file_ops.collect_files(sample_python_file)

                assert files == [sample_python_file]

    def test_collect_files_respects_max_files(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test that collect_files respects max_files limit."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                # Create multiple files
                for i in range(10):
                    (temp_project_dir / f"file_{i}.py").write_text(f"# File {i}")

                files = file_ops.collect_files(temp_project_dir, pattern="*.py", max_files=5)

                assert len(files) <= 5

    def test_collect_files_non_recursive(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test collecting files non-recursively."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                # Create nested structure
                subdir = temp_project_dir / "subdir"
                subdir.mkdir()
                (subdir / "nested.py").write_text("# Nested")
                (temp_project_dir / "root.py").write_text("# Root")

                files = file_ops.collect_files(
                    temp_project_dir, pattern="*.py", recursive=False
                )

                # Only root file should be collected
                assert (temp_project_dir / "root.py") in files
                assert (subdir / "nested.py") not in files

    def test_collect_files_ignores_patterns(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test that collected files respect ignore patterns."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                # Create ignored files
                pycache_dir = temp_project_dir / "__pycache__"
                pycache_dir.mkdir()
                (pycache_dir / "cache.pyc").write_text("cache")
                (temp_project_dir / "normal.py").write_text("code")

                files = file_ops.collect_files(temp_project_dir, pattern="*.py*")

                # Should not include files in __pycache__
                assert all("__pycache__" not in str(f) for f in files)


class TestFileOperationsCleanCodeBlocks:
    """Test code block cleaning."""

    def test_clean_code_blocks_removes_markers(self, mock_ai_client: Mock) -> None:
        """Test that code block markers are removed."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                text = "```python\ndef hello():\n    pass\n```"
                cleaned = file_ops._clean_code_blocks(text)

                assert "```" not in cleaned
                assert "def hello():" in cleaned

    def test_clean_code_blocks_plain_text(self, mock_ai_client: Mock) -> None:
        """Test cleaning plain text without code blocks."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                text = "def hello():\n    pass"
                cleaned = file_ops._clean_code_blocks(text)

                assert cleaned == text


class TestFileOperationsSearchInFiles:
    """Test searching in files."""

    def test_search_in_files_finds_matches(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test searching for text in files."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                # Create files with different content
                (temp_project_dir / "file1.py").write_text("def function_one():\n    pass")
                (temp_project_dir / "file2.py").write_text("def function_two():\n    pass")

                results = file_ops.search_in_files(
                    temp_project_dir, search_query="function", pattern="*.py"
                )

                assert len(results) == 2
                # Verify it returns (file_path, [(line_num, line_content), ...])
                assert all(len(result) == 2 for result in results)

    def test_search_in_files_case_insensitive(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test that search is case-insensitive."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                (temp_project_dir / "file.py").write_text("HELLO World")

                results = file_ops.search_in_files(
                    temp_project_dir, search_query="hello"
                )

                assert len(results) == 1

    def test_search_in_files_returns_line_numbers(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test that search results include line numbers."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()

                (temp_project_dir / "file.py").write_text("line1\nmatch here\nline3")

                results = file_ops.search_in_files(
                    temp_project_dir, search_query="match"
                )

                assert len(results) == 1
                file_path, matches = results[0]
                assert len(matches) == 1
                line_num, line_content = matches[0]
                assert line_num == 2
                assert "match here" in line_content


class TestFileOperationsProcessWithAI:
    """Test AI-powered file processing."""

    def test_process_with_ai_file_not_found(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test processing non-existent file raises error."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                nonexistent = temp_project_dir / "nonexistent.py"

                with pytest.raises(FileNotFoundError):
                    file_ops.process_with_ai(nonexistent, "analyze this")

    def test_process_with_ai_invalid_path(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test processing invalid path raises error."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                invalid_path = temp_project_dir / "nonexistent_dir"

                with pytest.raises(ValueError):
                    file_ops.process_with_ai(invalid_path, "analyze")


class TestFileOperationsEdgeCases:
    """Test edge cases and error conditions."""

    def test_read_empty_file(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test reading empty file."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                empty_file = temp_project_dir / "empty.txt"
                empty_file.write_text("")

                content = file_ops.read_file(empty_file)

                assert content == ""

    def test_write_file_with_unicode(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test writing file with unicode characters."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                unicode_file = temp_project_dir / "unicode.txt"
                unicode_content = "Hello 世界 مرحبا 🚀"

                file_ops.write_file(unicode_file, unicode_content)

                read_content = file_ops.read_file(unicode_file)
                assert read_content == unicode_content

    def test_collect_files_empty_directory(
        self, mock_ai_client: Mock, temp_project_dir: Path
    ) -> None:
        """Test collecting files from empty directory."""
        with patch("qcoder.modules.file_ops.get_ai_client", return_value=mock_ai_client):
            with patch("qcoder.modules.file_ops.Console"):
                file_ops = FileOperations()
                empty_dir = temp_project_dir / "empty"
                empty_dir.mkdir()

                files = file_ops.collect_files(empty_dir)

                assert files == []
