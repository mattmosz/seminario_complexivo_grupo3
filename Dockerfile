# imagen oficial de python slim 3.10
FROM python:3.10-slim

# creacion de la carpeta de la aplicacion dentro del contenedor
WORKDIR /app

# copia de los archivos de requerimientos de la api
COPY requirements-api.txt .

# instalacion de las dependencias
# paquetes de linux y librerias del sistema necesarias
RUN apt-get update && apt-get install -y libgomp1

# instalacion de las dependencias de python
RUN pip install --no-cache-dir -r requirements-api.txt

# copia de todos los archivos de la aplicacion al contenedor
COPY . . 

#
CMD ["uvicorn", "api_app:app", "--host", "0.0.0.0", "--port", "8000"]


