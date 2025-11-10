# Dockerfile para API Backend - Hotel Reviews Analysis
# Imagen base optimizada con Python 3.11
FROM python:3.11-slim

# Variables de entorno para Python y configuración
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para pandas y scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements primero (para aprovechar cache de Docker)
COPY requirements-api.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

# Descargar datos de NLTK necesarios
RUN python -c "import nltk; nltk.download('vader_lexicon', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"

# Copiar código de la aplicación y datos
COPY api_app.py .
COPY scripts/ ./scripts/
COPY data/ ./data/

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 apiuser && \
    chown -R apiuser:apiuser /app
USER apiuser

# Expone el puerto para FastAPI
EXPOSE 8000

# Nota: Cloud Run ignora HEALTHCHECK y usa su propio sistema
# Si despliegas en Cloud Run, el healthcheck se maneja automáticamente

# Comando para ejecutar la API con exec (importante para Cloud Run)
CMD exec uvicorn api_app:app --host 0.0.0.0 --port ${PORT} --workers 1 

