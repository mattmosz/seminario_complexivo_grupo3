# Dashboard Deployment - Streamlit Cloud

Guía completa para desplegar el dashboard de análisis de reseñas de hoteles en Streamlit Cloud.

## Pre-requisitos

1. API backend desplegada en Render (o Docker)
2. Cuenta en [Streamlit Cloud](https://streamlit.io/cloud)
3. Repositorio en GitHub con el código actualizado

## Deployment en Streamlit Cloud

### Paso 1: Preparar Repositorio

Asegúrate de tener estos archivos en tu repo:

```
dashboard/
├── app.py                         Dashboard principal
├── requirements.txt               Dependencias mínimas
├── .streamlit/
│   ├── config.toml                Configuración de Streamlit
│   └── secrets.toml.example       Ejemplo de secrets
└── README.md                      Este archivo
```

### Paso 2: Conectar con Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con GitHub
3. Click en **"New app"**
4. Selecciona tu repositorio
5. Configura:
   - **Main file path**: `dashboard/app.py`
   - **Python version**: 3.11
   - **Branch**: `main`

### Paso 3: Configurar Secrets

En Streamlit Cloud, ve a **Settings** → **Secrets** y agrega:

```toml
# URL de tu API desplegada en Render
API_URL = "https://hotel-reviews-api.onrender.com"

# Timeout para peticiones (30 segundos recomendado)
API_TIMEOUT = 30
```

**IMPORTANTE**: Reemplaza `hotel-reviews-api.onrender.com` con la URL real de tu API.

### Paso 4: Deploy

1. Click en **"Deploy"**
2. Espera 3-5 minutos (instalación de dependencias)
3. Tu dashboard estará en: `https://tu-app.streamlit.app`

## 🔧 Configuración

### Requirements (solo visualización)

El archivo [`requirements.txt`](requirements.txt) contiene **solo** las librerías necesarias para la UI:

```txt
streamlit==1.38.0      # Framework
plotly==5.24.1         # Gráficos interactivos
pandas==2.2.2          # Manipulación de datos
numpy==1.26.4          # Operaciones numéricas
requests==2.32.3       # Cliente HTTP para API
wordcloud==1.9.3       # Renderizado de nubes
Pillow==10.4.0         # Procesamiento de imágenes
```

**NO incluye**:
- scikit-learn (está en la API)
- nltk (está en la API)
- vaderSentiment (está en la API)

### Variables de Entorno

El dashboard soporta configuración via secrets:

| Variable | Descripción | Default | Requerido |
|----------|-------------|---------|-----------|
| `API_URL` | URL de la API backend | `http://localhost:8000` | ✅ Sí |
| `API_TIMEOUT` | Timeout en segundos | `30` |  No |

## Testing Local

### Opción 1: Con API local

```bash
cd dashboard

# Crear archivo de secrets local
echo 'API_URL = "http://localhost:8000"' > .streamlit/secrets.toml
echo 'API_TIMEOUT = 30' >> .streamlit/secrets.toml

# Iniciar dashboard
streamlit run app.py
```

### Opción 2: Con API en Render

```bash
cd dashboard

# Crear archivo de secrets con API de producción
echo 'API_URL = "https://tu-api.onrender.com"' > .streamlit/secrets.toml
echo 'API_TIMEOUT = 30' >> .streamlit/secrets.toml

# Iniciar dashboard
streamlit run app.py
```

## Arquitectura

```
┌──────────────────────────────────┐
│   STREAMLIT CLOUD (Frontend)     │
│   - Solo UI y visualizaciones    │
│   - Consume API REST              │
│   - Dashboard interactivo         │
└───────────┬──────────────────────┘
            │
            │ HTTPS/JSON
            │ (requests)
            │
┌───────────▼──────────────────────┐
│   RENDER (Backend API)           │
│   - Docker Container             │
│   - FastAPI + Uvicorn            │
│   - Procesamiento NLP            │
│   - Topic Modeling               │
│   - Análisis de Sentimiento      │
└──────────────────────────────────┘
```

## Troubleshooting

### Error: "API NO DISPONIBLE"

**Causa**: El dashboard no puede conectarse a la API.

**Solución**:
1. Verifica que la API esté corriendo: `https://tu-api.onrender.com/health`
2. Revisa los secrets en Streamlit Cloud
3. Confirma que `API_URL` no tenga trailing slash `/`
4. Verifica CORS en la API (debe permitir `*.streamlit.app`)

### Error: "ModuleNotFoundError"

**Causa**: Falta una dependencia en `requirements.txt`.

**Solución**:
1. Agrega la librería faltante a `dashboard/requirements.txt`
2. Haz commit y push
3. Streamlit Cloud redesplegará automáticamente

### Dashboard muy lento

**Causa**: Demasiadas peticiones a la API o cache deshabilitado.

**Solución**:
1. Verifica que las funciones usen `@st.cache_data`
2. Ajusta el TTL del cache (300s recomendado)
3. Reduce el `sample_size` en word clouds (3000 recomendado)

### Error de memoria

**Causa**: Streamlit Cloud tiene límites de memoria (1GB en plan free).

**Solución**:
1. Asegúrate de que el procesamiento pesado esté en la API
2. No guardes datasets grandes en session_state
3. Usa `@st.cache_data` para evitar recálculos

## Actualizar Deployment

```bash
# Hacer cambios en el código
git add .
git commit -m "Update dashboard"
git push origin main

# Streamlit Cloud redesplegará automáticamente
```

## Logs y Monitoring

### Ver logs en tiempo real

1. Ve a tu app en Streamlit Cloud
2. Click en **"Manage app"** (esquina inferior derecha)
3. Tab **"Logs"**

### Reboot si hay problemas

1. **"Manage app"** → **"Reboot app"**
2. O desde settings: **"⋮"** → **"Reboot app"**

## Custom Domain (Opcional)

Para usar tu propio dominio:

1. Upgrade a plan Pro en Streamlit Cloud
2. Ve a **Settings** → **"Custom domain"**
3. Configura DNS según instrucciones

## Best Practices

1. **Siempre usar secrets** para API_URL (nunca hardcodear)
2. **Cachear datos** con `@st.cache_data(ttl=300)`
3. **Manejar errores** de API con try/except
4. **Mostrar spinners** durante carga (`st.spinner()`)
5. **Limitar tamaño de datos** en session_state
6. **Verificar API availability** al inicio
7. **Usar loading states** para mejor UX

## Soporte

- **Documentación Streamlit**: https://docs.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **Status Page**: https://streamlitstatus.com

## URLs de Referencia

- **Dashboard**: https://tu-app.streamlit.app
- **API Backend**: https://hotel-reviews-api.onrender.com
- **API Docs**: https://hotel-reviews-api.onrender.com/docs
- **Repository**: https://github.com/mattmosz/seminario_complexivo_grupo3

---

**Última actualización**: Enero 2025  
**Versión Dashboard**: 2.0.0  
**Mantenido por**: Seminario de Analítica con Python
