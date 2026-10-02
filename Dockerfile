# Stage 1: build the React frontend into static files.
FROM node:22-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: the Python API, which also serves the built frontend.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models
WORKDIR /app

# Dependencies before source code, so code changes rebuild in seconds.
# requirements.lock is a constraints file here: it pins versions without adding dev packages.
COPY backend/requirements.txt backend/requirements.lock ./
RUN pip install -c requirements.lock torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt -c requirements.lock

# Bake the embedding model into the image, then forbid downloads at runtime.
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
ENV HF_HUB_OFFLINE=1

COPY backend/app ./app
COPY --from=frontend /frontend/dist ./static

RUN useradd --create-home --uid 1000 documind \
    && mkdir /data && chown documind:documind /data
USER documind

ENV STATIC_DIR=/app/static DATA_DIR=/data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
