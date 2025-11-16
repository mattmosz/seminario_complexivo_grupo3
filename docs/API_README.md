# API de Análisis de Reseñas de Hoteles

API REST construida con FastAPI para analizar sentimientos y extraer tópicos de reseñas de hoteles.

## Características

- **Análisis de reseñas individuales**: Analiza el sentimiento y extrae tópicos de una reseña
- **Resumen agregado de tópicos**: Obtiene tópicos más mencionados en reseñas positivas y negativas
- **Alto rendimiento**: Usa FastAPI con validación automática de datos
- **Documentación interactiva**: Swagger UI y ReDoc incluidos
- **CORS habilitado**: Listo para integración con dashboard

## Instalación

### Prerrequisitos

```bash
# Ya están instalados en el proyecto:
# - fastapi==0.121.0
# - uvicorn==0.38.0
# - pandas, nltk, scikit-learn
```

### Configuración

El proyecto ya tiene todas las dependencias instaladas. La API usa los módulos del pipeline en la carpeta `scripts/`:

- `text_processing.py` - Limpieza de texto
- `sentiment_analysis.py` - Análisis VADER
- `topic_modeling.py` - Extracción de tópicos con LDA

## Uso

### Iniciar el servidor

```bash
# Desde la raíz del proyecto
python api_app.py
```

O usando uvicorn directamente:

```bash
uvicorn api_app:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs
- Documentación alternativa: http://localhost:8000/redoc

### Endpoints disponibles

#### 1. `POST /reviews/analyze` - Analizar una reseña individual

Analiza el sentimiento y extrae tópicos de una reseña.

**Request:**
```json
{
  "text": "El hotel fue increíble. El personal muy amable y la habitación estaba limpia. Ubicación perfecta."

}
```

**Response:**
```json
{
  "cleaned_text": "El hotel fue increíble. El personal muy amable y la habitación estaba limpia. Ubicación perfecta.",
  "sentiment": {
    "sentiment": "positivo",
    "compound_score": 0.9468,
    "positive_score": 0.392,
    "negative_score": 0.0,
    "neutral_score": 0.608
  },
  "topics": [
    {
      "topic_id": 1,
      "keywords": "personal, amable, servicio, servicial, excelente"
    },
    {
      "topic_id": 2,
      "keywords": "habitación, limpia, cómoda, cama, espaciosa"
    }
  ]
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/reviews/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hotel increíble con excelente servicio"}'
```

**Ejemplo con Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/reviews/analyze",
    json={"text": "Hotel increíble con excelente servicio"}
)
print(response.json())
```

#### 2. `GET /reviews/topics` - Obtener resumen de tópicos agregados

Proporciona un resumen de los tópicos más frecuentes en reseñas positivas y negativas.

**Parámetros de query:**
- `n_topics` (opcional): Número de tópicos a extraer por categoría (default: 8)
- `max_reviews` (opcional): Máximo número de reseñas a analizar (default: 10000)

**Request:**
```bash
GET /reviews/topics?n_topics=5&max_reviews=5000
```

**Response:**
```json
{
  "positive_topics": {
    "sentiment_type": "positivo",
    "total_reviews": 3542,
    "topics": [
      {
        "topic_id": 1,
        "keywords": "ubicación, centro, caminata, distancia, atracciones"
      },
      {
        "topic_id": 2,
        "keywords": "personal, amable, servicial, servicio, excelente"
      },
      {
        "topic_id": 3,
        "keywords": "desayuno, comida, restaurante, delicioso, variedad"
      }
    ]
  },
  "negative_topics": {
    "sentiment_type": "negativo",
    "total_reviews": 1458,
    "topics": [
      {
        "topic_id": 1,
        "keywords": "habitación, pequeña, vieja, anticuada, diminuta"
      },
      {
        "topic_id": 2,
        "keywords": "ruido, ruidoso, calle, fuerte, dormir"
      }
    ]
  },
  "data_source": "hotel_reviews_processed.csv",
  "total_reviews_analyzed": 5000
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/reviews/topics?n_topics=5&max_reviews=5000"
```

**Ejemplo con Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/reviews/topics",
    params={"n_topics": 5, "max_reviews": 5000}
)
print(response.json())
```

#### 3. `GET /health` - Verificar estado de la API

Comprueba que la API está funcionando correctamente.

**Response:**
```json
{
  "status": "healthy",
  "vader_available": true,
  "data_loaded": true,
  "total_reviews": 515738
}
```

## Integración con Dashboard

### Ejemplo de uso en Streamlit

```python
import streamlit as st
import requests

# Configurar URL de la API
API_URL = "http://localhost:8000"

# Analizar una reseña
st.title("Análisis de Reseña")
user_review = st.text_area("Ingrese su reseña:")

if st.button("Analizar"):
    response = requests.post(
        f"{API_URL}/reviews/analyze",
        json={"text": user_review}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        st.subheader("Sentimiento")
        st.write(f"Clasificación: {result['sentiment']['sentiment']}")
        st.write(f"Score: {result['sentiment']['compound_score']:.3f}")
        
        st.subheader("Tópicos detectados")
        for topic in result['topics']:
            st.write(f"Tema {topic['topic_id']}: {topic['keywords']}")
    else:
        st.error("Error al analizar la reseña")

# Obtener resumen de tópicos
if st.button("Cargar resumen de tópicos"):
    response = requests.get(f"{API_URL}/reviews/topics")
    
    if response.status_code == 200:
        data = response.json()
        
        st.subheader("Tópicos en reseñas positivas")
        for topic in data['positive_topics']['topics']:
            st.write(f"• {topic['keywords']}")
        
        st.subheader("Tópicos en reseñas negativas")
        for topic in data['negative_topics']['topics']:
            st.write(f"• {topic['keywords']}")
```

## Arquitectura

### Flujo de análisis individual (`/reviews/analyze`)

1. **Limpieza de texto**: Usa `clean_text()` para normalizar la reseña
2. **Análisis de sentimiento**: Aplica VADER para obtener scores
3. **Extracción de tópicos**: Usa LDA con contexto del dataset para detectar temas
4. **Respuesta estructurada**: Devuelve JSON con sentimiento y tópicos

### Flujo de resumen agregado (`/reviews/topics`)

1. **Carga de datos**: Lee el dataset procesado o raw (limitado)
2. **Filtrado**: Separa reseñas positivas y negativas
3. **Modelado de tópicos**: Aplica LDA independientemente a cada grupo
4. **Agregación**: Devuelve tópicos de ambos grupos con estadísticas

### Fuentes de datos

La API intenta cargar datos en el siguiente orden:

1. **Dataset procesado** (`data/hotel_reviews_processed.csv`): 
   - Ya tiene sentimientos analizados
   - Texto limpio
   - Países estandarizados
   
2. **Dataset raw** (`data/Hotel_Reviews.csv`):
   - Procesa on-the-fly (limitado a 10,000 filas)
   - Analiza sentimientos al cargar

## Notas importantes

### Rendimiento

- El primer request puede tardar más (carga de datos y modelos)
- Los modelos LDA se entrenan en cada request (considerar cache para producción)
- El endpoint `/reviews/topics` puede tardar 30-60 segundos con datasets grandes

### Optimizaciones sugeridas

Para producción, considerar:

1. **Cache de modelos**: Guardar modelos LDA entrenados
2. **Base de datos**: Usar PostgreSQL/MongoDB en lugar de CSV
3. **Queue system**: Celery para procesamiento asíncrono
4. **Rate limiting**: Limitar requests por cliente
5. **Autenticación**: JWT tokens para seguridad

### Troubleshooting

**Error: "No se encontró ningún dataset"**
- Ejecutar `python main.py` para generar `hotel_reviews_processed.csv`
- O asegurarse que `Hotel_Reviews.csv` existe en `data/`

**Error: "NLTK data not found"**
- La API descarga automáticamente VADER lexicon
- Si falla, ejecutar manualmente: `python -c "import nltk; nltk.download('vader_lexicon')"`

**Error: "Module not found"**
- Verificar que los scripts estén en `scripts/`
- El path se agrega automáticamente en `api_app.py`

## Ejemplos avanzados

### Batch processing con la API

```python
import requests
import pandas as pd

API_URL = "http://localhost:8000"

# Lista de reseñas
reviews = [
    "Great hotel, loved it!",
    "Terrible experience, never coming back",
    "Average stay, nothing special"
]

# Analizar cada una
results = []
for review in reviews:
    response = requests.post(
        f"{API_URL}/reviews/analyze",
        json={"text": review}
    )
    if response.status_code == 200:
        results.append(response.json())

# Convertir a DataFrame
df_results = pd.DataFrame([
    {
        'review': r['cleaned_text'],
        'sentiment': r['sentiment']['sentiment'],
        'score': r['sentiment']['compound_score']
    }
    for r in results
])

print(df_results)
```

### Integración con JavaScript/React

```javascript
// Analizar reseña
async function analyzeReview(reviewText) {
  const response = await fetch('http://localhost:8000/reviews/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: reviewText })
  });
  
  const result = await response.json();
  console.log('Sentiment:', result.sentiment.sentiment);
  console.log('Topics:', result.topics);
  return result;
}

// Obtener tópicos
async function getTopics() {
  const response = await fetch('http://localhost:8000/reviews/topics?n_topics=5');
  const data = await response.json();
  console.log('Positive topics:', data.positive_topics.topics);
  console.log('Negative topics:', data.negative_topics.topics);
  return data;
}
```

## Licencia

Parte del proyecto Seminario Complexivo - Análisis de Reseñas de Hoteles

## Soporte

Para reportar issues o contribuir, contactar al equipo de desarrollo.
