"""GitHub integration for PR review, issue triage, and automation."""

from typing import Optional, Any
import subprocess
from pathlib import Path

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from ..core.ai_client import get_ai_client
from ..core.config import get_config
from ..utils.output import Console


class GitHubIntegration:
    """Handles GitHub operations with AI assistance."""

    def __init__(self) -> None:
        """Initialize GitHub integration."""
        self.ai_client = get_ai_client()
        self.console = Console()
        self.config = get_config()

        if not GIT_AVAILABLE:
            self.console.warning("GitPython not installed. Some features may be limited.")

        # Check for GitHub CLI
        self.gh_cli_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI (gh) is available.

        Returns:
            True if gh CLI is installed.
        """
        try:
            subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _get_repo(self) -> Any:
        """Get current Git repository.

        Returns:
            Repo object.

        Raises:
            RuntimeError: If not in a Git repository.
        """
        if not GIT_AVAILABLE:
            raise RuntimeError("GitPython not installed. Run: pip install gitpython")

        try:
            return Repo(Path.cwd(), search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise RuntimeError("Not in a Git repository")

    def _run_gh_command(self, args: list[str]) -> str:
        """Run GitHub CLI command.

        Args:
            args: Command arguments for gh CLI.

        Returns:
            Command output.

        Raises:
            RuntimeError: If gh CLI is not available or command fails.
        """
        if not self.gh_cli_available:
            raise RuntimeError(
                "GitHub CLI (gh) not installed. Install from: https://cli.github.com/"
            )

        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"GitHub CLI command failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("GitHub CLI command timed out")

    def review_pull_request(self, repo: Optional[str], pr_number: int) -> str:
        """Review a pull request with AI assistance.

        Args:
            repo: Repository in format "owner/repo". If None, uses current repo.
            pr_number: Pull request number.

        Returns:
            AI review of the pull request.
        """
        # Get PR details
        args = ["pr", "view", str(pr_number), "--json", "title,body,files,commits"]
        if repo:
            args.extend(["-R", repo])

        pr_data = self._run_gh_command(args)

        # Get PR diff
        diff_args = ["pr", "diff", str(pr_number)]
        if repo:
            diff_args.extend(["-R", repo])

        pr_diff = self._run_gh_command(diff_args)

        # Get AI review
        messages = [
            {
                "role": "system",
                "content": "You are an expert code reviewer. Provide thorough, constructive reviews "
                "focusing on code quality, potential bugs, security issues, and best practices.",
            },
            {
                "role": "user",
                "content": f"Review this pull request:\n\n"
                f"PR Data:\n```json\n{pr_data}\n```\n\n"
                f"Diff:\n```diff\n{pr_diff[:5000]}\n```\n\n"  # Limit diff size
                "Provide:\n"
                "1. Summary of changes\n"
                "2. Code quality assessment\n"
                "3. Potential issues or bugs\n"
                "4. Security concerns\n"
                "5. Suggestions for improvement\n"
                "6. Overall recommendation (approve/request changes)",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)

    def analyze_issue(self, repo: Optional[str], issue_number: int) -> str:
        """Analyze a GitHub issue with AI assistance.

        Args:
            repo: Repository in format "owner/repo". If None, uses current repo.
            issue_number: Issue number.

        Returns:
            AI analysis of the issue.
        """
        # Get issue details
        args = [
            "issue",
            "view",
            str(issue_number),
            "--json",
            "title,body,labels,comments",
        ]
        if repo:
            args.extend(["-R", repo])

        issue_data = self._run_gh_command(args)

        # Get AI analysis
        messages = [
            {
                "role": "system",
                "content": "You are an expert at triaging GitHub issues. Analyze issues thoroughly "
                "and provide actionable recommendations.",
            },
            {
                "role": "user",
                "content": f"Analyze this GitHub issue:\n\n"
                f"```json\n{issue_data}\n```\n\n"
                "Provide:\n"
                "1. Issue summary\n"
                "2. Priority assessment (high/medium/low)\n"
                "3. Suggested labels\n"
                "4. Potential root cause\n"
                "5. Recommended next steps\n"
                "6. Similar issues (if mentioned in comments)",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)

    def create_pull_request(
        self,
        title: Optional[str] = None,
        body: Optional[str] = None,
        base: str = "main",
    ) -> str:
        """Create a pull request from current branch with AI-generated description.

        Args:
            title: PR title. If None, AI generates it.
            body: PR body. If None, AI generates it.
            base: Base branch for PR.

        Returns:
            PR creation result.
        """
        repo = self._get_repo()

        if repo.is_dirty():
            self.console.warning("Repository has uncommitted changes.")

        # Get current branch
        current_branch = repo.active_branch.name

        if current_branch == base:
            raise RuntimeError(f"Cannot create PR from base branch '{base}'")

        # Get diff between current branch and base
        try:
            diff = repo.git.diff(f"{base}...{current_branch}")
        except GitCommandError:
            raise RuntimeError(f"Failed to get diff between {current_branch} and {base}")

        if not diff:
            raise RuntimeError("No changes to create PR from")

        # Get commit messages
        commits = list(repo.iter_commits(f"{base}..{current_branch}"))
        commit_messages = "\n".join([f"- {c.message.strip()}" for c in commits])

        # Generate PR title and body with AI if not provided
        if not title or not body:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at writing clear, concise pull request descriptions. "
                    "Follow conventional commit and PR best practices.",
                },
                {
                    "role": "user",
                    "content": f"Generate a pull request title and description for these changes:\n\n"
                    f"Commits:\n{commit_messages}\n\n"
                    f"Diff (first 3000 chars):\n```diff\n{diff[:3000]}\n```\n\n"
                    "Provide:\n"
                    "1. A concise, descriptive title (one line)\n"
                    "2. A detailed description with:\n"
                    "   - Summary of changes\n"
                    "   - Motivation and context\n"
                    "   - Testing performed\n"
                    "   - Breaking changes (if any)\n\n"
                    "Format:\n"
                    "TITLE: <title here>\n\n"
                    "BODY:\n<description here>",
                },
            ]

            response = self.ai_client.chat(messages, temperature=0.3)
            generated = self.ai_client.extract_text_response(response)

            # Parse generated content
            parts = generated.split("BODY:", 1)
            if not title and "TITLE:" in parts[0]:
                title = parts[0].split("TITLE:", 1)[1].strip()
            if not body and len(parts) > 1:
                body = parts[1].strip()

        # Fallback values
        title = title or f"Changes from {current_branch}"
        body = body or "AI-generated pull request"

        # Create PR using gh CLI
        args = [
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
        ]

        result = self._run_gh_command(args)
        return f"Pull request created successfully!\n\n{result}"

    def suggest_commit_message(self) -> str:
        """Generate AI-suggested commit message for staged changes.

        Returns:
            Suggested commit message.
        """
        repo = self._get_repo()

        # Get staged diff
        try:
            diff = repo.git.diff("--cached")
        except GitCommandError:
            raise RuntimeError("Failed to get staged changes")

        if not diff:
            raise RuntimeError("No staged changes to commit")

        # Get AI suggestion
        messages = [
            {
                "role": "system",
                "content": "You are an expert at writing conventional commit messages. "
                "Follow the format: <type>(<scope>): <description>",
            },
            {
                "role": "user",
                "content": f"Generate a commit message for these staged changes:\n\n"
                f"```diff\n{diff[:5000]}\n```\n\n"
                "Provide:\n"
                "1. A conventional commit message\n"
                "2. Brief explanation of the changes\n\n"
                "Types: feat, fix, docs, style, refactor, test, chore",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)

    def auto_triage_issues(self, repo: Optional[str], limit: int = 10) -> str:
        """Automatically triage multiple issues.

        Args:
            repo: Repository in format "owner/repo". If None, uses current repo.
            limit: Maximum number of issues to triage.

        Returns:
            Triage summary.
        """
        # Get open issues
        args = ["issue", "list", "--limit", str(limit), "--json", "number,title,body"]
        if repo:
            args.extend(["-R", repo])

        issues_data = self._run_gh_command(args)

        # Get AI triage
        messages = [
            {
                "role": "system",
                "content": "You are an expert at triaging GitHub issues. Analyze and prioritize issues efficiently.",
            },
            {
                "role": "user",
                "content": f"Triage these GitHub issues:\n\n"
                f"```json\n{issues_data}\n```\n\n"
                "For each issue, provide:\n"
                "1. Priority (high/medium/low)\n"
                "2. Suggested labels\n"
                "3. Brief recommendation\n\n"
                "Format as a table for easy reading.",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)
