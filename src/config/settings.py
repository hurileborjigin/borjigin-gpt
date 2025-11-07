# src/config/settings.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure OpenAI Settings
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    
    # Tavily Settings
    tavily_api_key: str
    
    # LangChain Settings (Optional - for tracing/debugging)
    langchain_tracing_v2: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    
    # Agent Settings
    temperature: float = 0.7
    max_iterations: int = 3
    critique_threshold: float = 7.0
    follow_up_depth: int = 3
    
    # Memory Settings
    chroma_persist_directory: str = "data/chroma_db"
    long_term_collection_name: str = "long_term_memory"
    short_term_collection_name: str = "short_term_memory"
    company_research_collection_name: str = "research_cache"
    
    # Data Directories
    cv_dir: Path = Path("data/cv")
    experiences_dir: Path = Path("data/experiences")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # ← ADD THIS LINE to ignore extra env variables
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.cv_dir.mkdir(parents=True, exist_ok=True)
        self.experiences_dir.mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_directory).mkdir(parents=True, exist_ok=True)

settings = Settings()