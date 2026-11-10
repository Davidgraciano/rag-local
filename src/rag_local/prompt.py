"""Construcción del prompt con fragmentos numerados para que el modelo cite sus fuentes."""
from __future__ import annotations

from typing import Any

SISTEMA = (
    "Eres un asistente que responde en español usando solo el contexto entregado. "
    "Cita las fuentes con su número entre corchetes, por ejemplo [1] o [2][3]. "
    "Si el contexto no tiene la respuesta, dilo claramente y no inventes."
)


def construir_mensajes(pregunta: str, encontrados: list[dict[str, Any]]) -> list[dict[str, str]]:
    bloques = [f"[{i}] ({d['fuente']})\n{d['texto']}" for i, d in enumerate(encontrados, start=1)]
    contexto = "\n\n".join(bloques) if bloques else "(sin contexto)"
    return [
        {"role": "system", "content": SISTEMA},
        {"role": "user", "content": f"Contexto:\n{contexto}\n\nPregunta: {pregunta}"},
    ]


def fuentes(encontrados: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"n": i, "fuente": d["fuente"], "posicion": d["posicion"], "puntaje": round(d.get("puntaje", 0.0), 4)} for i, d in enumerate(encontrados, start=1)]
