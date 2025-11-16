# Dashboard en Modo Resiliente

## Características

El dashboard está diseñado para **iniciar siempre**, incluso si la API no está disponible.

## Comportamiento

### API Disponible (Modo Normal)

```
┌─────────────────────────────────┐
│ Dashboard inicia                │
├─────────────────────────────────┤
│ Conecta a API                │
│ Carga TODOS los datos        │
│ KPIs con dataset completo    │
│ Filtros habilitados          │
│ Todas las funciones activas  │
└─────────────────────────────────┘
```

**Características:**
- **Todos los datos:** Sin límites, dataset completo
- **Filtros activos:** Hotel, sentimiento, nacionalidad
- **Nubes de palabras:** Generación en tiempo real
- **Análisis completo:** Tópicos, distribuciones, tablas

### API No Disponible (Modo Resiliente)

```
┌─────────────────────────────────┐
│ Dashboard inicia                │
├─────────────────────────────────┤
│ API no responde              │
│ Muestra mensaje informativo  │
│ Filtros deshabilitados       │
│ Espera reconexión            │
└─────────────────────────────────┘
```

**Características:**
- **Dashboard inicia:** No se bloquea
- **Mensaje claro:** Explica por qué no hay datos
- **Instrucciones:** Cómo resolver el problema
- **Render Free Tier:** Info sobre "sleep mode"

## Escenarios Comunes

### Render Free Tier - Servicio Dormido

**Síntoma:**
```
API No Disponible
El servicio está en modo "sleep" (Render Free Tier)
```

**Solución:**
1. Espera 30-60 segundos
2. Recarga la página
3. El servicio despierta automáticamente

**Prevención:**
- Usa Render Paid tier para evitar "sleep"
- Implementa "keep-alive" pings cada 10 min

### Desarrollo Local - API No Iniciada

**Síntoma:**
```
API No Disponible
La API no está corriendo
```

**Solución:**
```bash
# Terminal 1: Iniciar API
python api_app.py

# Terminal 2: Iniciar Dashboard
streamlit run dashboard/app.py
```

### Producción - Error de Red

**Síntoma:**
```
API No Disponible
Problemas de red o configuración
```

**Solución:**
1. Verifica `API_URL` en secrets
2. Prueba acceder a: `{API_URL}/health`
3. Revisa logs de Render

## Configuración

### Timeouts Optimizados

```python
# dashboard/app.py
API_TIMEOUT = 10  # 10 segundos para requests
health_check_timeout = 3  # 3 segundos para health check
```

### Secrets de Streamlit Cloud

```toml
# .streamlit/secrets.toml
API_URL = "https://tu-api.onrender.com"
API_TIMEOUT = 10
```

## Verificación

### Modo Normal (API Online)

```
Dashboard muestra:
{X} reseñas cargadas desde la API
KPIs con datos completos
Filtros habilitados
Estado: API Online
```

### Modo Resiliente (API Offline)

```
Dashboard muestra:
API No Disponible
Instrucciones claras
Filtros deshabilitados (grayed out)
Estado: API Offline
```

## Ventajas

| Ventaja | Descripción |
|---------|-------------|
| **Inicio Rápido** | Dashboard siempre carga, no se bloquea |
| **Resiliente** | Maneja errores de API gracefully |
| **Informativo** | Mensajes claros al usuario |
| **Recuperable** | Simple reload resuelve problemas temporales |
| **Render-Friendly** | Maneja "sleep mode" automáticamente |

## Datos Completos

### Sin Límites

```python
# load_data()
result = get_filtered_reviews_from_api(limit=None)  # SIN LÍMITE

# Aplicar filtros
current_filters = {
    # ...
    "limit": None  # Obtiene TODOS los datos filtrados
}
```

**Garantía:**
- KPIs usan dataset completo
- Filtros consultan todas las reseñas
- Análisis con datos completos
- Nubes de palabras con todos los datos (o muestra de 3k si acelerar está activo)

## Métricas de Rendimiento

| Métrica | Con API | Sin API |
|---------|---------|---------|
| Tiempo de inicio | 5-10s | < 2s |
| Datos cargados | Todos | 0 |
| Funcionalidad | 100% | 0% (modo info) |
| Experiencia usuario | Completa | Informativa |

## Troubleshooting

### Dashboard no carga datos

1. **Verifica estado de API en sidebar:**
   - Online → Problema con datos
   - Offline → Problema con API

2. **Si API Offline:**
   ```bash
   # Prueba manualmente
   curl https://tu-api.onrender.com/health
   ```

3. **Revisa logs:**
   - Streamlit: Terminal donde corre
   - Render: Dashboard → Logs

4. **Verifica secrets:**
   ```toml
   # ¿API_URL es correcto?
   API_URL = "https://..."  # Sin / al final
   ```

---

**Última actualización:** 8 de noviembre de 2025
