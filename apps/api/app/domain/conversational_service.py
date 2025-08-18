import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..ports.conversation_store import IConversationStore
from ..ports.llm import IChatLLM, IEmbedder
from ..ports.vector_store import IVectorStore
from .models import ConversationalQueryRequest, ConversationMessage, Document, QueryResponse


class ConversationalRagService:
    """RAG service with conversation memory capabilities."""

    def __init__(
        self,
        store: IVectorStore,
        llm: IChatLLM,
        embed: IEmbedder,
        conversation_store: IConversationStore,
        rag_only: bool = False,
    ):
        self.store = store
        self.llm = llm
        self.embed = embed
        self.conversation_store = conversation_store
        self.rag_only = rag_only

    def conversational_query(self, request: ConversationalQueryRequest) -> QueryResponse:
        """Execute a conversational RAG query with memory."""

        # Get or create conversation
        if request.conversation_id:
            conversation_history = self.conversation_store.get_conversation_history(
                request.conversation_id, limit=request.memory_window or 10
            )
        else:
            # Create new conversation
            title = self._generate_conversation_title(request.query)
            conversation_id = self.conversation_store.create_conversation(
                request.tenant_id, request.user_id, title
            )
            conversation_history = []
            request.conversation_id = conversation_id

        # Build contextual query considering conversation history
        contextual_query = self._build_contextual_query(request.query, conversation_history)

        # Generate query embedding (could be enhanced with conversation context)
        query_vector = self.embed.embed_query(contextual_query)

        # Search with tenant isolation
        hits = self.store.search(
            tenant_id=request.tenant_id, query_vector=query_vector, k=request.context_limit or 5
        )

        # Generate conversational answer
        answer = self._generate_conversational_answer(
            hits, request.query, conversation_history, rag_only=self.rag_only
        )

        # Save user message
        user_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            role="user",
            content=request.query,
            timestamp=datetime.utcnow(),
            metadata={},
        )
        self.conversation_store.add_message(request.conversation_id, user_message)

        # Save assistant response
        assistant_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow(),
            metadata={
                "sources": [hit.get("source", "") for hit in hits],
                "confidence": self._calculate_confidence(hits),
                "context_used": len(hits),
            },
        )
        self.conversation_store.add_message(request.conversation_id, assistant_message)

        # Convert hits to domain documents
        source_documents = [
            Document(
                id=hit.get("id", ""),
                title=hit.get("source", "Unknown"),
                content=hit.get("text", ""),
                source=hit.get("source", ""),
                metadata={"score": hit.get("score", 0.0)},
                tenant_id=request.tenant_id,
                created_at=datetime.utcnow(),
            )
            for hit in hits
        ]

        return QueryResponse(
            answer=answer,
            sources=source_documents,
            confidence=self._calculate_confidence(hits),
            query_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            conversation_id=request.conversation_id,
        )

    def _build_contextual_query(
        self, current_query: str, history: List[ConversationMessage]
    ) -> str:
        """Enhance current query with conversation context."""
        if not history:
            return current_query

        # Take last few exchanges for context
        recent_context = []
        for msg in history[-6:]:  # Last 3 exchanges (user + assistant)
            role_prefix = "User" if msg.role == "user" else "Assistant"
            recent_context.append(f"{role_prefix}: {msg.content}")

        if recent_context:
            context_str = "\n".join(recent_context)
            return f"Previous conversation:\n{context_str}\n\nCurrent question: {current_query}"

        return current_query

    def _generate_conversational_answer(
        self,
        hits: List[Dict[str, Any]],
        current_query: str,
        history: List[ConversationMessage],
        rag_only: bool = False,
    ) -> str:
        """Generate answer considering conversation context."""

        # Format retrieved context
        ctx = [f"[{i + 1}] {h['text']} (src: {h.get('source', '')})" for i, h in enumerate(hits)]

        if rag_only:
            return "RAG_ONLY mode: returning top snippets only.\n" + "\n".join(ctx[:3])

        # Build conversation-aware system prompt
        sys_prompt = (
            "You are the Organizational Twin, an AI assistant that helps users "
            "understand their organization through documents and data.\n\n"
            "Key behaviors:\n"
            "- Always cite sources using [1], [2], [3] format\n"
            "- Maintain conversation context and refer to previous exchanges when relevant\n"
            "- If the user asks follow-up questions, connect them to the previous discussion\n"
            "- Be conversational but professional\n"
            "- If you don't have enough information, say so clearly"
        )

        # Build conversation context for the LLM
        conversation_context = ""
        if history:
            recent_exchanges = []
            for msg in history[-4:]:  # Last 2 exchanges
                role = "Human" if msg.role == "user" else "Assistant"
                recent_exchanges.append(f"{role}: {msg.content}")

            if recent_exchanges:
                conversation_context = (
                    "\nRecent conversation:\n" + "\n".join(recent_exchanges) + "\n"
                )

        # Build user message with context and retrieved documents
        user_message = f"""{conversation_context}
Retrieved documents:
{chr(10).join(ctx)}

Current question: {current_query}

Please provide a helpful answer using the retrieved documents and conversation context."""

        # Use LangChain for response generation
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_message},
        ]

        response = self.llm.llm.invoke(messages)
        return response.content

    def _generate_conversation_title(self, first_query: str) -> str:
        """Generate a title for the conversation based on the first query."""
        # Simple approach - use first few words
        words = first_query.split()[:6]
        title = " ".join(words)
        if len(first_query.split()) > 6:
            title += "..."
        return title or "New Conversation"

    def _calculate_confidence(self, hits: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results."""
        if not hits:
            return 0.0

        # Simple confidence calculation based on top result score
        top_score = hits[0].get("score", 0.0)

        # Normalize score to 0-1 range (assuming scores are similarity scores)
        # This is a simple heuristic - you might want to adjust based on your vector store
        confidence = min(top_score, 1.0)

        return confidence
