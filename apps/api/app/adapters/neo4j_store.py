from typing import List, Dict, Any
from neo4j import GraphDatabase
from ..ports.vector_store import IVectorStore

class Neo4jStore(IVectorStore):
    def __init__(self, cfg):
        self.driver = GraphDatabase.driver(cfg.uri, auth=(cfg.user, cfg.password))
        self.db = cfg.database
        self.index = cfg.vector_index

    def search(self, tenant_id: str, query_vector: list[float], k: int = 5) -> List[Dict[str, Any]]:
        q = (
            "CALL db.index.vector.queryNodes($index, $k, $vec) YIELD node, score "
            "WHERE coalesce(node.tenantId,'demo') = $tenant "
            "RETURN node as n, score"
        )
        with self.driver.session(database=self.db) as s:
            res = s.run(q, index=self.index, k=k, vec=query_vector, tenant=tenant_id)
            out = []
            for r in res:
                n = r["n"]
                out.append({"id": n.element_id, "text": n.get("text",""), "source": n.get("source",""), "score": r["score"]})
            return out

    def upsert_chunks(self, tenant_id: str, title: str, chunks: list[str], embeddings: list[list[float]]) -> str:
        import uuid, datetime
        sid = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat()+"Z"
        def _tx(tx):
            tx.run("MERGE (s:Source {id:$sid}) SET s.title=$title, s.tenantId=$tenantId, s.createdAt=$now",
                   sid=sid, title=title, tenantId=tenant_id, now=now)
            for i, ch in enumerate(chunks):
                tx.run(
                    """
                    MERGE (d:Doc {id:$id})
                    SET d.text=$text, d.source=$title, d.embedding=$emb, d.tenantId=$tenantId, d.createdAt=$now
                    WITH d MATCH (s:Source {id:$sid}) MERGE (s)-[:HAS_CHUNK]->(d)
                    """,
                    id=str(uuid.uuid4()), text=ch, emb=embeddings[i], tenantId=tenant_id, now=now, title=title, sid=sid
                )
        with self.driver.session(database=self.db) as s:
            s.execute_write(_tx)
        return sid

    def get_recent_sources(self, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently ingested sources for a tenant."""
        q = """
        MATCH (s:Source)
        WHERE coalesce(s.tenantId, 'demo') = $tenant
        OPTIONAL MATCH (s)-[:HAS_CHUNK]->(d:Doc)
        WITH s, count(d) as chunk_count
        RETURN s.id as id, s.title as title, s.createdAt as created_at, 
               chunk_count, 'document' as type
        ORDER BY s.createdAt DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.db) as session:
            result = session.run(q, tenant=tenant_id, limit=limit)
            sources = []
            for record in result:
                sources.append({
                    "id": record["id"],
                    "title": record["title"],
                    "created_at": record["created_at"],
                    "chunk_count": record["chunk_count"],
                    "type": record["type"]
                })
            return sources
