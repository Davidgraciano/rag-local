"""Cliente mínimo de Ollama para embeddings y chat en streaming."""
from __future__ import annotations

import json
from collections.abc import Iterator

import httpx


class Ollama:
    def __init__(self, url: str, modelo_embeddings: str, modelo_chat: str, timeout: float = 120):
        self.http = httpx.Client(base_url=url, timeout=timeout)
        self.modelo_embeddings = modelo_embeddings
        self.modelo_chat = modelo_chat

    def embeddings(self, textos: list[str]) -> list[list[float]]:
        r = self.http.post("/api/embed", json={"model": self.modelo_embeddings, "input": textos})
        r.raise_for_status()
        return r.json()["embeddings"]

    def chat(self, mensajes: list[dict[str, str]]) -> Iterator[str]:
        with self.http.stream("POST", "/api/chat", json={"model": self.modelo_chat, "messages": mensajes, "stream": True}) as r:
            r.raise_for_status()
            for linea in r.iter_lines():
                if not linea:
                    continue
                parte = json.loads(linea)
                if contenido := parte.get("message", {}).get("content"):
                    yield contenido
                if parte.get("done"):
                    break
