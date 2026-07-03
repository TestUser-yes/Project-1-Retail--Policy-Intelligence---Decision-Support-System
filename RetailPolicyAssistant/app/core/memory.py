"""Conversation Memory Management

Maintains multi-turn conversation state and context for coherent dialogue.
Supports in-memory storage for demo, extensible to database backing.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class Message:
    """Single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)  # Additional context (intent, risk_level, etc.)

    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationMemory:
    """Manages conversation history and context."""

    def __init__(self, conversation_id: str, user_id: str = None, max_messages: int = 100):
        """Initialize conversation memory.

        Args:
            conversation_id: Unique ID for this conversation
            user_id: ID of the user (optional)
            max_messages: Maximum messages to keep in memory
        """
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.max_messages = max_messages
        self.messages: List[Message] = []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def add_message(self, role: str, content: str, metadata: Dict = None) -> Message:
        """Add a message to conversation history.

        Args:
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata (intent, cost, risk_level, etc.)

        Returns:
            The added Message object
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)

        # Trim if exceeded max messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        return message

    def get_context(self, include_system: bool = True) -> str:
        """Get conversation context for prompt injection.

        Args:
            include_system: Include system context summary

        Returns:
            Formatted context string for inclusion in prompts
        """
        if not self.messages:
            return ""

        context_lines = []

        if include_system:
            context_lines.append(f"[Conversation ID: {self.conversation_id}]")
            context_lines.append(f"[Messages in conversation: {len(self.messages)}]")
            context_lines.append("")

        # Include last 10 messages for context window
        for message in self.messages[-10:]:
            role = message.role.upper()
            context_lines.append(f"{role}: {message.content[:200]}")

        return "\n".join(context_lines)

    def get_last_messages(self, n: int = 5) -> List[Message]:
        """Get last N messages.

        Args:
            n: Number of messages to retrieve

        Returns:
            List of last N messages
        """
        return self.messages[-n:] if self.messages else []

    def get_all_messages(self) -> List[Message]:
        """Get all messages in conversation.

        Returns:
            List of all messages
        """
        return self.messages.copy()

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self.updated_at = datetime.now(timezone.utc)

    def summarize(self, max_length: int = 500) -> str:
        """Summarize conversation (for token efficiency).

        Args:
            max_length: Maximum length of summary

        Returns:
            Summary of conversation
        """
        if not self.messages:
            return ""

        summary_parts = []

        # Extract key information from messages
        user_queries = [m.content for m in self.messages if m.role == "user"]
        assistant_responses = [m.content for m in self.messages if m.role == "assistant"]

        summary_parts.append(f"Topics discussed: {len(user_queries)} queries")

        # First and last topics
        if user_queries:
            summary_parts.append(f"Started with: {user_queries[0][:50]}...")
            if len(user_queries) > 1:
                summary_parts.append(f"Latest topic: {user_queries[-1][:50]}...")

        # Key entities if any
        if self.messages and self.messages[-1].metadata:
            metadata = self.messages[-1].metadata
            if "cost" in metadata:
                summary_parts.append(f"Total cost tracked: ${metadata.get('total_cost', 0):.2f}")
            if "risk_level" in metadata:
                summary_parts.append(f"Latest risk level: {metadata['risk_level']}")

        summary = " | ".join(summary_parts)
        return summary[:max_length]

    def get_stats(self) -> Dict:
        """Get conversation statistics.

        Returns:
            Dict with conversation stats
        """
        user_messages = [m for m in self.messages if m.role == "user"]
        assistant_messages = [m for m in self.messages if m.role == "assistant"]

        total_tokens = sum(len(m.content.split()) for m in self.messages)

        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_tokens": total_tokens,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "duration_seconds": (self.updated_at - self.created_at).total_seconds(),
        }

    def to_dict(self) -> Dict:
        """Convert entire conversation to dictionary.

        Returns:
            Dict representation of conversation
        """
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages],
            "stats": self.get_stats(),
        }


# Global conversation store (in-memory, can be extended to DB)
_conversations: Dict[str, ConversationMemory] = {}


def get_or_create_conversation(conversation_id: str, user_id: str = None) -> ConversationMemory:
    """Get existing conversation or create new one.

    Args:
        conversation_id: Unique ID for conversation
        user_id: User ID (for new conversations)

    Returns:
        ConversationMemory instance
    """
    if conversation_id not in _conversations:
        _conversations[conversation_id] = ConversationMemory(
            conversation_id=conversation_id,
            user_id=user_id
        )
    return _conversations[conversation_id]


def get_conversation(conversation_id: str) -> Optional[ConversationMemory]:
    """Get conversation by ID.

    Args:
        conversation_id: Unique ID for conversation

    Returns:
        ConversationMemory or None if not found
    """
    return _conversations.get(conversation_id)


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation.

    Args:
        conversation_id: Unique ID for conversation

    Returns:
        True if deleted, False if not found
    """
    if conversation_id in _conversations:
        del _conversations[conversation_id]
        return True
    return False


def list_conversations() -> List[str]:
    """List all conversation IDs.

    Returns:
        List of conversation IDs
    """
    return list(_conversations.keys())
