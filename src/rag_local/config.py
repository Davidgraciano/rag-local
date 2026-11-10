import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    es_url: str = os.environ.get("ES_URL", "http://localhost:9200")
    ollama_url: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    modelo_embeddings: str = os.environ.get("MODELO_EMBEDDINGS", "nomic-embed-text")
    modelo_chat: str = os.environ.get("MODELO_CHAT", "qwen2.5:7b")
    indice: str = os.environ.get("INDICE", "documentos")
    tam_fragmento: int = int(os.environ.get("TAM_FRAGMENTO", "800"))
    solapamiento: int = int(os.environ.get("SOLAPAMIENTO", "120"))
    top_k: int = int(os.environ.get("TOP_K", "4"))
