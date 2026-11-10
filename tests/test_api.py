from fastapi.testclient import TestClient

from rag_local.api import crear_app
from rag_local.config import Config


class ModeloFalso:
    def embeddings(self, textos):
        return [[float(len(t)), 1.0, 0.0] for t in textos]

    def chat(self, mensajes):
        assert "[1]" in mensajes[1]["content"]
        yield "Según el manual, "
        yield "la respuesta es 42 [1]."


class AlmacenFalso:
    def __init__(self):
        self.fragmentos = []

    def guardar(self, fragmentos, vectores):
        self.fragmentos.extend(fragmentos)
        return len(fragmentos)

    def buscar(self, vector, k):
        return [{"fuente": f.fuente, "posicion": f.posicion, "texto": f.texto, "puntaje": 0.9} for f in self.fragmentos[:k]]


def cliente():
    return TestClient(crear_app(AlmacenFalso(), ModeloFalso(), Config(tam_fragmento=300, solapamiento=50, top_k=2)))


def test_salud():
    assert cliente().get("/salud").json() == {"estado": "ok"}


def test_preguntar_sin_documentos():
    r = cliente().post("/preguntar", json={"pregunta": "¿Qué dice el manual?"})
    assert r.status_code == 404


def test_flujo_completo():
    c = cliente()
    r = c.post("/documentos", json={"fuente": "manual.md", "texto": "La respuesta es 42.\n\nOtro párrafo."})
    assert r.json() == {"fuente": "manual.md", "fragmentos": 1}
    r = c.post("/preguntar", json={"pregunta": "¿Cuál es la respuesta?", "stream": False})
    cuerpo = r.json()
    assert cuerpo["respuesta"] == "Según el manual, la respuesta es 42 [1]."
    assert cuerpo["fuentes"][0]["fuente"] == "manual.md"


def test_streaming_incluye_fuentes():
    c = cliente()
    c.post("/documentos", json={"fuente": "manual.md", "texto": "La respuesta es 42."})
    r = c.post("/preguntar", json={"pregunta": "¿Cuál es la respuesta?"})
    assert r.text.startswith("Según el manual")
    assert "Fuentes:" in r.text and "manual.md" in r.text


def test_valida_la_pregunta():
    assert cliente().post("/preguntar", json={"pregunta": "a"}).status_code == 422
