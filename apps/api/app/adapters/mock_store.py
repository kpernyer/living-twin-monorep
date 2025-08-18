"""Mock store for RAG operations in tests."""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class MockStore:
    """Mock store for RAG operations in tests."""

    def __init__(self, data_dir: str = "./local_data"):
        self.data_dir = data_dir
        self.chunks_file = os.path.join(data_dir, "chunks.json")
        self.sources_file = os.path.join(data_dir, "sources.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize empty data if files don't exist
        self._init_empty_data()

    def _init_empty_data(self):
        """Initialize with empty data."""
        if not os.path.exists(self.chunks_file):
            with open(self.chunks_file, "w") as f:
                json.dump({}, f)

        if not os.path.exists(self.sources_file):
            with open(self.sources_file, "w") as f:
                json.dump({}, f)

    def _load_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from file."""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self, file_path: str, data: Dict[str, Any]):
        """Save data to file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def upsert_chunks(
        self, tenant_id: str, title: str, chunks: List[str], embeddings: List[List[float]]
    ) -> str:
        """Mock upsert chunks operation."""
        chunks_data = self._load_data(self.chunks_file)
        sources_data = self._load_data(self.sources_file)

        # Generate source ID
        source_id = str(uuid.uuid4())

        # Store chunks
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{source_id}_{i}"
            chunks_data[chunk_id] = {
                "id": chunk_id,
                "tenant_id": tenant_id,
                "source_id": source_id,
                "content": chunk,
                "metadata": {"title": title},
                "embedding": embedding,
                "created_at": datetime.now().isoformat(),
            }

        # Store source info
        sources_data[source_id] = {
            "id": source_id,
            "tenant_id": tenant_id,
            "title": title,
            "chunk_count": len(chunks),
            "created_at": datetime.now().isoformat(),
        }

        self._save_data(self.chunks_file, chunks_data)
        self._save_data(self.sources_file, sources_data)

        return source_id

    def search(self, tenant_id: str, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Mock similarity search."""
        chunks_data = self._load_data(self.chunks_file)

        # Filter by tenant
        tenant_chunks = [chunk for chunk in chunks_data.values() if chunk["tenant_id"] == tenant_id]

        # Simple mock: return first k chunks (no real similarity calculation)
        results = []
        for chunk in tenant_chunks[:k]:
            results.append(
                {
                    "id": chunk["id"],
                    "text": chunk["content"],
                    "source": chunk["metadata"].get("title", "Unknown"),
                    "score": 0.95,  # Mock similarity score
                }
            )

        return results

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get source by ID."""
        sources_data = self._load_data(self.sources_file)
        return sources_data.get(source_id)

    def ensure_vector_index(self, label: str, property_name: str, dimensions: int, similarity: str):
        """Mock vector index creation."""
        # No-op for mock store
        pass

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Mock get recent sources operation."""
        sources_data = self._load_data(self.sources_file)

        # Filter by tenant
        tenant_sources = [
            source for source in sources_data.values() if source["tenant_id"] == tenant_id
        ]

        # Sort by created_at and limit
        tenant_sources.sort(key=lambda x: x["created_at"], reverse=True)
        limited_sources = tenant_sources[:limit]

        # Convert to expected format
        result = []
        for source in limited_sources:
            result.append(
                {
                    "id": source["id"],
                    "title": source["title"],
                    "created_at": source["created_at"],
                    "chunk_count": source["chunk_count"],
                    "type": "document",
                }
            )

        return result


class MockConversationStore:
    """Mock conversation store for testing."""

    def __init__(self, data_dir: str = "./local_data"):
        self.data_dir = data_dir
        self.conversations_file = os.path.join(data_dir, "conversations.json")
        self.messages_file = os.path.join(data_dir, "messages.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize empty data if files don't exist
        self._init_empty_data()

    def _init_empty_data(self):
        """Initialize with empty data."""
        if not os.path.exists(self.conversations_file):
            self._save_data(self.conversations_file, {})
        if not os.path.exists(self.messages_file):
            self._save_data(self.messages_file, {})

    def _load_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_data(self, file_path: str, data: Dict[str, Any]):
        """Save data to JSON file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def create_conversation(self, tenant_id: str, user_id: str, title: str) -> str:
        """Mock create conversation operation."""
        conversations_data = self._load_data(self.conversations_file)

        # Generate conversation ID
        conversation_id = str(uuid.uuid4())

        # Store conversation
        conversations_data[conversation_id] = {
            "id": conversation_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self._save_data(self.conversations_file, conversations_data)

        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        conversations_data = self._load_data(self.conversations_file)
        return conversations_data.get(conversation_id)

    def add_message(self, conversation_id: str, message) -> None:
        """Mock add message operation."""
        messages_data = self._load_data(self.messages_file)
        conversations_data = self._load_data(self.conversations_file)

        # Store message
        messages_data[message.id] = {
            "id": message.id,
            "conversation_id": conversation_id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "metadata": message.metadata or {},
        }

        # Update conversation timestamp
        if conversation_id in conversations_data:
            conversations_data[conversation_id]["updated_at"] = datetime.now().isoformat()

        self._save_data(self.messages_file, messages_data)
        self._save_data(self.conversations_file, conversations_data)

    def get_messages(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get messages for a conversation."""
        messages_data = self._load_data(self.messages_file)

        conversation_messages = [
            msg for msg in messages_data.values() if msg["conversation_id"] == conversation_id
        ]

        # Sort by created_at and limit
        conversation_messages.sort(key=lambda x: x["created_at"])
        return conversation_messages[-limit:]

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List:
        """Mock get conversation history operation."""
        from ..domain.models import ConversationMessage

        messages_data = self._load_data(self.messages_file)

        # Filter messages by conversation_id
        conversation_messages = [
            msg for msg in messages_data.values() if msg["conversation_id"] == conversation_id
        ]

        # Sort by timestamp and limit
        conversation_messages.sort(key=lambda x: x["timestamp"])
        limited_messages = conversation_messages[:limit]

        # Convert to ConversationMessage objects
        result = []
        for msg in limited_messages:
            result.append(
                ConversationMessage(
                    id=msg["id"],
                    conversation_id=msg["conversation_id"],
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                    metadata=msg["metadata"],
                )
            )

        return result

    def list_conversations(self, tenant_id: str, user_id: str, limit: int = 20) -> List:
        """Mock list conversations operation."""
        from ..domain.models import Conversation

        conversations_data = self._load_data(self.conversations_file)
        messages_data = self._load_data(self.messages_file)

        # Filter by tenant and user
        user_conversations = [
            conv
            for conv in conversations_data.values()
            if conv["tenant_id"] == tenant_id and conv["user_id"] == user_id
        ]

        # Sort by updated_at and limit
        user_conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        limited_conversations = user_conversations[:limit]

        # Convert to Conversation objects
        result = []
        for conv in limited_conversations:
            # Count messages for this conversation
            message_count = sum(
                1 for msg in messages_data.values() if msg["conversation_id"] == conv["id"]
            )

            result.append(
                Conversation(
                    id=conv["id"],
                    tenant_id=conv["tenant_id"],
                    user_id=conv["user_id"],
                    title=conv["title"],
                    created_at=datetime.fromisoformat(conv["created_at"]),
                    updated_at=datetime.fromisoformat(conv["updated_at"]),
                    messages=[],  # Don't load messages for list view
                    metadata={"message_count": message_count},
                )
            )

        return result
