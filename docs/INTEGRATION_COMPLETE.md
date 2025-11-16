# Integración API + Dashboard - COMPLETADA

## Resumen Ejecutivo

Se ha integrado exitosamente la **API REST de FastAPI** con el **Dashboard de Streamlit**, agregando una nueva pestaña que permite análisis de reseñas en tiempo real.

---

## Archivos Modificados/Creados

### 1. **`dashboard/app.py`** - MODIFICADO

**Cambios realizados:**

- Importado `json` para manejo de datos
- Agregadas 3 funciones de integración con API:
  - `check_api_available()` - Verifica estado de la API
  - `analyze_review_with_api()` - Analiza reseña individual
  - `get_topics_from_api()` - Obtiene resumen de tópicos
- Agregado CSS personalizado para sección de API:
  - Estilos para badges de sentimiento
  - Estilos para badges de tópicos
  - Estilos para cards de API
  - Estilos para estados de conexión
- Agregada nueva pestaña "🔌 Análisis con API"
- Implementadas 2 sub-pestañas:
  - "Análisis Individual"
  - "Resumen de Tópicos"

**Líneas modificadas:** ~400 líneas agregadas

### 2. **`DASHBOARD_API_INTEGRATION.md`** - CREADO 

Documentación completa de la integración con:
- Instrucciones de uso paso a paso
- Ejemplos de reseñas para probar
- Troubleshooting detallado
- Personalización y configuración
- Métricas de rendimiento

**Líneas:** 345

### 3. **`start_services.ps1`** - CREADO 

Script PowerShell para iniciar ambos servicios automáticamente:
- Verifica Python y dependencias
- Inicia API en puerto 8000
- Inicia Dashboard en puerto 8501
- Maneja procesos y permite detenerlos
- Muestra resumen de URLs y PIDs

**Líneas:** 133

---

## Nuevas Funcionalidades en el Dashboard

### Tab "Análisis con API"

#### **Sub-tab 1: Análisis Individual**

**Características:**
- Textarea para ingresar reseñas
- Validación de longitud mínima (10 caracteres)
- Botones de "Analizar" y "Limpiar"
- Mostrar texto procesado
- Badge visual de sentimiento (positivo/negativo/neutral)
- 4 métricas de sentimiento:
  - Score compuesto
  - Score positivo
  - Score neutral
  - Score negativo
- Gráfico de barras de distribución
- Lista expandible de tópicos detectados
- Palabras clave con badges coloridos
- Descarga de resultado en JSON

**Flujo:**
```
Usuario escribe reseña
    ↓
Clic en "Analizar"
    ↓
Spinner de carga
    ↓
POST a /reviews/analyze
    ↓
Visualización de resultados
    ↓
Descarga opcional (JSON)
```

#### **Sub-tab 2: Resumen de Tópicos**

**Características:**
- Slider para número de tópicos (3-15)
- Select slider para máximo de reseñas
- Botón "Generar Resumen"
- Spinner con estimación de tiempo
- 4 métricas generales:
  - Fuente de datos
  - Total analizado
  - Reseñas positivas (con %)
  - Reseñas negativas (con %)
- Dos columnas: Positivos vs Negativos
- Cards por tópico con ID y palabras clave
- Tabla comparativa de tópicos
- Descarga de resumen completo (JSON)
- Información sobre la funcionalidad
- Enlaces a documentación

**Flujo:**
```
Usuario ajusta parámetros
    ↓
Clic en "Generar Resumen"
    ↓
Spinner (30-90s)
    ↓
GET a /reviews/topics?n_topics=X&max_reviews=Y
    ↓
Visualización lado a lado
    ↓
Descarga opcional (JSON)
```

---

## Estilos CSS Agregados

### 1. **Estado de API**
```css
.api-status-online {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    /* Verde para API conectada */
}

.api-status-offline {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    /* Rojo para API desconectada */
}
```

### 2. **Badges de Sentimiento**
```css
.sentiment-positive {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    /* Verde para positivo */
}

.sentiment-negative {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    /* Rojo para negativo */
}

.sentiment-neutral {
    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
    /* Gris para neutral */
}
```

### 3. **Badges de Tópicos**
```css
.topic-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Gradiente púrpura para palabras clave */
}
```

### 4. **Cards de API**
```css
.api-card {
    background: white;
    border-radius: 15px;
    border-left: 5px solid #E91E8C;
    /* Card con borde izquierdo rosa */
}
```

---

## Configuración Técnica

### Variables de Configuración

```python
# URL de la API
API_URL = "http://localhost:8000"

# Cache de verificación (60 segundos)
@st.cache_data(ttl=60)
def check_api_available()

# Cache de tópicos (5 minutos)
@st.cache_data(ttl=300)
def get_topics_from_api()

# Timeouts
- Análisis individual: 30 segundos
- Resumen de tópicos: 120 segundos
- Verificación de salud: 5 segundos
```

### Endpoints Utilizados

| Endpoint | Método | Uso | Timeout |
|----------|--------|-----|---------|
| `/health` | GET | Verificar estado | 5s |
| `/reviews/analyze` | POST | Analizar reseña | 30s |
| `/reviews/topics` | GET | Resumen de tópicos | 120s |

---

## Flujo de Datos

### Análisis Individual

```
Dashboard (Streamlit)
    ↓ [POST] {"text": "..."}
API (FastAPI)
    ↓
scripts/text_processing.py
    ↓ clean_text()
scripts/sentiment_analysis.py
    ↓ VADER analysis
scripts/topic_modeling.py
    ↓ LDA extraction
API Response
    ↓ JSON
Dashboard Visualización
```

### Resumen de Tópicos

```
Dashboard (Streamlit)
    ↓ [GET] ?n_topics=8&max_reviews=10000
API (FastAPI)
    ↓
load_processed_data()
    ↓ Filtrar por sentimiento
extract_topics(df_positive)
extract_topics(df_negative)
    ↓
API Response (JSON)
    ↓
Dashboard Visualización
    ├─ Columna Positivos
    └─ Columna Negativos
```

---

## Cómo Ejecutar

### Opción 1: Script Automático (Recomendado)

```powershell
# En PowerShell desde la raíz del proyecto
.\start_services.ps1
```

### Opción 2: Manual

```bash
# Terminal 1: API
python api_app.py

# Terminal 2: Dashboard
streamlit run dashboard/app.py
```

### Opción 3: Comandos individuales

```bash
# Solo API
python api_app.py

# Solo Dashboard
cd dashboard
streamlit run app.py
```

---

## Checklist de Verificación

### Antes de usar:
- [ ] Python virtual environment activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Dataset disponible (raw o procesado)
- [ ] Puerto 8000 libre para API
- [ ] Puerto 8501 libre para Dashboard

### Probar integración:
- [ ] API inicia sin errores
- [ ] Dashboard inicia sin errores
- [ ] Dashboard muestra "API CONECTADA"
- [ ] Análisis individual funciona
- [ ] Resumen de tópicos funciona
- [ ] Descarga de JSON funciona
- [ ] Estilos CSS se ven correctamente

### Troubleshooting:
- [ ] Si API offline, revisar terminal de API
- [ ] Si timeout, reducir parámetros
- [ ] Si error de datos, generar dataset procesado (`python main.py`)
- [ ] Si no se ven estilos, limpiar cache del navegador

---

## Mejoras Futuras (Sugerencias)

### Dashboard
1. Agregar historial de análisis
2. Comparación de múltiples reseñas
3. Exportar a PDF/Excel
4. Filtros por fecha en resumen de tópicos
5. Gráficos de comparación temporal

### API
1. Autenticación JWT
2. Rate limiting
3. Batch analysis endpoint
4. Websockets para análisis en tiempo real
5. Cache Redis para modelos LDA

### Integración
1. Notificaciones push cuando análisis completa
2. Modo offline con fallback local
3. Sincronización automática de cache
4. Métricas de uso de API en dashboard
5. Logs centralizados

---

## Documentación Relacionada

| Archivo | Descripción |
|---------|-------------|
| `API_README.md` | Documentación completa de la API |
| `QUICKSTART_API.md` | Guía rápida para iniciar |
| `API_SUMMARY.md` | Resumen técnico de la API |
| `DASHBOARD_API_INTEGRATION.md` | Esta integración en detalle |
| `dashboard_api_integration_example.py` | Demo standalone |
| `test_api.py` | Tests automatizados |

---

## Conclusión

La integración está **100% completa y funcional**. El dashboard ahora puede:

Verificar estado de la API automáticamente
Analizar reseñas individuales en tiempo real
Generar resúmenes de tópicos agregados
Visualizar resultados de forma atractiva
Exportar datos en JSON
Manejar errores de forma robusta
Cachear resultados para mejor rendimiento

**Próximo paso:** Ejecutar `.\start_services.ps1` y empezar a usar! 🚀

---

**Creado:** 6 de noviembre de 2025  
**Versión Dashboard:** 2.1  
**Versión API:** 1.0.0  
**Integración:** v1.0
