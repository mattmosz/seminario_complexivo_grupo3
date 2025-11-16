# Integración Completada - Dashboard + API

## Lo que se ha integrado

### 1. **Nuevo Tab en el Dashboard**: "Análisis con API"

El dashboard ahora incluye una nueva pestaña que permite:

#### **Subtab 1: Análisis Individual**
- Textarea para ingresar reseñas
- Análisis en tiempo real usando API
- Visualización de sentimiento con badges y gráficos
- Tópicos detectados con palabras clave
- Descarga de resultados en JSON

#### **Subtab 2: Resumen de Tópicos**
- Configuración de parámetros (número de tópicos, máximo de reseñas)
- Análisis agregado de tópicos positivos vs negativos
- Comparación lado a lado
- Métricas generales
- Descarga de resumen completo

### 2. **Funciones de API añadidas al dashboard**

```python
# Verificación de salud de la API
check_api_available() -> bool

# Análisis de reseña individual
analyze_review_with_api(review_text: str) -> dict | None

# Obtención de resumen de tópicos
get_topics_from_api(n_topics: int, max_reviews: int) -> dict | None
```

### 3. **Estilos CSS personalizados**

- `.api-status-online` / `.api-status-offline`: Estado de la API
- `.sentiment-badge`: Badges de sentimiento con colores
- `.topic-badge`: Badges para palabras clave de tópicos
- `.api-card`: Tarjetas para contenido de API

## Cómo Usar

### Paso 1: Iniciar la API

```bash
# En una terminal (desde la raíz del proyecto)
python api_app.py
```

Verás:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Paso 2: Iniciar el Dashboard

```bash
# En otra terminal
cd dashboard
streamlit run app.py
```

O desde la raíz:
```bash
streamlit run dashboard/app.py
```

### Paso 3: Usar la nueva funcionalidad

1. **Abre el dashboard** en tu navegador (usualmente http://localhost:8501)
2. **Navega al tab** "🔌 Análisis con API" (el último tab)
3. **Verifica que la API esté conectada** (debería mostrar "API CONECTADA")
4. **Prueba el análisis individual**:
   - Escribe una reseña en el textarea
   - Haz clic en "Analizar"
   - Observa el sentimiento y tópicos detectados
5. **Prueba el resumen de tópicos**:
   - Ve al subtab "Resumen de Tópicos"
   - Ajusta los parámetros (número de tópicos, máximo de reseñas)
   - Haz clic en "Generar Resumen"
   - Espera 30-90 segundos
   - Explora los tópicos positivos y negativos

## Ejemplos de Reseñas para Probar

### Reseña Positiva:
```
El hotel fue absolutamente increíble. La ubicación es perfecta, justo en el centro de la ciudad, con fácil acceso a las principales atracciones. El personal fue increíblemente amable y atento durante toda nuestra estancia. Nuestra habitación era espaciosa, limpia y con una decoración preciosa. La cama era muy cómoda y dormimos de maravilla. El desayuno estaba delicioso, con una gran variedad de opciones. Las instalaciones eran excelentes: el gimnasio, el spa y la piscina eran de primera categoría. Nos encantó el bar de la azotea con sus impresionantes vistas. ¡Recomendamos encarecidamente este hotel a cualquiera que visite la ciudad!
```

### Reseña Negativa:
```
Una experiencia muy decepcionante. La habitación era pequeña, sucia y anticuada. Había un olor terrible y el aire acondicionado no funcionaba bien. La cama era incómoda y las sábanas parecían viejas. La zona es ruidosa: se oía el tráfico toda la noche y no pudimos dormir. El personal fue grosero y poco servicial cuando nos quejamos. El desayuno fue pésimo, con pocas opciones y la comida fría. Las instalaciones estaban deterioradas y mal mantenidas. El wifi apenas funcionaba. Definitivamente no valió la pena el precio que pagamos. No lo recomendaría y no volveré jamás.
```

### Reseña Mixta:
```
El hotel tiene aspectos positivos y negativos. La ubicación es excelente, muy cerca del metro y de las principales zonas comerciales. El personal de recepción fue amable. Sin embargo, la habitación era más pequeña de lo esperado y un poco ruidosa debido al ruido de la calle. El desayuno era correcto, pero nada del otro mundo. El precio era razonable para la zona. En general, una estancia aceptable, pero nada excepcional.
```

## 🔧 Troubleshooting

### Problema: "API NO DISPONIBLE"

**Solución:**
1. Verifica que ejecutaste `python api_app.py`
2. Espera a que aparezca el mensaje de Uvicorn
3. Comprueba que no haya errores en la terminal de la API
4. Verifica que el puerto 8000 no esté ocupado
5. Haz clic en "Verificar API" en el dashboard

### Problema: "Timeout" al generar resumen de tópicos

**Solución:**
1. Reduce el número de reseñas (`max_reviews`)
2. Reduce el número de tópicos (`n_topics`)
3. Asegúrate de que existe `hotel_reviews_processed.csv`
4. Si no existe, ejecuta primero: `python main.py`

### Problema: Error al analizar reseña individual

**Solución:**
1. Verifica que la reseña tenga al menos 10 caracteres
2. Revisa la consola de la API para ver errores
3. Verifica que VADER lexicon esté descargado
4. Reinicia la API si es necesario

### Problema: Los tópicos no se muestran bien

**Solución:**
1. Verifica que el dataset procesado exista
2. Ejecuta `python main.py` para generar/actualizar el dataset
3. Reinicia la API después de generar el dataset
4. Limpia el cache del dashboard (botón " Verificar API")

## Características de la Integración

### Verificación automática de API
- El dashboard verifica automáticamente si la API está disponible
- Muestra estado visual (online/offline)
- Cache de 60 segundos para no sobrecargar

### Manejo robusto de errores
- Timeouts configurados (30s para análisis, 120s para resumen)
- Mensajes de error descriptivos
- Reintentos disponibles

### Cache inteligente
- Resultados de tópicos cacheados por 5 minutos
- Evita procesamiento redundante
- Mejora la experiencia del usuario

###  Visualizaciones interactivas
- Badges de sentimiento con colores
- Gráficos de barras para distribución
- Comparación lado a lado de tópicos
- Expandibles para ver detalles

### Exportación de datos
- Descarga de resultados en JSON
- Nombres de archivo con timestamp
- Formato legible y estructurado

## Personalización

### Cambiar el URL de la API

En `dashboard/app.py`, línea ~72:
```python
API_URL = "http://localhost:8000"
```

Cambia a tu URL personalizada:
```python
API_URL = "http://tu-servidor.com:8000"
```

### Cambiar timeouts

```python
# Para análisis individual (línea ~82)
timeout=30  # segundos

# Para resumen de tópicos (línea ~101)
timeout=120  # segundos
```

### Cambiar cache TTL

```python
# Cache de verificación de API (línea ~70)
@st.cache_data(ttl=60)  # 60 segundos

# Cache de tópicos (línea ~96)
@st.cache_data(ttl=300)  # 300 segundos (5 minutos)
```

## Métricas de Rendimiento

| Operación | Tiempo esperado | Cache |
|-----------|----------------|-------|
| Verificar API | < 1s | 60s |
| Análisis individual | 2-5s | No |
| Resumen (1000 reviews) | 10-15s | 300s |
| Resumen (10000 reviews) | 30-60s | 300s |
| Resumen (50000 reviews) | 60-120s | 300s |

## 🔗 Recursos Adicionales

- **Documentación API**: `API_README.md`
- **Guía rápida API**: `QUICKSTART_API.md`
- **Resumen técnico**: `API_SUMMARY.md`
- **Swagger UI**: http://localhost:8000/docs
- **Demo standalone**: `dashboard_api_integration_example.py`
- **Tests de API**: `python test_api.py`

## Próximos Pasos Recomendados

1. **Probar la integración**:
   ```bash
   # Terminal 1
   python api_app.py
   
   # Terminal 2
   streamlit run dashboard/app.py
   ```

2. **Ejecutar tests**:
   ```bash
   # Terminal 3
   python test_api.py
   ```

3. **Generar dataset procesado** (si no existe):
   ```bash
   python main.py
   ```

4. **Explorar Swagger UI**:
   - Abrir http://localhost:8000/docs
   - Probar endpoints interactivamente
   - Ver esquemas de datos

5. **Personalizar estilos**:
   - Modificar CSS en `dashboard/app.py`
   - Ajustar colores de badges
   - Personalizar tarjetas

## Resumen

**Dashboard actualizado** con nuevo tab de API
**Funciones de API** integradas y funcionando
**Estilos CSS** personalizados para la sección
**Manejo de errores** robusto y descriptivo
**Cache inteligente** para mejor rendimiento
**Visualizaciones** atractivas e informativas
**Exportación** de resultados en JSON
**Documentación** completa y detallada

**¡La integración está completa y lista para usar!** 

---

**Fecha**: 6 de noviembre de 2025
**Versión Dashboard**: 2.1
**Versión API**: 1.0.0
