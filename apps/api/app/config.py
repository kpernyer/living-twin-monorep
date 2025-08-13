"""Configuration settings for the Living Twin API."""

import os
from typing import Optional
from pydantic import BaseSettings


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
