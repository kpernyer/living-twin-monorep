from typing import Any, Dict, List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..ports.llm import IChatLLM, IEmbedder


class OpenAIEmbedder(IEmbedder):
    def __init__(self, model: str):
        self.emb = OpenAIEmbeddings(model=model)

    def embed_query(self, text: str) -> list[float]:
        return self.emb.embed_query(text)

    def embed_batch(self, chunks: list[str]) -> list[list[float]]:
        return [self.emb.embed_query(c) for c in chunks]


class OpenAIChat(IChatLLM):
    def __init__(self, model: str):
        self.llm = ChatOpenAI(model=model)

    def answer(self, hits: List[Dict[str, Any]], question: str, rag_only: bool = False) -> str:
        ctx = [f"[{i + 1}] {h['text']} (src: {h.get('source', '')})" for i, h in enumerate(hits)]
        sys = "You are the Organizational Twin. Always cite snippets like [1], [2]."
        user = "Context:\n" + "\n".join(ctx) + f"\n\nQuestion: {question}\nAnswer:"
        if rag_only:
            return "RAG_ONLY mode: returning top snippets only.\n" + "\n".join(ctx[:3])
        r = self.llm.invoke([{"role": "system", "content": sys}, {"role": "user", "content": user}])
        return r.content
