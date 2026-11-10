# rag-local

Un servicio de preguntas y respuestas sobre tus propios documentos (RAG) que corre completo en tus servidores: Elasticsearch como almacén vectorial y Ollama para los embeddings y las respuestas. Ningún documento sale a una API externa.

> **In English:** a self-hosted RAG service. Elasticsearch stores the vectors, Ollama runs the embedding and chat models locally, and a FastAPI app ingests documents and streams answers with numbered source citations. No document leaves your servers.

Es una versión genérica, con documentos de una empresa ficticia, de la arquitectura que uso en proyectos de IA sobre datos privados.

## Cómo funciona

```text
documento ──► fragmentos con solapamiento ──► embeddings (Ollama) ──► Elasticsearch (dense_vector)

pregunta ──► embedding ──► búsqueda kNN ──► prompt con fragmentos numerados ──► modelo de chat (Ollama) ──► respuesta con citas [1][2]
```

- **Fragmentos que respetan párrafos**, con un solapamiento configurable para que una idea partida en dos no se pierda.
- **Citas verificables:** cada fragmento va numerado en el prompt y la respuesta termina con la lista de fuentes y su puntaje.
- **Respuesta en streaming**, palabra por palabra, o en un solo JSON con `"stream": false`.
- **Sin inventar:** el prompt obliga al modelo a decir que no sabe cuando el contexto no tiene la respuesta.

## Arranque rápido

```bash
docker compose up -d --build
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:7b
pip install httpx && python -m rag_local.ingestar ejemplos/documentos
```

Pregunta:

```bash
curl -N http://localhost:8000/preguntar \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuánto tiempo se guardan los datos personales?"}'
```

La documentación interactiva de la API queda en http://localhost:8000/docs.

## API

| Método | Ruta | Qué hace |
| --- | --- | --- |
| `GET` | `/salud` | Comprueba que el servicio responde |
| `POST` | `/documentos` | Recibe `{"fuente", "texto"}`, lo fragmenta, calcula embeddings y lo indexa |
| `POST` | `/preguntar` | Recibe `{"pregunta", "k", "stream"}` y responde con citas |

## Configuración

Por variables de entorno: `ES_URL`, `OLLAMA_URL`, `MODELO_EMBEDDINGS` (por defecto `nomic-embed-text`), `MODELO_CHAT` (por defecto `qwen2.5:7b`), `INDICE`, `TAM_FRAGMENTO`, `SOLAPAMIENTO` y `TOP_K`.

Con GPU NVIDIA, descomenta la sección `deploy` del servicio `ollama` en `docker-compose.yml`. Para modelos más grandes, elige uno que haga bien llamadas a herramientas y siga instrucciones en español.

## Pruebas

Las pruebas usan un modelo y un almacén falsos, así que corren sin Docker ni GPU:

```bash
pip install -e ".[dev]"
pytest
```

## Licencia

MIT
