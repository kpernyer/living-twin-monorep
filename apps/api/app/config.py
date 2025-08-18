"""Configuration settings for the Living Twin API."""

import os
from typing import Optional, List
from dataclasses import dataclass
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Settings
    api_title: str = "Living Twin API"
    api_version: str = "1.0.0"
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Neo4j Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database: str = os.getenv("NEO4J_DB", "neo4j")
    vector_index_name: str = os.getenv("VECTOR_INDEX_NAME", "docEmbeddings")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Firebase Configuration
    firebase_project_id: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    firebase_credentials_path: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH")
    firestore_emulator_host: Optional[str] = os.getenv("FIRESTORE_EMULATOR_HOST")
    firebase_auth_emulator_host: Optional[str] = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")
    
    # Local Development
    use_local_mock: bool = os.getenv("USE_LOCAL_MOCK", "false").lower() == "true"
    local_data_dir: str = os.getenv("LOCAL_DATA_DIR", "./local_data")
    
    # Ollama Configuration (for local LLM)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Sentence Transformers (for local embeddings)
    sbert_model: str = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")
    
    # CORS Settings
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:5173"
    ]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def should_use_local_mock(self) -> bool:
        """Determine if local mock should be used."""
        return self.use_local_mock or (self.is_development and not self.firebase_project_id)
    
    @property
    def should_use_firebase_emulator(self) -> bool:
        """Determine if Firebase emulator should be used."""
        return bool(self.firestore_emulator_host or self.firebase_auth_emulator_host)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Structured application config expected by DI and main
@dataclass
class Neo4jCfg:
    uri: str
    user: str
    password: str
    database: str
    vector_index: str


@dataclass
class OpenAICfg:
    chat_model: str
    embedding_model: str
    embedding_dimensions: int


@dataclass
class LocalCfg:
    model: str
    embedding_dimensions: int


@dataclass
class AppCfg:
    # Feature flags and runtime toggles
    bypass_auth: bool
    allow_cors: bool
    cors_origins: List[str]
    rag_only: bool
    llm_provider: str  # "openai" | "ollama" | "stub"
    local_embeddings: bool
    use_local_mock: bool
    local_data_dir: str

    # Providers
    neo4j: Neo4jCfg
    openai: OpenAICfg
    local: LocalCfg
    ollama_base: str
    ollama_model: str
    embedding_dimensions: int
    async_ingest: bool


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def load_config() -> AppCfg:
    """Build the application configuration expected by DI and FastAPI app."""
    # Use Settings for base values
    s = settings

    neo4j = Neo4jCfg(
        uri=s.neo4j_uri,
        user=s.neo4j_user,
        password=s.neo4j_password,
        database=s.neo4j_database,
        vector_index=s.vector_index_name,
    )

    openai = OpenAICfg(
        chat_model=s.openai_model,
        embedding_model=s.openai_embedding_model,
        embedding_dimensions=int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536")),
    )

    local = LocalCfg(
        model=s.sbert_model,
        embedding_dimensions=int(os.getenv("SBERT_EMBEDDING_DIMENSIONS", "384")),
    )

    # Additional toggles from env
    bypass_auth = _env_bool("BYPASS_AUTH", default=s.is_development)
    allow_cors = _env_bool("ALLOW_CORS", default=True)
    rag_only = _env_bool("RAG_ONLY", default=False)
    local_embeddings = _env_bool("LOCAL_EMBEDDINGS", default=False)
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    async_ingest = _env_bool("ASYNC_INGEST", default=False)
    use_local_mock = _env_bool("USE_LOCAL_MOCK", default=s.use_local_mock)
    local_data_dir = s.local_data_dir

    # Decide active embedding dimensions based on embedder
    active_dims = local.embedding_dimensions if local_embeddings else openai.embedding_dimensions

    return AppCfg(
        bypass_auth=bypass_auth,
        allow_cors=allow_cors,
        cors_origins=list(s.cors_origins),
        rag_only=rag_only,
        llm_provider=llm_provider,
        local_embeddings=local_embeddings,
        use_local_mock=use_local_mock,
        local_data_dir=local_data_dir,
        neo4j=neo4j,
        openai=openai,
        local=local,
        ollama_base=s.ollama_base_url,
        ollama_model=s.ollama_model,
        embedding_dimensions=active_dims,
        async_ingest=async_ingest,
    )
