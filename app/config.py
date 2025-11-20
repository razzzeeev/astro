import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # Cohere Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-r-08-2024")
    COHERE_TEMPERATURE: float = float(os.getenv("COHERE_TEMPERATURE", "0.7"))
    COHERE_MAX_TOKENS: int = int(os.getenv("COHERE_MAX_TOKENS", "200"))
    
    # Cohere Embedding Configuration
    COHERE_EMBEDDING_MODEL: str = os.getenv("COHERE_EMBEDDING_MODEL", "embed-english-v3.0")
    EMBEDDING_INPUT_TYPE: str = os.getenv("EMBEDDING_INPUT_TYPE", "search_document")
    
    # Vector Store Configuration
    VECTOR_STORE_ENABLED: bool = os.getenv("VECTOR_STORE_ENABLED", "true").lower() == "true"
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "3"))
    
    # Translation Configuration
    TRANSLATION_ENABLED: bool = os.getenv("TRANSLATION_ENABLED", "true").lower() == "true"
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()

