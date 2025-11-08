# Imagen base ligera de Python
FROM python:3.11-slim

# Evita bytecode y buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Asegura que NLTK y demás dependencias funcionen correctamente
RUN python -m nltk.downloader vader_lexicon stopwords punkt

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando para ejecutar la API
CMD ["uvicorn", "api_app:app", "--host", "0.0.0.0", "--port", "8000"]
