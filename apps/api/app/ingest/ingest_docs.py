import glob
import os
import uuid

from langchain_openai import OpenAIEmbeddings
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DB = os.getenv("NEO4J_DB", "neo4j")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY.")

emb = OpenAIEmbeddings(model="text-embedding-3-small")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def chunk_text(text: str, chunk_size=800, overlap=120):
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        i += chunk_size - overlap
    return chunks


def upsert_chunk(tx, text: str, source: str, vec):
    tx.run(
        """
        MERGE (d:Doc {id: $id})
        SET d.text=$text, d.source=$source, d.embedding=$vec
        """,
        id=str(uuid.uuid4()),
        text=text,
        source=source,
        vec=vec,
    )


def ingest_path(path_glob: str):
    files = glob.glob(path_glob, recursive=True)
    print(f"Ingesting {len(files)} files...")
    with driver.session(database=NEO4J_DB) as session:
        for fp in files:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            for ch in chunk_text(raw):
                vec = emb.embed_query(ch)
                session.execute_write(upsert_chunk, ch, fp, vec)
    print("Done.")


if __name__ == "__main__":
    ingest_path("corpus/**/*.txt")
