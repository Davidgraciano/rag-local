"""Elasticsearch como almacén vectorial: un índice con dense_vector y búsqueda kNN."""
from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch, helpers

from .fragmentos import Fragmento


class Almacen:
    def __init__(self, es: Elasticsearch, indice: str):
        self.es = es
        self.indice = indice

    def asegurar_indice(self, dimensiones: int) -> None:
        if self.es.indices.exists(index=self.indice):
            return
        self.es.indices.create(index=self.indice, mappings={"properties": {
            "fuente": {"type": "keyword"},
            "posicion": {"type": "integer"},
            "texto": {"type": "text"},
            "vector": {"type": "dense_vector", "dims": dimensiones, "index": True, "similarity": "cosine"},
        }})

    def guardar(self, fragmentos: list[Fragmento], vectores: list[list[float]]) -> int:
        self.asegurar_indice(len(vectores[0]))
        acciones = ({"_index": self.indice, "_id": f"{f.fuente}#{f.posicion}", "fuente": f.fuente, "posicion": f.posicion, "texto": f.texto, "vector": v} for f, v in zip(fragmentos, vectores))
        ok, _ = helpers.bulk(self.es, acciones, refresh="wait_for")
        return ok

    def buscar(self, vector: list[float], k: int) -> list[dict[str, Any]]:
        r = self.es.search(index=self.indice, knn={"field": "vector", "query_vector": vector, "k": k, "num_candidates": max(50, k * 10)}, source=["fuente", "posicion", "texto"], size=k)
        return [{**h["_source"], "puntaje": h["_score"]} for h in r["hits"]["hits"]]
