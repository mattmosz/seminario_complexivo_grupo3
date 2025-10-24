# ==========================
# 1️⃣ Imagen base oficial de Python
# ==========================
FROM python:3.11-slim

# ==========================
# 2️⃣ Variables de entorno básicas
# ==========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================
# 3️⃣ Crear y entrar al directorio de trabajo
# ==========================
WORKDIR /app

# ==========================
# 4️⃣ Copiar requirements e instalarlos
# ==========================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================
# 5️⃣ Copiar el código de la app al contenedor
# ==========================
COPY ./app ./app

# ==========================
# 6️⃣ Exponer el puerto del backend
# ==========================
EXPOSE 8000

# ==========================
# 7️⃣ Comando por defecto para ejecutar FastAPI con Uvicorn
# ==========================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
