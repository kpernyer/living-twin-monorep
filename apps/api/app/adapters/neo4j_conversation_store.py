import json
import uuid
from datetime import datetime
from typing import List, Optional
from neo4j import GraphDatabase
from ..ports.conversation_store import IConversationStore
from ..domain.models import Conversation, ConversationMessage


class Neo4jConversationStore(IConversationStore):
    """Neo4j implementation of conversation storage."""
    
    def __init__(self, cfg):
        self.driver = GraphDatabase.driver(cfg.uri, auth=(cfg.user, cfg.password))
        self.db = cfg.database

    def create_conversation(self, tenant_id: str, user_id: str, title: str) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        with self.driver.session(database=self.db) as session:
            session.run("""
                CREATE (c:Conversation {
                    id: $id,
                    tenantId: $tenantId,
                    userId: $userId,
                    title: $title,
                    createdAt: $now,
                    updatedAt: $now
                })
            """, 
            id=conversation_id, 
            tenantId=tenant_id, 
            userId=user_id, 
            title=title, 
            now=now
            )
        
        return conversation_id

    def get_conversation(self, conversation_id: str, tenant_id: str) -> Optional[Conversation]:
        """Get a conversation with all its messages."""
        with self.driver.session(database=self.db) as session:
            # Get conversation details
            conv_result = session.run("""
                MATCH (c:Conversation {id: $convId, tenantId: $tenantId})
                RETURN c
            """, convId=conversation_id, tenantId=tenant_id)
            
            conv_record = conv_result.single()
            if not conv_record:
                return None
            
            c = conv_record["c"]
            
            # Get all messages for this conversation
            msg_result = session.run("""
                MATCH (c:Conversation {id: $convId})-[:HAS_MESSAGE]->(m:Message)
                RETURN m
                ORDER BY m.timestamp ASC
            """, convId=conversation_id)
            
            messages = []
            for record in msg_result:
                m = record["m"]
                messages.append(ConversationMessage(
                    id=m["id"],
                    conversation_id=conversation_id,
                    role=m["role"],
                    content=m["content"],
                    timestamp=datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")),
                    metadata=json.loads(m.get("metadata", "{}"))
                ))
            
            return Conversation(
                id=c["id"],
                tenant_id=c["tenantId"],
                user_id=c["userId"],
                title=c["title"],
                created_at=datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(c["updatedAt"].replace("Z", "+00:00")),
                messages=messages
            )

    def list_conversations(self, tenant_id: str, user_id: str, limit: int = 20) -> List[Conversation]:
        """List conversations for a user, ordered by most recent."""
        with self.driver.session(database=self.db) as session:
            result = session.run("""
                MATCH (c:Conversation {tenantId: $tenantId, userId: $userId})
                OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:Message)
                WITH c, count(m) as messageCount
                RETURN c, messageCount
                ORDER BY c.updatedAt DESC
                LIMIT $limit
            """, tenantId=tenant_id, userId=user_id, limit=limit)
            
            conversations = []
            for record in result:
                c = record["c"]
                conversations.append(Conversation(
                    id=c["id"],
                    tenant_id=c["tenantId"],
                    user_id=c["userId"],
                    title=c["title"],
                    created_at=datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(c["updatedAt"].replace("Z", "+00:00")),
                    messages=[],  # Don't load messages for list view
                    metadata={"message_count": record["messageCount"]}
                ))
            
            return conversations

    def add_message(self, conversation_id: str, message: ConversationMessage) -> None:
        """Add a message to an existing conversation."""
        with self.driver.session(database=self.db) as session:
            session.run("""
                MATCH (c:Conversation {id: $convId})
                CREATE (m:Message {
                    id: $msgId,
                    role: $role,
                    content: $content,
                    timestamp: $timestamp,
                    metadata: $metadata
                })
                CREATE (c)-[:HAS_MESSAGE]->(m)
                SET c.updatedAt = $timestamp
            """, 
            convId=conversation_id,
            msgId=message.id,
            role=message.role,
            content=message.content,
            timestamp=message.timestamp.isoformat() + "Z",
            metadata=json.dumps(message.metadata)
            )

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[ConversationMessage]:
        """Get conversation messages ordered by timestamp."""
        with self.driver.session(database=self.db) as session:
            result = session.run("""
                MATCH (c:Conversation {id: $convId})-[:HAS_MESSAGE]->(m:Message)
                RETURN m
                ORDER BY m.timestamp ASC
                LIMIT $limit
            """, convId=conversation_id, limit=limit)
            
            messages = []
            for record in result:
                m = record["m"]
                messages.append(ConversationMessage(
                    id=m["id"],
                    conversation_id=conversation_id,
                    role=m["role"],
                    content=m["content"],
                    timestamp=datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")),
                    metadata=json.loads(m.get("metadata", "{}"))
                ))
            return messages

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        with self.driver.session(database=self.db) as session:
            session.run("""
                MATCH (c:Conversation {id: $convId})
                SET c.title = $title, c.updatedAt = $now
            """, 
            convId=conversation_id, 
            title=title, 
            now=datetime.utcnow().isoformat() + "Z"
            )

    def delete_conversation(self, conversation_id: str, tenant_id: str) -> bool:
        """Delete a conversation and all its messages."""
        with self.driver.session(database=self.db) as session:
            result = session.run("""
                MATCH (c:Conversation {id: $convId, tenantId: $tenantId})
                OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:Message)
                DETACH DELETE c, m
                RETURN count(c) as deleted
            """, convId=conversation_id, tenantId=tenant_id)
            
            record = result.single()
            return record["deleted"] > 0 if record else False
