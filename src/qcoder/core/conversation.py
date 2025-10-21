"""Conversation management with checkpoint support."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict, field

from .config import get_config


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary.

        Returns:
            Message as dictionary.
        """
        return asdict(self)

    def to_api_format(self) -> dict[str, str]:
        """Convert message to OpenAI API format.

        Returns:
            Message in API format (only role and content).
        """
        return {"role": self.role, "content": self.content}


class Conversation:
    """Manages conversation history and checkpoints."""

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_context_length: Optional[int] = None,
    ) -> None:
        """Initialize conversation manager.

        Args:
            conversation_id: Optional ID for this conversation.
            system_prompt: Optional system prompt to use.
            max_context_length: Maximum context length in tokens.
        """
        config = get_config()
        self.conversation_id = conversation_id or self._generate_id()
        self.max_context_length = max_context_length or config.max_context_length
        self.messages: list[Message] = []

        # Metadata - MUST be initialized before add_message()
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Add system prompt if provided
        if system_prompt:
            self.add_message("system", system_prompt)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique conversation ID.

        Returns:
            Unique conversation ID based on timestamp.
        """
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Message:
        """Add a message to the conversation.

        Args:
            role: Message role ('system', 'user', 'assistant').
            content: Message content.
            metadata: Optional metadata for the message.

        Returns:
            Created Message object.
        """
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
        return message

    def get_messages_for_api(self, max_messages: Optional[int] = None) -> list[dict[str, str]]:
        """Get messages formatted for API requests.

        Args:
            max_messages: Maximum number of recent messages to include.

        Returns:
            List of messages in API format.
        """
        messages = self.messages if max_messages is None else self.messages[-max_messages:]
        return [msg.to_api_format() for msg in messages]

    def trim_context(self, target_length: Optional[int] = None) -> None:
        """Trim conversation context to fit within token limit.

        Keeps system message and recent messages within token budget.

        Args:
            target_length: Target context length. Uses max_context_length if None.
        """
        target = target_length or self.max_context_length

        # Always keep system message if present
        system_messages = [msg for msg in self.messages if msg.role == "system"]
        other_messages = [msg for msg in self.messages if msg.role != "system"]

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        total_tokens = sum(len(msg.content) // 4 for msg in self.messages)

        # Remove oldest non-system messages until within budget
        while total_tokens > target and len(other_messages) > 1:
            removed = other_messages.pop(0)
            total_tokens -= len(removed.content) // 4

        self.messages = system_messages + other_messages

    def clear(self, keep_system: bool = True) -> None:
        """Clear conversation history.

        Args:
            keep_system: If True, keep system messages.
        """
        if keep_system:
            self.messages = [msg for msg in self.messages if msg.role == "system"]
        else:
            self.messages = []

        self.metadata["updated_at"] = datetime.now(timezone.utc).isoformat()

    def save_checkpoint(self, name: Optional[str] = None) -> Path:
        """Save conversation to a checkpoint file.

        Args:
            name: Optional checkpoint name. Uses conversation_id if None.

        Returns:
            Path to saved checkpoint file.
        """
        config = get_config()
        checkpoint_name = name or self.conversation_id
        checkpoint_path = config.conversation_dir / f"{checkpoint_name}.json"

        checkpoint_data = {
            "conversation_id": self.conversation_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "max_context_length": self.max_context_length,
        }

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

        return checkpoint_path

    @classmethod
    def load_checkpoint(cls, name: str) -> "Conversation":
        """Load conversation from a checkpoint file.

        Args:
            name: Checkpoint name (without .json extension).

        Returns:
            Loaded Conversation instance.

        Raises:
            FileNotFoundError: If checkpoint file doesn't exist.
        """
        config = get_config()
        checkpoint_path = config.conversation_dir / f"{name}.json"

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)

        conversation = cls(
            conversation_id=checkpoint_data["conversation_id"],
            max_context_length=checkpoint_data.get("max_context_length"),
        )

        # Restore messages
        conversation.messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp", ""),
                metadata=msg.get("metadata"),
            )
            for msg in checkpoint_data["messages"]
        ]

        # Restore metadata
        conversation.metadata = checkpoint_data.get("metadata", {})

        return conversation

    @staticmethod
    def list_checkpoints() -> list[dict[str, Any]]:
        """List all available conversation checkpoints.

        Returns:
            List of checkpoint information dictionaries.
        """
        config = get_config()
        checkpoints = []

        for path in config.conversation_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                checkpoints.append(
                    {
                        "name": path.stem,
                        "path": str(path),
                        "conversation_id": data.get("conversation_id", ""),
                        "created_at": data.get("metadata", {}).get("created_at", ""),
                        "updated_at": data.get("metadata", {}).get("updated_at", ""),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except Exception:
                # Skip invalid checkpoint files
                continue

        # Sort by updated_at descending
        checkpoints.sort(key=lambda x: x["updated_at"], reverse=True)
        return checkpoints

    def get_summary(self) -> dict[str, Any]:
        """Get conversation summary information.

        Returns:
            Summary dictionary with key conversation info.
        """
        message_counts = {}
        for msg in self.messages:
            message_counts[msg.role] = message_counts.get(msg.role, 0) + 1

        return {
            "conversation_id": self.conversation_id,
            "total_messages": len(self.messages),
            "message_counts": message_counts,
            "created_at": self.metadata.get("created_at"),
            "updated_at": self.metadata.get("updated_at"),
        }
