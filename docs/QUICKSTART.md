# Guía Rápida de Ejecución

## Arquitectura del Proyecto

El proyecto ahora tiene **dos componentes separados**:

1. **Backend API** (FastAPI) - `api_app.py`
2. **Frontend Dashboard** (Streamlit) - `dashboard/app.py`

Ambos deben ejecutarse simultáneamente para que el dashboard funcione correctamente.

---

## Inicio Rápido

### Paso 1: Iniciar el Backend API

Abre una terminal en la raíz del proyecto y ejecuta:

```bash
python api_app.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

La API estará disponible en:
- **Base URL**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

### Paso 2: Iniciar el Dashboard

Abre **otra terminal** (mantén la primera corriendo) y ejecuta:

```bash
streamlit run dashboard/app.py
```

El dashboard se abrirá automáticamente en tu navegador en:
- **URL**: http://localhost:8501

---

## Verificación de Funcionamiento

### 1. Verificar que la API esté corriendo:

Abre http://localhost:8000/health en tu navegador o ejecuta:

```bash
curl http://localhost:8000/health
```

Deberías recibir:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "dataset_loaded": true,
  "total_reviews": 
}
```

### 2. Verificar que el Dashboard se conecte a la API:

En el dashboard, revisa la parte superior. Deberías ver:
- **API CONECTADA** (en verde)
- Si ves **API NO DISPONIBLE** (en rojo), verifica que la API esté corriendo

---

## Funcionalidades Disponibles

Una vez ambos servicios estén corriendo, podrás usar:

### Tabs Principales:
1. **Análisis General** - Estadísticas, distribuciones, top hoteles
2. **Geografía** - Análisis por nacionalidad y países
3. **Palabras Clave** - Word clouds de reseñas positivas/negativas
4. **Datos Detallados** - Tabla con filtros y búsqueda
5. **Sentimiento** - Análisis de sentimiento detallado (si VADER está activo)
6. **Análisis con API** - Análisis individual de reseñas y tópicos

### Filtros en Sidebar:
- Filtrar por hoteles específicos
- Filtrar por nacionalidad del revisor
- Filtrar por puntuación mínima
- Filtrar por sentimiento (si VADER está activo)

---

## Solución de Problemas

### Problema: "API NO DISPONIBLE"

**Causa**: El backend no está corriendo o no está en el puerto correcto.

**Solución**:
1. Verifica que `python api_app.py` esté corriendo en otra terminal
2. Revisa que la API esté en http://localhost:8000
3. Haz clic en "Verificar API" en el dashboard

### Problema: "Connection refused"

**Causa**: La API no ha iniciado completamente o está en un puerto diferente.

**Solución**:
1. Espera unos segundos a que la API inicie completamente
2. Verifica la terminal donde corre la API - debe decir "Application startup complete"
3. Si cambiaste el puerto, actualiza `API_URL` en `dashboard/app.py`

### Problema: "Dataset not found"

**Causa**: No encuentra el archivo CSV de datos.

**Solución**:
1. Verifica que existe `data/hotel_reviews_processed.csv` o `data/Hotel_Reviews.csv`
2. La API busca automáticamente en este orden:
   - `data/hotel_reviews_processed.csv` (preferido)
   - `data/Hotel_Reviews.csv` (fallback)

### Problema: Timeout en análisis de tópicos

**Causa**: El análisis de muchas reseñas puede tardar.

**Solución**:
1. Es normal - el análisis de tópicos puede tardar 30-90 segundos
2. Reduce el número de reseñas a analizar (usa el slider "Máximo de reseñas")
3. El timeout está configurado a 120 segundos

---

## Configuración Avanzada

### Cambiar Puerto de la API

Edita `api_app.py` al final del archivo:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambia 8000 por el puerto deseado
```

Y actualiza `API_URL` en `dashboard/app.py`:

```python
API_URL = os.getenv("API_URL", "http://localhost:TU_PUERTO")
```

### Usar Variables de Entorno

En lugar de editar el código, puedes usar variables de entorno:

**PowerShell**:
```powershell
$env:API_URL = "http://localhost:8000"
streamlit run dashboard/app.py
```

**CMD**:
```cmd
set API_URL=http://localhost:8000
streamlit run dashboard/app.py
```

### Modo Debug

Para más información de debug en la API:

```bash
# En la terminal de la API, presiona CTRL+C para detener
# Luego ejecuta con modo reload (auto-restart en cambios):
uvicorn api_app:app --reload --log-level debug
```

---

## Dependencias

### Para la API:
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pandas>=2.2.0
pydantic>=2.6.0
scikit-learn>=1.4.0
nltk>=3.8.0
vaderSentiment>=3.3.2
```

### Para el Dashboard:
```txt
streamlit>=1.51.0
pandas>=2.2.0
plotly>=5.18.0
wordcloud>=1.9.0
requests>=2.31.0
```

Instalar todas las dependencias:
```bash
pip install -r requirements.txt
pip install -r dashboard/requirements.txt
```

---

## Deployment en Producción

### Backend (Render con Docker):

1. Crear `Dockerfile` en la raíz
2. Configurar en render.yaml
3. Deploy a Render

### Frontend (Streamlit Cloud):

1. Subir código a GitHub
2. Conectar con Streamlit Cloud
3. Configurar secrets (API_URL)
4. Deploy automático

Ver `docs/deploy_guía.md` para instrucciones detalladas.

---

## Recursos Adicionales

- **Documentación API**: http://localhost:8000/docs (cuando está corriendo)
- **MIGRATION_SUMMARY.md**: Detalles de la arquitectura y cambios
- **docs/api_endpoints.md**: Documentación de endpoints
- **docs/arquitectura.md**: Diagrama de arquitectura completo

---

## Tips de Uso

1. **Siempre inicia la API primero** antes del dashboard
2. **Usa el cache** - La API cachea datos durante 5 minutos para mejor rendimiento
3. **Ajusta filtros** - Menos reseñas = respuestas más rápidas
4. **Revisa logs** - La terminal de la API muestra logs útiles para debugging
5. **Descarga resultados** - Puedes descargar análisis en formato JSON

---

**¿Necesitas ayuda?**
- Revisa los logs en las terminales
- Visita http://localhost:8000/docs para probar endpoints manualmente
- Consulta MIGRATION_SUMMARY.md para entender la arquitectura
