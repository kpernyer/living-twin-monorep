from .config import AppCfg
from .adapters.firebase_auth import FirebaseAuth, SimpleAuthorizer
from .adapters.neo4j_store import Neo4jStore
from .adapters.neo4j_conversation_store import Neo4jConversationStore
from .adapters.openai_llm import OpenAIChat, OpenAIEmbedder
from .adapters.sbert_embedder import LocalEmbedder
from .adapters.ollama_llm import OllamaChat
from .domain.services import RagService, DocumentService, TenantService
from .domain.conversational_service import ConversationalRagService

class Container:
    def __init__(self, cfg: AppCfg):
        self.cfg = cfg
        
        # Infrastructure adapters
        self.auth = FirebaseAuth(bypass=cfg.bypass_auth)
        self.authorizer = SimpleAuthorizer()
        self.store = Neo4jStore(cfg.neo4j)
        self.conversation_store = Neo4jConversationStore(cfg.neo4j)
        self.embedder = LocalEmbedder(cfg.local.model) if cfg.local_embeddings else OpenAIEmbedder(cfg.openai.embedding_model)
        
        # LLM selection
        if cfg.llm_provider == "openai":
            self.llm = OpenAIChat(cfg.openai.chat_model)
        elif cfg.llm_provider == "ollama":
            self.llm = OllamaChat(cfg.ollama_base, cfg.ollama_model)
        else:
            self.llm = OpenAIChat(cfg.openai.chat_model)
        
        # Domain services (pure business logic)
        self.rag = RagService(self.store, self.llm, self.embedder, rag_only=cfg.rag_only or cfg.llm_provider=="stub")
        self.conversational_rag = ConversationalRagService(
            self.store, 
            self.llm, 
            self.embedder, 
            self.conversation_store,
            rag_only=cfg.rag_only or cfg.llm_provider=="stub"
        )
        self.document_service = DocumentService(self.store)
        self.tenant_service = TenantService()

container: Container | None = None

def init_container(cfg: AppCfg) -> Container:
    global container
    container = Container(cfg)
    return container
