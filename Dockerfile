FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "rag_local.api:app_por_defecto", "--factory", "--host", "0.0.0.0", "--port", "8000"]
