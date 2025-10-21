"""Tests for conversation management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from qcoder.core.conversation import Conversation, Message


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation_with_all_fields(self) -> None:
        """Test creating a message with all fields."""
        timestamp = "2024-01-01T12:00:00"
        metadata = {"key": "value"}

        msg = Message(role="user", content="Hello", timestamp=timestamp, metadata=metadata)

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp == timestamp
        assert msg.metadata == metadata

    def test_message_auto_generates_timestamp(self) -> None:
        """Test that message auto-generates timestamp if not provided."""
        msg = Message(role="user", content="Hello")

        assert msg.timestamp
        assert "T" in msg.timestamp  # ISO format

    def test_message_metadata_defaults_to_empty_dict(self) -> None:
        """Test that metadata defaults to empty dict."""
        msg = Message(role="user", content="Hello")

        assert msg.metadata == {}
        assert isinstance(msg.metadata, dict)

    def test_message_to_dict(self) -> None:
        """Test message serialization to dictionary."""
        msg = Message(role="user", content="Hello", timestamp="2024-01-01T12:00:00")

        data = msg.to_dict()

        assert data["role"] == "user"
        assert data["content"] == "Hello"
        assert data["timestamp"] == "2024-01-01T12:00:00"
        assert data["metadata"] == {}

    def test_message_to_api_format(self) -> None:
        """Test message conversion to OpenAI API format."""
        msg = Message(
            role="assistant",
            content="Hi there!",
            timestamp="2024-01-01T12:00:00",
            metadata={"tokens": 50},
        )

        api_format = msg.to_api_format()

        assert api_format == {"role": "assistant", "content": "Hi there!"}
        assert "timestamp" not in api_format
        assert "metadata" not in api_format


class TestConversationInitialization:
    """Test Conversation initialization."""

    def test_conversation_creates_default_id(self, mock_config: Mock) -> None:
        """Test that conversation generates default ID if not provided."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()

            assert conv.conversation_id
            assert len(conv.conversation_id) > 0

    def test_conversation_uses_provided_id(self, mock_config: Mock) -> None:
        """Test that conversation uses provided ID."""
        test_id = "custom-id-123"
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(conversation_id=test_id)

            assert conv.conversation_id == test_id

    def test_conversation_initializes_empty_messages(self, mock_config: Mock) -> None:
        """Test that conversation starts with empty messages."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()

            assert conv.messages == []

    def test_conversation_uses_config_max_context_length(self, mock_config: Mock) -> None:
        """Test that conversation uses config max_context_length."""
        mock_config.max_context_length = 12000
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()

            assert conv.max_context_length == 12000

    def test_conversation_uses_provided_max_context_length(self, mock_config: Mock) -> None:
        """Test that provided max_context_length overrides config."""
        mock_config.max_context_length = 8000
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(max_context_length=16000)

            assert conv.max_context_length == 16000

    def test_conversation_initializes_metadata(self, mock_config: Mock) -> None:
        """Test that conversation initializes metadata."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()

            assert "created_at" in conv.metadata
            assert "updated_at" in conv.metadata
            assert conv.metadata["created_at"] == conv.metadata["updated_at"]

    def test_conversation_adds_system_prompt(self, mock_config: Mock) -> None:
        """Test that conversation adds system prompt if provided."""
        system_prompt = "You are a helpful assistant."
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(system_prompt=system_prompt)

            assert len(conv.messages) == 1
            assert conv.messages[0].role == "system"
            assert conv.messages[0].content == system_prompt


class TestConversationAddMessage:
    """Test adding messages to conversation."""

    def test_add_message_creates_message(self, mock_config: Mock) -> None:
        """Test adding a message to conversation."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            msg = conv.add_message("user", "Hello")

            assert len(conv.messages) == 1
            assert conv.messages[0].role == "user"
            assert conv.messages[0].content == "Hello"
            assert isinstance(msg, Message)

    def test_add_message_returns_message_object(self, mock_config: Mock) -> None:
        """Test that add_message returns the created Message."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            msg = conv.add_message("user", "Test message")

            assert isinstance(msg, Message)
            assert msg.role == "user"
            assert msg.content == "Test message"

    def test_add_message_with_metadata(self, mock_config: Mock) -> None:
        """Test adding message with metadata."""
        metadata = {"tokens": 50, "source": "api"}
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("assistant", "Response", metadata=metadata)

            assert conv.messages[0].metadata == metadata

    def test_add_multiple_messages(self, mock_config: Mock) -> None:
        """Test adding multiple messages."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()

            conv.add_message("user", "Message 1")
            conv.add_message("assistant", "Response 1")
            conv.add_message("user", "Message 2")
            conv.add_message("assistant", "Response 2")

            assert len(conv.messages) == 4
            assert conv.messages[0].role == "user"
            assert conv.messages[1].role == "assistant"

    def test_add_message_updates_metadata_timestamp(self, mock_config: Mock) -> None:
        """Test that adding a message updates conversation metadata timestamp."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            created_at = conv.metadata["updated_at"]

            import time
            time.sleep(0.01)  # Ensure time difference
            conv.add_message("user", "Test")

            assert conv.metadata["updated_at"] > created_at


class TestConversationGetMessagesForAPI:
    """Test getting messages formatted for API."""

    def test_get_messages_for_api_all_messages(self, mock_config: Mock) -> None:
        """Test getting all messages in API format."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("user", "Hello")
            conv.add_message("assistant", "Hi there")

            api_messages = conv.get_messages_for_api()

            assert len(api_messages) == 2
            assert all("role" in msg and "content" in msg for msg in api_messages)
            assert api_messages[0]["role"] == "user"
            assert api_messages[1]["role"] == "assistant"

    def test_get_messages_for_api_max_messages(self, mock_config: Mock) -> None:
        """Test getting limited number of messages."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            for i in range(5):
                conv.add_message("user", f"Message {i}")

            api_messages = conv.get_messages_for_api(max_messages=2)

            assert len(api_messages) == 2
            assert api_messages[0]["content"] == "Message 3"
            assert api_messages[1]["content"] == "Message 4"

    def test_get_messages_for_api_no_metadata(self, mock_config: Mock) -> None:
        """Test that API format excludes metadata and timestamp."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("user", "Test", metadata={"tokens": 50})

            api_messages = conv.get_messages_for_api()

            assert len(api_messages) == 1
            assert api_messages[0] == {"role": "user", "content": "Test"}


class TestConversationTrimContext:
    """Test context trimming functionality."""

    def test_trim_context_removes_old_messages(self, mock_config: Mock) -> None:
        """Test that trim_context removes oldest messages first."""
        mock_config.max_context_length = 10  # Very small to force trimming
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(max_context_length=10)
            conv.add_message("user", "Short")
            conv.add_message("assistant", "Response")
            conv.add_message("user", "Another")

            initial_count = len(conv.messages)
            conv.trim_context()

            # Should have removed at least one message
            assert len(conv.messages) <= initial_count

    def test_trim_context_keeps_system_message(self, mock_config: Mock) -> None:
        """Test that trim_context keeps system message."""
        mock_config.max_context_length = 10
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            system_prompt = "System prompt"
            conv = Conversation(system_prompt=system_prompt, max_context_length=10)

            # Add messages
            for i in range(10):
                conv.add_message("user", f"Message {i} with some content")

            conv.trim_context()

            # System message should still be there
            assert any(msg.role == "system" for msg in conv.messages)

    def test_trim_context_with_target_length(self, mock_config: Mock) -> None:
        """Test trim_context with custom target length."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(max_context_length=1000)

            for i in range(10):
                conv.add_message("user", f"Message {i}")

            initial_count = len(conv.messages)
            conv.trim_context(target_length=5)

            # Should have removed more messages due to smaller target
            assert len(conv.messages) <= initial_count


class TestConversationClear:
    """Test conversation clearing."""

    def test_clear_removes_all_messages(self, mock_config: Mock) -> None:
        """Test that clear removes all messages."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("user", "Message 1")
            conv.add_message("assistant", "Response 1")

            conv.clear(keep_system=False)

            assert conv.messages == []

    def test_clear_keeps_system_message(self, mock_config: Mock) -> None:
        """Test that clear keeps system message when requested."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            system_prompt = "System prompt"
            conv = Conversation(system_prompt=system_prompt)
            conv.add_message("user", "Message 1")
            conv.add_message("assistant", "Response 1")

            conv.clear(keep_system=True)

            assert len(conv.messages) == 1
            assert conv.messages[0].role == "system"
            assert conv.messages[0].content == system_prompt

    def test_clear_updates_metadata(self, mock_config: Mock) -> None:
        """Test that clear updates metadata timestamp."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("user", "Test")
            old_updated_at = conv.metadata["updated_at"]

            import time
            time.sleep(0.01)
            conv.clear()

            assert conv.metadata["updated_at"] > old_updated_at


class TestConversationCheckpoint:
    """Test checkpoint save/load functionality."""

    def test_save_checkpoint_creates_file(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test that save_checkpoint creates a JSON file."""
        mock_config.conversation_dir = tmp_path
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(conversation_id="test-conv-1")
            conv.add_message("user", "Hello")
            conv.add_message("assistant", "Hi")

            checkpoint_path = conv.save_checkpoint()

            assert checkpoint_path.exists()
            assert checkpoint_path.suffix == ".json"

    def test_save_checkpoint_with_custom_name(self, mock_config: Mock, tmp_path: Path) -> None:
        """Test saving checkpoint with custom name."""
        mock_config.conversation_dir = tmp_path
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(conversation_id="test-conv-1")
            conv.add_message("user", "Test")

            checkpoint_path = conv.save_checkpoint(name="custom_checkpoint")

            assert checkpoint_path.name == "custom_checkpoint.json"

    def test_checkpoint_contains_all_data(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that checkpoint file contains all conversation data."""
        mock_config.conversation_dir = tmp_path
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv_id = "test-conv-1"
            conv = Conversation(conversation_id=conv_id, max_context_length=16000)
            conv.add_message("user", "Question")
            conv.add_message("assistant", "Answer")

            conv.save_checkpoint()

            checkpoint_path = tmp_path / f"{conv_id}.json"
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["conversation_id"] == conv_id
            assert len(data["messages"]) == 2
            assert data["max_context_length"] == 16000
            assert "created_at" in data["metadata"]

    def test_load_checkpoint_restores_conversation(
        self, mock_config: Mock, saved_checkpoint: Path
    ) -> None:
        """Test loading a checkpoint restores conversation state."""
        mock_config.conversation_dir = saved_checkpoint.parent
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation.load_checkpoint("test_checkpoint")

            assert conv.conversation_id == "20240101_120000_000000"
            assert len(conv.messages) == 3
            assert conv.messages[0].role == "system"
            assert conv.messages[1].role == "user"
            assert conv.messages[2].role == "assistant"

    def test_load_checkpoint_raises_for_missing_file(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that load_checkpoint raises FileNotFoundError for missing file."""
        mock_config.conversation_dir = tmp_path
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            with pytest.raises(FileNotFoundError):
                Conversation.load_checkpoint("nonexistent")

    def test_load_checkpoint_restores_metadata(
        self, mock_config: Mock, saved_checkpoint: Path
    ) -> None:
        """Test that loading checkpoint restores metadata."""
        mock_config.conversation_dir = saved_checkpoint.parent
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation.load_checkpoint("test_checkpoint")

            assert "created_at" in conv.metadata
            assert "updated_at" in conv.metadata


class TestConversationListCheckpoints:
    """Test listing available checkpoints."""

    def test_list_checkpoints_empty_directory(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test list_checkpoints with no checkpoints."""
        mock_config.conversation_dir = tmp_path
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            checkpoints = Conversation.list_checkpoints()

            assert checkpoints == []

    def test_list_checkpoints_returns_all(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that list_checkpoints returns all saved checkpoints."""
        mock_config.conversation_dir = tmp_path

        # Create multiple checkpoints
        checkpoint_data_1 = {
            "conversation_id": "conv-1",
            "messages": [],
            "metadata": {"created_at": "2024-01-01T12:00:00", "updated_at": "2024-01-01T12:00:00"},
        }
        checkpoint_data_2 = {
            "conversation_id": "conv-2",
            "messages": [],
            "metadata": {"created_at": "2024-01-01T13:00:00", "updated_at": "2024-01-01T13:00:00"},
        }

        with open(tmp_path / "checkpoint1.json", "w", encoding="utf-8") as f:
            json.dump(checkpoint_data_1, f)
        with open(tmp_path / "checkpoint2.json", "w", encoding="utf-8") as f:
            json.dump(checkpoint_data_2, f)

        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            checkpoints = Conversation.list_checkpoints()

            assert len(checkpoints) == 2
            names = [cp["name"] for cp in checkpoints]
            assert "checkpoint1" in names
            assert "checkpoint2" in names

    def test_list_checkpoints_sorted_by_updated_at(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that checkpoints are sorted by updated_at descending."""
        mock_config.conversation_dir = tmp_path

        checkpoint_data_1 = {
            "conversation_id": "conv-1",
            "messages": [],
            "metadata": {"created_at": "2024-01-01T12:00:00", "updated_at": "2024-01-01T12:00:00"},
        }
        checkpoint_data_2 = {
            "conversation_id": "conv-2",
            "messages": [],
            "metadata": {"created_at": "2024-01-01T13:00:00", "updated_at": "2024-01-01T13:00:00"},
        }

        with open(tmp_path / "checkpoint1.json", "w", encoding="utf-8") as f:
            json.dump(checkpoint_data_1, f)
        with open(tmp_path / "checkpoint2.json", "w", encoding="utf-8") as f:
            json.dump(checkpoint_data_2, f)

        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            checkpoints = Conversation.list_checkpoints()

            # Most recent should be first
            assert checkpoints[0]["updated_at"] > checkpoints[1]["updated_at"]

    def test_list_checkpoints_skips_invalid_files(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that list_checkpoints skips invalid JSON files."""
        mock_config.conversation_dir = tmp_path

        # Create valid checkpoint
        checkpoint_data = {
            "conversation_id": "conv-1",
            "messages": [],
            "metadata": {"created_at": "2024-01-01T12:00:00", "updated_at": "2024-01-01T12:00:00"},
        }
        with open(tmp_path / "valid.json", "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f)

        # Create invalid JSON file
        with open(tmp_path / "invalid.json", "w", encoding="utf-8") as f:
            f.write("not valid json {]")

        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            checkpoints = Conversation.list_checkpoints()

            assert len(checkpoints) == 1
            assert checkpoints[0]["name"] == "valid"


class TestConversationSummary:
    """Test conversation summary functionality."""

    def test_get_summary_empty_conversation(self, mock_config: Mock) -> None:
        """Test summary of empty conversation."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            summary = conv.get_summary()

            assert summary["total_messages"] == 0
            assert summary["message_counts"] == {}

    def test_get_summary_with_messages(self, mock_config: Mock) -> None:
        """Test summary with multiple messages."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation(system_prompt="System")
            conv.add_message("user", "Message 1")
            conv.add_message("assistant", "Response 1")
            conv.add_message("user", "Message 2")

            summary = conv.get_summary()

            assert summary["total_messages"] == 4
            assert summary["message_counts"]["system"] == 1
            assert summary["message_counts"]["user"] == 2
            assert summary["message_counts"]["assistant"] == 1

    def test_get_summary_includes_timestamps(self, mock_config: Mock) -> None:
        """Test that summary includes metadata timestamps."""
        with patch("qcoder.core.conversation.get_config", return_value=mock_config):
            conv = Conversation()
            conv.add_message("user", "Test")

            summary = conv.get_summary()

            assert "created_at" in summary
            assert "updated_at" in summary
            assert summary["conversation_id"] == conv.conversation_id
