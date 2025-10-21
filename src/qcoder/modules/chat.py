"""Interactive chat session module."""

import sys
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

from ..core.conversation import Conversation
from ..core.ai_client import get_ai_client
from ..core.config import get_config
from ..utils.output import Console
from ..utils.banner import print_banner


class ChatSession:
    """Manages an interactive chat session with the AI."""

    def __init__(
        self,
        conversation: Optional[Conversation] = None,
        model: Optional[str] = None,
    ) -> None:
        """Initialize chat session.

        Args:
            conversation: Existing conversation to use.
            model: Override AI model.
        """
        self.conversation = conversation or Conversation()
        self.console = Console()
        self.ai_client = get_ai_client()

        if model:
            self.ai_client.model = model

        # Setup prompt toolkit
        config = get_config()
        history_file = config.config_dir / "chat_history.txt"
        self.prompt_session: PromptSession[str] = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=Style.from_dict(
                {
                    "prompt": "cyan bold",
                }
            ),
        )

        # Special commands
        self.commands = {
            "/help": self._show_help,
            "/clear": self._clear_conversation,
            "/save": self._save_conversation,
            "/summary": self._show_summary,
            "/exit": self._exit_session,
            "/quit": self._exit_session,
        }

    def start(self) -> None:
        """Start the interactive chat session."""
        print_banner()
        self.console.rule("QCoder Chat Session", style="cyan")
        self.console.info(
            f"Using model: {self.ai_client.model}\n"
            "Type your message or use /help for commands."
        )

        while True:
            try:
                # Get user input
                user_input = self.prompt_session.prompt("\n> ", multiline=False)

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.split()[0]
                    if command in self.commands:
                        self.commands[command](user_input)
                        continue
                    else:
                        self.console.error(f"Unknown command: {command}. Type /help for available commands.")
                        continue

                # Add user message to conversation
                self.conversation.add_message("user", user_input)
                self.console.print_user_message(user_input)

                # Get AI response
                response = self._get_ai_response()

                # Add assistant response to conversation
                self.conversation.add_message("assistant", response)
                self.console.print_assistant_message(response)

            except KeyboardInterrupt:
                self.console.info("\nUse /exit to quit or continue chatting.")
                continue
            except EOFError:
                self._exit_session("")
                break

    def _get_ai_response(self) -> str:
        """Get AI response for current conversation.

        Returns:
            AI response text.
        """
        try:
            # Trim context if needed
            self.conversation.trim_context()

            # Get messages for API
            messages = self.conversation.get_messages_for_api()

            # Show spinner while waiting
            with self.console.spinner() as progress:
                progress.add_task("Generating response...", total=None)
                response = self.ai_client.chat(messages, stream=False)

            return self.ai_client.extract_text_response(response)

        except Exception as e:
            self.console.error(f"Failed to get AI response: {e}")
            return "I apologize, but I encountered an error. Please try again."

    def _show_help(self, _: str) -> None:
        """Show help message with available commands."""
        help_text = """
**Available Commands:**

- `/help` - Show this help message
- `/clear` - Clear conversation history (keeps system prompt)
- `/save [name]` - Save conversation checkpoint
- `/summary` - Show conversation summary
- `/exit` or `/quit` - Exit chat session

**Tips:**

- Press Ctrl+C to interrupt (conversation continues)
- Use arrow keys to navigate history
- Multi-line input: Use Shift+Enter (in supported terminals)
        """
        self.console.print_markdown(help_text.strip())

    def _clear_conversation(self, _: str) -> None:
        """Clear conversation history."""
        self.conversation.clear(keep_system=True)
        self.console.success("Conversation cleared. System prompt retained.")

    def _save_conversation(self, command: str) -> None:
        """Save conversation to checkpoint.

        Args:
            command: Command string, may include checkpoint name.
        """
        parts = command.split(maxsplit=1)
        name = parts[1] if len(parts) > 1 else None

        try:
            checkpoint_path = self.conversation.save_checkpoint(name)
            self.console.success(f"Conversation saved: {checkpoint_path.stem}")
        except Exception as e:
            self.console.error(f"Failed to save conversation: {e}")

    def _show_summary(self, _: str) -> None:
        """Show conversation summary."""
        summary = self.conversation.get_summary()
        self.console.print_dict(summary, title="Conversation Summary")

    def _exit_session(self, _: str) -> None:
        """Exit the chat session."""
        if self.console.confirm("\nSave this conversation before exiting?", default=False):
            self._save_conversation("/save")

        self.console.info("Goodbye!")
        sys.exit(0)
