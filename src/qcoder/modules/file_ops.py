"""File and directory operations with AI assistance."""

import os
from pathlib import Path
from typing import Optional
import fnmatch

from ..core.ai_client import get_ai_client
from ..utils.output import Console
from ..utils.validators import validate_glob_pattern, ValidationError


class FileOperations:
    """Handles file and directory manipulation with AI assistance."""

    def __init__(self) -> None:
        """Initialize file operations handler."""
        self.ai_client = get_ai_client()
        self.console = Console()

        # Default ignore patterns
        self.ignore_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".qcoder/cache",
            ".qcoder/logs",
            "*.log",
            ".DS_Store",
        ]

        # SECURITY: Define allowed base directories for file operations
        # This prevents path traversal attacks
        self.allowed_base_dirs = [
            Path.cwd().resolve(),  # Current working directory
            Path.home().resolve(),  # User home directory
        ]

    def _validate_path(self, path: Path, operation: str = "access") -> Path:
        """Validate path to prevent directory traversal attacks.

        Args:
            path: Path to validate.
            operation: Operation being performed (for error messages).

        Returns:
            Resolved, validated path.

        Raises:
            ValueError: If path is outside allowed directories or contains dangerous patterns.
        """
        # SECURITY: Resolve path to absolute form and resolve symlinks
        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path for {operation}: {e}")

        # SECURITY: Check for path traversal attempts
        # Ensure resolved path is within allowed base directories
        is_allowed = False
        for base_dir in self.allowed_base_dirs:
            try:
                # Check if resolved_path is relative to base_dir
                resolved_path.relative_to(base_dir)
                is_allowed = True
                break
            except ValueError:
                # Path is not relative to this base_dir, continue checking
                continue

        if not is_allowed:
            raise ValueError(
                f"Access denied: Path '{path}' is outside allowed directories. "
                f"Allowed base directories: {[str(d) for d in self.allowed_base_dirs]}"
            )

        # SECURITY: Additional dangerous path checks
        path_str = str(resolved_path).lower()

        # Prevent access to sensitive system directories
        dangerous_paths = [
            "/etc/passwd", "/etc/shadow", "c:\\windows\\system32",
            "/root/", "c:\\users\\administrator\\",
        ]

        for dangerous in dangerous_paths:
            if dangerous in path_str:
                raise ValueError(f"Access denied: Cannot {operation} sensitive system path")

        return resolved_path

    def read_file(self, path: Path) -> str:
        """Read file contents.

        Args:
            path: Path to file.

        Returns:
            File contents as string.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If path is invalid or outside allowed directories.
        """
        # SECURITY: Validate path before reading
        validated_path = self._validate_path(path, operation="read")

        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {validated_path}")

        if not validated_path.is_file():
            raise ValueError(f"Not a file: {validated_path}")

        try:
            return validated_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try reading as binary and decode with error handling
            content = validated_path.read_bytes()
            return content.decode("utf-8", errors="replace")

    def write_file(self, path: Path, content: str) -> None:
        """Write content to file.

        Args:
            path: Path to file.
            content: Content to write.

        Raises:
            ValueError: If path is invalid or outside allowed directories.
        """
        # SECURITY: Validate path before writing
        validated_path = self._validate_path(path, operation="write")

        # Ensure parent directory exists
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        validated_path.write_text(content, encoding="utf-8")

    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored.

        Args:
            path: Path to check.

        Returns:
            True if path matches ignore patterns.
        """
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
        return False

    def collect_files(
        self,
        root: Path,
        pattern: str = "*",
        recursive: bool = True,
        max_files: int = 100,
    ) -> list[Path]:
        """Collect files matching pattern.

        Args:
            root: Root directory to search.
            pattern: File pattern (glob style).
            recursive: Whether to search recursively.
            max_files: Maximum files to collect.

        Returns:
            List of file paths.

        Raises:
            ValidationError: If glob pattern is invalid.
        """
        # Validate glob pattern
        try:
            pattern = validate_glob_pattern(pattern)
        except ValidationError as e:
            self.console.error(f"Invalid glob pattern: {e}")
            raise

        files: list[Path] = []

        if root.is_file():
            return [root]

        if not root.is_dir():
            return []

        glob_pattern = f"**/{pattern}" if recursive else pattern

        try:
            for path in root.glob(glob_pattern):
                if len(files) >= max_files:
                    self.console.warning(f"Reached maximum file limit ({max_files})")
                    break

                if path.is_file() and not self.should_ignore(path):
                    files.append(path)
        except (ValueError, OSError) as e:
            # Catch glob execution errors (e.g., invalid pattern syntax)
            raise ValidationError(
                f"Failed to process glob pattern '{pattern}': {e}"
            ) from e

        return files

    def analyze_file(self, path: Path, prompt: Optional[str] = None) -> str:
        """Analyze a file using AI.

        Args:
            path: Path to file.
            prompt: Optional custom analysis prompt.

        Returns:
            AI analysis result.
        """
        content = self.read_file(path)

        analysis_prompt = prompt or f"Analyze this code from {path.name}:"

        messages = [
            {
                "role": "system",
                "content": "You are a code analysis expert. Analyze code thoroughly and provide clear, actionable insights.",
            },
            {"role": "user", "content": f"{analysis_prompt}\n\n```\n{content}\n```"},
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def transform_file(
        self,
        path: Path,
        transformation_prompt: str,
        output_path: Optional[Path] = None,
    ) -> str:
        """Transform a file using AI.

        Args:
            path: Path to source file.
            transformation_prompt: What transformation to apply.
            output_path: Optional output path. If None, returns transformed content.

        Returns:
            Transformed content or success message.
        """
        content = self.read_file(path)

        messages = [
            {
                "role": "system",
                "content": "You are a code transformation expert. When transforming code, output ONLY the transformed code without explanations or markdown formatting.",
            },
            {
                "role": "user",
                "content": f"{transformation_prompt}\n\nOriginal code from {path.name}:\n\n```\n{content}\n```\n\nProvide only the transformed code:",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        transformed = self.ai_client.extract_text_response(response)

        # Clean markdown code blocks if present
        transformed = self._clean_code_blocks(transformed)

        if output_path:
            self.write_file(output_path, transformed)
            return f"Transformed code written to: {output_path}"

        return transformed

    def _clean_code_blocks(self, text: str) -> str:
        """Remove markdown code block formatting.

        Args:
            text: Text potentially containing markdown code blocks.

        Returns:
            Cleaned text.
        """
        lines = text.split("\n")

        # Remove starting ``` or ```language
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        # Remove ending ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines)

    def search_in_files(
        self,
        root: Path,
        search_query: str,
        pattern: str = "*.py",
        max_results: int = 50,
    ) -> list[tuple[Path, list[tuple[int, str]]]]:
        """Search for text in files.

        Args:
            root: Root directory to search.
            search_query: Text to search for.
            pattern: File pattern to search in.
            max_results: Maximum number of results.

        Returns:
            List of (file_path, [(line_number, line_content), ...]) tuples.
        """
        results: list[tuple[Path, list[tuple[int, str]]]] = []
        files = self.collect_files(root, pattern, recursive=True, max_files=max_results)

        for file_path in files:
            try:
                content = self.read_file(file_path)
                matches = []

                for line_num, line in enumerate(content.splitlines(), start=1):
                    if search_query.lower() in line.lower():
                        matches.append((line_num, line.strip()))

                if matches:
                    results.append((file_path, matches))

            except Exception:
                continue

        return results

    def process_with_ai(
        self,
        path: Path,
        prompt: str,
        output_path: Optional[Path] = None,
    ) -> str:
        """Process file or directory with AI based on prompt.

        Args:
            path: Path to file or directory.
            prompt: What to do with the file(s).
            output_path: Optional output path.

        Returns:
            AI response or transformed content.
        """
        # Check if it's a transformation or analysis request
        transformation_keywords = [
            "add",
            "modify",
            "change",
            "refactor",
            "improve",
            "fix",
            "update",
            "rewrite",
        ]

        is_transformation = any(keyword in prompt.lower() for keyword in transformation_keywords)

        if path.is_file():
            if is_transformation and not output_path:
                self.console.warning(
                    "Transformation requested without output path. "
                    "Showing preview. Use --output to save changes."
                )

            if is_transformation:
                return self.transform_file(path, prompt, output_path)
            else:
                return self.analyze_file(path, prompt)

        elif path.is_dir():
            # For directories, collect and analyze files
            files = self.collect_files(path, max_files=20)

            if not files:
                return "No files found to process."

            file_contents = []
            for file in files[:10]:  # Limit to 10 files for context
                try:
                    content = self.read_file(file)
                    file_contents.append(f"File: {file.relative_to(path)}\n```\n{content}\n```\n")
                except Exception:
                    continue

            combined = "\n".join(file_contents)

            messages = [
                {
                    "role": "system",
                    "content": "You are a code analysis expert. Analyze multiple files and provide comprehensive insights.",
                },
                {"role": "user", "content": f"{prompt}\n\n{combined}"},
            ]

            response = self.ai_client.chat(messages)
            return self.ai_client.extract_text_response(response)

        else:
            raise ValueError(f"Invalid path: {path}")
