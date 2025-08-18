from typing import List, Optional, Protocol

from ..domain.models import Conversation, ConversationMessage


class IConversationStore(Protocol):
    """Port for conversation storage operations."""

    def create_conversation(self, tenant_id: str, user_id: str, title: str) -> str:
        """Create a new conversation and return its ID."""
        ...

    def get_conversation(self, conversation_id: str, tenant_id: str) -> Optional[Conversation]:
        """Get a conversation with all its messages."""
        ...

    def list_conversations(
        self, tenant_id: str, user_id: str, limit: int = 20
    ) -> List[Conversation]:
        """List conversations for a user, ordered by most recent."""
        ...

    def add_message(self, conversation_id: str, message: ConversationMessage) -> None:
        """Add a message to an existing conversation."""
        ...

    def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> List[ConversationMessage]:
        """Get conversation messages ordered by timestamp."""
        ...

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        ...

    def delete_conversation(self, conversation_id: str, tenant_id: str) -> bool:
        """Delete a conversation and all its messages."""
        ...
