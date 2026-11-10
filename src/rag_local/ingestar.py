"""Carga todos los .md y .txt de una carpeta: python -m rag_local.ingestar ejemplos/documentos"""
import sys
from pathlib import Path

import httpx

API = "http://localhost:8000"


def main() -> int:
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else "ejemplos/documentos")
    for ruta in sorted([*carpeta.glob("*.md"), *carpeta.glob("*.txt")]):
        r = httpx.post(f"{API}/documentos", json={"fuente": ruta.name, "texto": ruta.read_text(encoding="utf-8")}, timeout=300)
        r.raise_for_status()
        print(f"{ruta.name}: {r.json()['fragmentos']} fragmentos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
