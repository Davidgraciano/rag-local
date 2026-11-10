"""Partición de documentos en fragmentos con solapamiento, respetando párrafos."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Fragmento:
    fuente: str
    posicion: int
    texto: str


def fragmentar(texto: str, fuente: str, tam: int = 800, solapamiento: int = 120) -> list[Fragmento]:
    """Agrupa párrafos hasta `tam` caracteres; un párrafo más largo se corta por oraciones.

    Cada fragmento empieza con el final del anterior (`solapamiento` caracteres) para que
    una idea partida en dos no se pierda en la búsqueda.
    """
    if solapamiento >= tam:
        raise ValueError("El solapamiento debe ser menor que el tamaño del fragmento")
    parrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    piezas: list[str] = []
    for p in parrafos:
        if len(p) <= tam:
            piezas.append(p)
            continue
        actual = ""
        for oracion in re.split(r"(?<=[.!?])\s+", p):
            while len(oracion) > tam:  # oración enorme sin puntos: corte duro
                piezas.append(oracion[:tam])
                oracion = oracion[tam:]
            if len(actual) + len(oracion) + 1 > tam and actual:
                piezas.append(actual)
                actual = oracion
            else:
                actual = f"{actual} {oracion}".strip()
        if actual:
            piezas.append(actual)

    fragmentos: list[str] = []
    actual = ""
    for pieza in piezas:
        if actual and len(actual) + len(pieza) + 2 > tam:
            fragmentos.append(actual)
            cola = actual[-solapamiento:]
            cola = cola[cola.find(" ") + 1:] if " " in cola else cola
            actual = f"{cola}\n\n{pieza}" if len(cola) + len(pieza) + 2 <= tam else pieza
        else:
            actual = f"{actual}\n\n{pieza}" if actual else pieza
    if actual:
        fragmentos.append(actual)
    return [Fragmento(fuente, i, t) for i, t in enumerate(fragmentos)]
