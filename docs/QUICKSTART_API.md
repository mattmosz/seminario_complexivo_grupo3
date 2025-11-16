# Guía de Inicio Rápido - API de Análisis de Reseñas

## Lo que se ha creado

### 1. **api_app.py** - API Principal
API REST completa con FastAPI que incluye:

- **POST /reviews/analyze**: Analiza reseña individual (sentimiento + tópicos)
- **GET /reviews/topics**: Resumen agregado de tópicos (positivos vs negativos)
- **GET /health**: Verificación de salud de la API
- **GET /**: Información general y endpoints disponibles

**Características:**
- Integración con pipeline existente (`scripts/`)
- CORS habilitado para dashboard
- Modelos Pydantic para validación
- Documentación automática (Swagger + ReDoc)
- Manejo robusto de errores
- Cache de datos para mejor rendimiento

### 2. **test_api.py** - Suite de Pruebas
Script completo para probar todos los endpoints:

- 7 tests automatizados
- Validación de casos positivos, negativos y errores
- Métricas de rendimiento
- Reporte de resultados

### 3. **dashboard_api_integration_example.py** - Demo de Integración
Ejemplo completo de cómo integrar la API en Streamlit:

- UI para análisis de reseñas individuales
- Visualización de resumen de tópicos
- Componentes reutilizables
- Manejo de errores y estados de carga

### 4. **API_README.md** - Documentación Completa
Documentación exhaustiva que incluye:

- Instalación y configuración
- Ejemplos de uso (curl, Python, JavaScript)
- Descripción de endpoints
- Arquitectura y flujo de datos
- Troubleshooting
- Optimizaciones para producción

## Inicio Rápido

### Paso 1: Verificar dependencias

```bash
# Las siguientes librerías ya están instaladas:
# - fastapi==0.121.0
# - uvicorn==0.38.0
# - pandas, nltk, scikit-learn

# Verificar instalación de Python environment
C:/Users/MSi/Documents/SOFTWARE/SEMINARIO/seminario_complexivo_grupo3/venv/Scripts/python.exe --version
```

### Paso 2: Iniciar la API

```bash
# Opción 1: Directamente con Python
python api_app.py

# Opción 2: Con uvicorn (para desarrollo)
uvicorn api_app:app --reload --host 0.0.0.0 --port 8000
```

Verás:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Paso 3: Verificar que funciona

Abre tu navegador en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs 
- **ReDoc**: http://localhost:8000/redoc

### Paso 4: Ejecutar tests

En otra terminal:

```bash
python test_api.py
```

### Paso 5: Probar demo de integración

```bash
streamlit run dashboard_api_integration_example.py
```

## Ejemplos Rápidos

### Desde terminal (curl)

```bash
# Analizar una reseña
curl -X POST "http://localhost:8000/reviews/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Amazing hotel with excellent service!\"}"

# Obtener resumen de tópicos
curl "http://localhost:8000/reviews/topics?n_topics=5&max_reviews=2000"

# Verificar salud
curl "http://localhost:8000/health"
```

### Desde Python

```python
import requests

# Analizar reseña
response = requests.post(
    "http://localhost:8000/reviews/analyze",
    json={"text": "Great hotel, loved the location!"}
)
result = response.json()
print(f"Sentimiento: {result['sentiment']['sentiment']}")
print(f"Score: {result['sentiment']['compound_score']}")

# Obtener tópicos
response = requests.get(
    "http://localhost:8000/reviews/topics",
    params={"n_topics": 5, "max_reviews": 5000}
)
data = response.json()
print(f"Reseñas positivas: {data['positive_topics']['total_reviews']}")
print(f"Reseñas negativas: {data['negative_topics']['total_reviews']}")
```

### Desde JavaScript

```javascript
// Analizar reseña
fetch('http://localhost:8000/reviews/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Amazing experience!'})
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## 🏗️ Estructura de Respuestas

### POST /reviews/analyze

```json
{
  "cleaned_text": "Amazing hotel with excellent service!",
  "sentiment": {
    "sentiment": "positivo",
    "compound_score": 0.8481,
    "positive_score": 0.625,
    "negative_score": 0.0,
    "neutral_score": 0.375
  },
  "topics": [
    {
      "topic_id": 1,
      "keywords": "service, staff, excellent, helpful, friendly"
    }
  ]
}
```

### GET /reviews/topics

```json
{
  "positive_topics": {
    "sentiment_type": "positivo",
    "total_reviews": 8542,
    "topics": [
      {
        "topic_id": 1,
        "keywords": "location, center, walking, distance, attractions"
      }
    ]
  },
  "negative_topics": {
    "sentiment_type": "negativo",
    "total_reviews": 1458,
    "topics": [
      {
        "topic_id": 1,
        "keywords": "room, small, old, outdated, tiny"
      }
    ]
  },
  "data_source": "hotel_reviews_processed.csv",
  "total_reviews_analyzed": 10000
}
```

## 🔧 Configuración Avanzada

### Variables de entorno (opcional)

Crear `.env` en la raíz:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
MAX_REVIEWS_DEFAULT=10000
N_TOPICS_DEFAULT=8
```

### Integración con dashboard existente

Agregar al `dashboard/app.py`:

```python
import requests

API_URL = "http://localhost:8000"

# Verificar si API está disponible
@st.cache_data(ttl=60)
def check_api_available():
    try:
        res = requests.get(f"{API_URL}/health", timeout=5)
        return res.status_code == 200
    except:
        return False

# Usar API para análisis
if check_api_available():
    st.success("Usando API para análisis")
    # Código de integración aquí
else:
    st.warning("API no disponible, usando procesamiento local")
    # Código local existente
```

## Rendimiento

### Tiempos esperados

| Endpoint | Dataset | Tiempo aprox. |
|----------|---------|---------------|
| `/reviews/analyze` | - | 2-5 segundos |
| `/reviews/topics` (1000 reviews) | Raw | 10-15 segundos |
| `/reviews/topics` (1000 reviews) | Procesado | 8-12 segundos |
| `/reviews/topics` (10000 reviews) | Procesado | 30-60 segundos |

### Optimizaciones

1. **Primera carga**: Más lenta (carga de datos)
2. **Siguientes requests**: Más rápidos (datos en cache)
3. **Dataset procesado**: Recomendado ejecutar `python main.py` primero

## Notas Importantes

### 1. Dataset

- La API busca primero `data/hotel_reviews_processed.csv`
- Si no existe, usa `data/Hotel_Reviews.csv` (limitado a 10,000 filas)
- **Recomendación**: Ejecutar `python main.py` para generar dataset procesado

### 2. VADER Lexicon

- Se descarga automáticamente en primer uso
- Si falla, ejecutar: `python -c "import nltk; nltk.download('vader_lexicon')"`

### 3. Memoria

- Con datasets grandes (>50k reseñas), puede usar 2-4 GB de RAM
- Limitar `max_reviews` en `/reviews/topics` si hay problemas de memoria

### 4. Producción

Para producción, considerar:

- Usar gunicorn/uvicorn workers
- Configurar reverse proxy (nginx)
- Agregar autenticación (JWT)
- Implementar rate limiting
- Usar base de datos (no CSV)
- Cache Redis para modelos LDA
- Logging estructurado
- Monitoring (Prometheus/Grafana)

## Troubleshooting

### Error: "No se encontró ningún dataset"
```bash
# Solución: Generar dataset procesado
python main.py
```

### Error: "Module not found"
```bash
# Verificar que estás en el entorno virtual
C:/Users/MSi/Documents/SOFTWARE/SEMINARIO/seminario_complexivo_grupo3/venv/Scripts/python.exe api_app.py
```

### Error: "Address already in use"
```bash
# Puerto 8000 ocupado, usar otro puerto
uvicorn api_app:app --port 8001
```

### Timeout en /reviews/topics
```bash
# Reducir número de reseñas
curl "http://localhost:8000/reviews/topics?max_reviews=1000"
```

## Recursos Adicionales

- **Documentación completa**: `API_README.md`
- **Tests**: `test_api.py`
- **Demo de integración**: `dashboard_api_integration_example.py`
- **Swagger UI**: http://localhost:8000/docs
- **Código fuente**: `api_app.py`

## ¡Listo!

La API está completamente funcional y lista para:

1. Recibir reseñas y analizarlas en tiempo real
2. Proveer resúmenes agregados de tópicos
3. Integrarse con el dashboard de Streamlit
4. Documentación automática
5. Tests automatizados

**Próximos pasos sugeridos:**

1. Ejecutar `python api_app.py` para iniciar la API
2. Abrir http://localhost:8000/docs para explorar
3. Ejecutar `python test_api.py` para verificar
4. Revisar `dashboard_api_integration_example.py` para ideas de integración

---

**¿Necesitas ayuda?** Revisa `API_README.md` o los comentarios en `api_app.py`
