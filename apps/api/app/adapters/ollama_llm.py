from typing import Any, Dict, List

import requests

from ..ports.llm import IChatLLM


class OllamaChat(IChatLLM):
    def __init__(self, base: str = "http://localhost:11434", model: str = "llama3"):
        self.base, self.model = base, model

    def answer(self, hits: List[Dict[str, Any]], question: str, rag_only: bool = False) -> str:
        ctx = [f"[{i + 1}] {h['text']} (src: {h.get('source', '')})" for i, h in enumerate(hits)]
        if rag_only:
            return "RAG_ONLY mode (ollama):\n" + "\n".join(ctx[:3])
        prompt = "Context:\n" + "\n".join(ctx) + f"\n\nQuestion: {question}\nAnswer:"
        r = requests.post(
            f"{self.base}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "")
