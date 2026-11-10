"""API HTTP: cargar documentos y hacer preguntas con respuesta en streaming."""
from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any, Protocol

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .config import Config
from .fragmentos import fragmentar
from .prompt import construir_mensajes, fuentes


class Modelo(Protocol):
    def embeddings(self, textos: list[str]) -> list[list[float]]: ...
    def chat(self, mensajes: list[dict[str, str]]) -> Iterator[str]: ...


class Documento(BaseModel):
    fuente: str = Field(min_length=1, max_length=200)
    texto: str = Field(min_length=1)


class Pregunta(BaseModel):
    pregunta: str = Field(min_length=3)
    k: int | None = Field(default=None, ge=1, le=20)
    stream: bool = True


def crear_app(almacen: Any, modelo: Modelo, config: Config = Config()) -> FastAPI:
    app = FastAPI(title="RAG local", version="0.1.0")

    @app.get("/salud")
    def salud() -> dict[str, str]:
        return {"estado": "ok"}

    @app.post("/documentos")
    def cargar(doc: Documento) -> dict[str, Any]:
        partes = fragmentar(doc.texto, doc.fuente, config.tam_fragmento, config.solapamiento)
        vectores = modelo.embeddings([p.texto for p in partes])
        guardados = almacen.guardar(partes, vectores)
        return {"fuente": doc.fuente, "fragmentos": guardados}

    @app.post("/preguntar")
    def preguntar(p: Pregunta):
        vector = modelo.embeddings([p.pregunta])[0]
        encontrados = almacen.buscar(vector, p.k or config.top_k)
        if not encontrados:
            raise HTTPException(404, "No hay documentos cargados todavía")
        mensajes = construir_mensajes(p.pregunta, encontrados)
        if not p.stream:
            return {"respuesta": "".join(modelo.chat(mensajes)), "fuentes": fuentes(encontrados)}

        def emitir() -> Iterator[str]:
            yield from modelo.chat(mensajes)
            yield "\n\n---\nFuentes: " + json.dumps(fuentes(encontrados), ensure_ascii=False)

        return StreamingResponse(emitir(), media_type="text/plain; charset=utf-8")

    return app


def app_por_defecto() -> FastAPI:
    from elasticsearch import Elasticsearch

    from .almacen import Almacen
    from .ollama import Ollama

    config = Config()
    return crear_app(Almacen(Elasticsearch(config.es_url), config.indice), Ollama(config.ollama_url, config.modelo_embeddings, config.modelo_chat), config)
