"""Stub LLM adapter for testing."""

from typing import List, Dict, Any, Optional


class StubChat:
    """Stub chat LLM for testing."""
    
    def __init__(self, model: str = "stub"):
        self.model = model
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Return a stub response based on the last user message."""
        if not messages:
            return "Hello! I'm a stub LLM for testing."
        
        # Get the last user message
        last_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        if not last_message:
            return "I'm here to help with your questions."
        
        # Return predictable responses based on content
        if "living twin" in last_message.lower():
            return "Living Twin is an organizational AI system that helps companies understand their data and align their strategies."
        elif "rag" in last_message.lower():
            return "RAG (Retrieval Augmented Generation) is a technique that combines document retrieval with language model generation to provide more accurate and contextual responses."
        elif "purpose" in last_message.lower():
            return "The main purpose is to help organizations better understand and utilize their internal knowledge and data."
        else:
            return f"This is a stub response to: {last_message[:50]}..."
    
    def answer(self, hits: List[Dict[str, Any]], query: str, rag_only: bool = False) -> str:
        """Return a stub answer based on the query and retrieved hits."""
        if not hits:
            return f"I couldn't find any relevant information for: {query}"
        
        # Return a predictable response based on the query
        if "living twin" in query.lower():
            return "Based on the retrieved documents, Living Twin is an organizational AI system that helps companies understand their data and align their strategies. It uses RAG (Retrieval Augmented Generation) to provide intelligent answers based on company documents and knowledge bases."
        elif "rag" in query.lower():
            return "RAG (Retrieval Augmented Generation) is a technique that combines document retrieval with language model generation to provide more accurate and contextual responses."
        else:
            return f"Based on the retrieved documents, here's what I found about '{query}': This is a stub response that would normally be generated from the actual retrieved content."


class StubEmbedder:
    """Stub embedder for testing."""
    
    def __init__(self, model: str = "stub"):
        self.model = model
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return stub embeddings (all zeros for simplicity)."""
        # Return embeddings with 384 dimensions (common for sentence transformers)
        return [[0.0] * 384 for _ in texts]
    
    def embed_single(self, text: str) -> List[float]:
        """Return a single stub embedding."""
        return [0.0] * 384
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return stub embeddings for a batch of texts."""
        # Alias for embed method to match interface
        return self.embed(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Return a stub embedding for a query."""
        # Alias for embed_single method to match interface
        return self.embed_single(query)
