import pytest

from rag_local.fragmentos import fragmentar

TEXTO = "\n\n".join(f"Párrafo {i}. " + "Una oración de relleno con algo de contenido útil. " * 6 for i in range(12))


def test_respeta_el_tamano():
    frags = fragmentar(TEXTO, "doc.md", tam=500, solapamiento=80)
    assert len(frags) > 1
    assert all(len(f.texto) <= 500 for f in frags)


def test_posiciones_y_fuente():
    frags = fragmentar(TEXTO, "doc.md", tam=500, solapamiento=80)
    assert [f.posicion for f in frags] == list(range(len(frags)))
    assert {f.fuente for f in frags} == {"doc.md"}


def test_solapamiento_entre_fragmentos():
    frags = fragmentar(TEXTO, "doc.md", tam=500, solapamiento=80)
    for anterior, siguiente in zip(frags, frags[1:]):
        inicio = siguiente.texto.split("\n\n")[0]
        assert inicio in anterior.texto or len(inicio) > 80


def test_no_pierde_contenido():
    frags = fragmentar(TEXTO, "doc.md", tam=500, solapamiento=80)
    unido = " ".join(f.texto for f in frags)
    for i in range(12):
        assert f"Párrafo {i}." in unido


def test_parrafo_gigante_sin_puntos():
    frags = fragmentar("x" * 2000, "doc.md", tam=500, solapamiento=50)
    assert all(len(f.texto) <= 500 for f in frags)
    assert sum(len(f.texto) for f in frags) >= 2000


def test_solapamiento_invalido():
    with pytest.raises(ValueError):
        fragmentar("hola", "doc.md", tam=100, solapamiento=100)
