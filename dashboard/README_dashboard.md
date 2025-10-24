# 📊 Dashboard — Análisis de Reseñas de Hoteles (Booking.com)

Dashboard profesional construido con **Streamlit**, **Plotly** y **FastAPI**  
para visualizar y analizar reseñas de hoteles con análisis de sentimiento (VADER)  
y extracción de tópicos.

---

## 🧩 Estructura del Proyecto

```
dashboard/
├─ app.py                     # Aplicación principal Streamlit
├─ requirements.txt           # Dependencias
├─ .streamlit/
│  └─ secrets.toml            # Configuración (API, token, CSV)
├─ assets/                    # Logo, CSS, imágenes
├─ config/                    # Configuración global
├─ services/                  # Cliente API
├─ components/                # Gráficas, KPIs, tablas
└─ README.md                  # Este archivo
```

---

## ⚙️ Configuración Inicial

### 1️⃣ Instalar dependencias

Asegúrate de tener **Python 3.10 o superior** y luego ejecuta:

```bash
cd dashboard
pip install -r requirements.txt
```

---

### 2️⃣ Configurar conexión (`.streamlit/secrets.toml`)

Crea el archivo `.streamlit/secrets.toml` con este contenido:

```toml
BASE_API_URL = "http://localhost:8000/v1"
TOKEN = ""
OFFLINE_CSV = "data/hotel_reviews_processed.csv"
```

📍 Si aún no tienes el backend funcionando, el dashboard operará en **modo offline**,  
usando tu archivo CSV local (`data/hotel_reviews_processed.csv`).

---

### 3️⃣ Ejecutar el dashboard

```bash
streamlit run app.py
```

📍 Luego abre tu navegador en:  
👉 [http://localhost:8501](http://localhost:8501)

---

## 🧠 Funcionalidades Principales

- **Filtros:** Hotel, nacionalidad, sentimiento, rango de puntuación  
- **KPIs dinámicos:** Total de reseñas, filtradas, promedio, satisfacción, hoteles únicos  
- **Gráficas interactivas:**
  - Área apilada por categoría (sentimiento/puntuación)
  - Top 10 hoteles por reseñas
  - Distribución de nacionalidades
  - Tendencia de puntuaciones
  - Histograma avanzado
  - Mapas interactivos de reseñas
- **Modo offline:** Trabaja directamente con el CSV local sin depender del backend  
- **Modo online:** Se conecta al backend FastAPI en tiempo real

---

## 🐳 Despliegue en Producción

Puedes desplegar fácilmente tu dashboard en:

- 🌐 [Streamlit Cloud](https://streamlit.io/cloud) — rápido y gratuito  
- ⚙️ [Render](https://render.com) — ideal para front + back  
- 🚀 [Railway](https://railway.app) — rápido para APIs y dashboards  
- 🐋 Integrado con Docker junto al backend (mediante `docker-compose.yml`)

---

## 📦 Dependencias Principales

| Librería | Uso principal |
|-----------|----------------|
| **streamlit** | Framework de visualización interactiva |
| **plotly** | Gráficas interactivas |
| **pandas** | Manipulación de datos |
| **numpy** | Cálculos numéricos |
| **requests** | Conexión con la API FastAPI |
| **wordcloud** | Nubes de palabras |

---

## 🧩 Estructura Recomendada del Proyecto Completo

```
seminario_complexivo_grupo3/
├─ backend/                    # API en FastAPI (procesamiento y endpoints)
├─ dashboard/                  # Dashboard Streamlit (visualización)
├─ etl/                        # Scripts de limpieza y análisis (analyze.py)
├─ data/                       # Datasets originales y procesados
└─ docs/                       # Documentación técnica y guías
```

---

## ✍️ Autores

**Francisco Javier Quinteros Andrade (FQ)** 
**Matía Marcelo Mosquera Báez (MM)**
**José Xavier Torres Cuenca(JT)**
**Seminario de Analítica con Python — Grupo 3**  
UNIANDES — 2025  

---

> “Los datos cuentan historias; el dashboard las hace visibles.”
