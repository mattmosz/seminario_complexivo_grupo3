# API Backend - Hotel Reviews Analysis

API REST completa construida con FastAPI para análisis de reseñas de hoteles. Maneja toda la lógica de negocio: procesamiento de datos, análisis de sentimiento, extracción de tópicos y generación de visualizaciones.

## Características

- **8 Endpoints REST** completos
- **Análisis de Sentimiento** con VADER
- **Topic Modeling** con LDA
- **Word Cloud** data generation
- **Cache inteligente** con TTL
- **CORS configurado** para producción
- **Validación** con Pydantic
- **Documentación automática** (Swagger/ReDoc)
- **Health checks** para monitoring
- **Docker ready** para deployment

## Dependencias

Ver `requirements-api.txt`:
- FastAPI 0.110.0
- Uvicorn 0.27.1
- Pandas 2.2.0
- scikit-learn 1.4.0
- NLTK 3.8.1
- vaderSentiment 3.3.2

## Ejecución Local

### Opción 1: Python directo

```bash
# Instalar dependencias
pip install -r requirements-api.txt

# Ejecutar API
python api_app.py
```

La API estará disponible en:
- **Base URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Opción 2: Docker

```bash
# Construir imagen
docker build -t hotel-reviews-api .

# Ejecutar contenedor
docker run -d -p 8000:8000 --name api hotel-reviews-api

# Ver logs
docker logs -f api

# Detener
docker stop api
```

### Opción 3: PowerShell Script (Windows)

```powershell
.\docker-run.ps1
```

## 📡 Endpoints Disponibles

### Dataset y Estadísticas
- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /stats` - Estadísticas del dataset
- `GET /hotels` - Lista de hoteles
- `GET /nationalities` - Lista de nacionalidades

### Análisis y Procesamiento
- `POST /reviews/filter` - Filtrar reseñas
- `POST /reviews/analyze` - Analizar reseña individual
- `POST /reviews/topics` - Extracción de tópicos
- `POST /reviews/wordcloud` - Datos para word cloud

## Deployment en Render

### Paso 1: Preparar Repositorio

Asegúrate de tener estos archivos en tu repo:
- `api_app.py` 
- `requirements-api.txt` 
- `Dockerfile` 
- `render.yaml` 
- `scripts/` 
- `data/` 

### Paso 2: Conectar con Render

1. Ve a [render.com](https://render.com)
2. Crea una cuenta o inicia sesión
3. Clic en "New +" → "Blueprint"
4. Conecta tu repositorio de GitHub
5. Render detectará automáticamente `render.yaml`

### Paso 3: Configurar Variables de Entorno

En el dashboard de Render, configura:
```
PORT=8000
ALLOWED_ORIGINS=https://tu-app.streamlit.app
```

### Paso 4: Deploy

- Render construirá la imagen Docker automáticamente
- El deployment toma ~5-10 minutos
- La API estará en: `https://tu-servicio.onrender.com`

## Configuración de Seguridad

### CORS

Por defecto está configurado para:
```python
allow_origins=[
    "http://localhost:8501",
    "https://*.streamlit.app",
    "*"  # Cambiar en producción
]
```

Para producción, actualiza en `api_app.py`:
```python
allow_origins=[
    "https://tu-dashboard-especifico.streamlit.app"
]
```

### Variables de Entorno

Soportadas:
- `PORT` - Puerto del servidor (default: 8000)
- `ALLOWED_ORIGINS` - Dominios permitidos para CORS

## Uso con Dashboard

El dashboard de Streamlit consume esta API. Configurar:

**En Streamlit Cloud** (`.streamlit/secrets.toml`):
```toml
API_URL = "https://tu-api.onrender.com"
API_TIMEOUT = 30
```

**Localmente** (variables de entorno):
```bash
export API_URL=http://localhost:8000
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Obtener estadísticas
```bash
curl http://localhost:8000/stats
```

### Filtrar reseñas
```bash
curl -X POST http://localhost:8000/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{"sentiment": "positivo", "score_min": 8.0}'
```

## Performance

### Cache TTL
- Health check: 60 segundos
- Listas (hoteles, nacionalidades): 300 segundos
- Dataset completo: 300 segundos

### Límites
- Word cloud: max 500K caracteres de texto
- Tópicos: requiere mínimo 100 reseñas
- Sample size: configurable (default: 3000 reseñas)

## Troubleshooting

### Error: "Dataset no encontrado"
Verifica que existe `data/hotel_reviews_processed.csv`

### Error: "VADER not available"
Ejecuta: `python -c "import nltk; nltk.download('vader_lexicon')"`

### Docker: Build fails
Verifica que tienes espacio en disco y Docker está corriendo

### Render: Service unhealthy
- Verifica logs en Render dashboard
- Asegúrate que el archivo CSV está en el repo
- Confirma que `requirements-api.txt` tiene todas las dependencias

## Logs

### Local
```bash
# Ver logs en terminal donde corre la API
```

### Docker
```bash
docker logs -f hotel-reviews-api
```

### Render
Ver en el dashboard: Service → Logs

## Actualizar Deployment

### Render (Automático)
```bash
git add .
git commit -m "Update API"
git push origin main
# Render redeploya automáticamente
```

### Docker (Manual)
```bash
docker build -t hotel-reviews-api .
docker stop api && docker rm api
docker run -d -p 8000:8000 --name api hotel-reviews-api
```

## Tips de Producción

1. **Monitoring**: Usa el endpoint `/health` para healthchecks
2. **Logs**: Configura log aggregation (e.g., Papertrail)
3. **Cache**: Ajusta `CACHE_TTL_SECONDS` según necesidad
4. **Workers**: Para más tráfico, aumenta workers en Dockerfile
5. **Resources**: Render Free tier tiene límites, considera upgrade

## Soporte

- **Documentación API**: http://localhost:8000/docs
- **Issues**: GitHub Issues del repositorio
- **Logs**: Revisa logs para debugging detallado

---

**Versión**: 2.0.0  
**Última actualización**: Enero 2025  
**Autor**: Seminario de Analítica con Python
