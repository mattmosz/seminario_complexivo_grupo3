# 🚀 Configuración de Streamlit Cloud - Guía Definitiva

## ⚠️ Problema Resuelto

**Error anterior:**
```
ModuleNotFoundError: import plotly.express as px
Tiempo de despliegue: 2 horas
```

**Causa:** Configuración incorrecta en Streamlit Cloud + carga bloqueante de API

## ✅ Solución Implementada

### 1. Configuración Correcta en Streamlit Cloud

Al crear/editar la app en Streamlit Cloud, usa **EXACTAMENTE** esta configuración:

#### Paso 1: Repositorio
```
Repository: mattmosz/seminario_complexivo_grupo3
Branch: main
```

#### Paso 2: Main file path (CRÍTICO)
```
Main file path: dashboard/app.py
```
⚠️ **IMPORTANTE:** Debe ser `dashboard/app.py`, NO solo `app.py`

#### Paso 3: Python version
```
Python version: 3.11
```

#### Paso 4: Requirements file (OPCIONAL)
Streamlit Cloud busca automáticamente `requirements.txt` en:
1. Misma carpeta que `app.py` → `dashboard/requirements.txt` ✅
2. Raíz del repo → `requirements-dashboard.txt` ✅ (respaldo)

**NO NECESITAS** especificar la ruta, Streamlit Cloud lo detecta automáticamente.

### 2. Secrets Configuration

En Streamlit Cloud, ve a: **App settings → Secrets**

Agrega:
```toml
API_URL = "https://tu-api-render.onrender.com"
API_TIMEOUT = 10
```

⚠️ **IMPORTANTE:** 
- NO incluyas `/` al final de `API_URL`
- Reemplaza `tu-api-render` con tu URL real de Render

### 3. Advanced Settings (Opcional)

Si el despliegue sigue siendo lento:

```
Python version: 3.11
Memory: 1 GB (gratis)
```

## 📋 Checklist Pre-Despliegue

Antes de hacer deploy/redeploy:

- [x] `dashboard/requirements.txt` existe y contiene:
  ```
  streamlit==1.38.0
  plotly==5.24.1
  pandas==2.2.2
  numpy==1.26.4
  requests==2.32.3
  wordcloud==1.9.3
  Pillar==10.4.0
  ```

- [x] `dashboard/app.py` tiene carga resiliente:
  ```python
  check_api_available_fast()  # timeout 1s
  st.session_state.data_loaded  # evita bloqueos
  ```

- [x] `dashboard/.streamlit/config.toml` configurado

- [x] Secrets configurados en Streamlit Cloud

- [x] `API_URL` sin `/` al final

## 🔄 Proceso de Despliegue Esperado

### Streamlit Cloud Build Logs

```
1. Cloning repository...                          (10s)
2. Installing Python 3.11...                      (20s)
3. Installing requirements from dashboard/...     (60s)
   ✅ streamlit
   ✅ plotly
   ✅ pandas
   ✅ numpy
   ✅ requests
   ✅ wordcloud
   ✅ Pillow
4. Starting app...                                (5s)
5. App is live! 🎉                               (Total: ~95s)
```

### Dashboard Startup

```
1. Inicializar session_state                      (0.1s)
2. check_api_available_fast()                     (1s)
   - Si API responde: cargar datos               (+15s)
   - Si API dormida: mostrar botón "Reintentar"  (inmediato)
3. Renderizar UI                                  (0.5s)

Total: 2-17 segundos (dependiendo de API)
```

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: plotly

**Causa:** Requirements no instalados correctamente

**Solución:**
1. Verifica que `Main file path` sea `dashboard/app.py`
2. Verifica que `dashboard/requirements.txt` exista
3. En Streamlit Cloud: **Reboot app** (no solo redeploy)
4. Si persiste: **Delete app** y crear nueva

### Error: App tarda 2+ horas

**Causa:** Código anterior bloqueaba esperando API

**Solución:**
1. ✅ Ya está resuelto con `check_api_available_fast()` (timeout 1s)
2. ✅ Session state evita bloqueos
3. Pull último código de GitHub
4. Redeploy app

### Error: API No Disponible

**Causa:** Render Free Tier dormido (normal)

**Solución:**
1. Dashboard se muestra correctamente (no espera API)
2. Ver mensaje: "⚠️ API No Disponible"
3. Clic en botón "🔄 Reintentar Conexión" después de 1 min
4. API despierta automáticamente

### Build logs muestran errores

**Verificar:**
```bash
# En build logs, buscar:
✅ "Collecting plotly==5.24.1"
✅ "Successfully installed plotly-5.24.1"

# Si dice "No module named plotly":
❌ Requirements no se instalaron → Verificar path
```

## 📊 Métricas Esperadas

| Métrica | Antes | Ahora | Target |
|---------|-------|-------|--------|
| Build time | 2 horas | 90-120s | < 2 min |
| First render | Nunca | 2-17s | < 20s |
| API offline | Bloqueo total | UI + retry | Inmediato |
| ModuleNotFoundError | ✗ | ✓ | 0 errores |

## 🎯 Configuración Final en Streamlit Cloud

Captura de pantalla de configuración correcta:

```
┌─────────────────────────────────────────────────┐
│ App settings                                    │
├─────────────────────────────────────────────────┤
│ General                                         │
│   Repository: mattmosz/seminario_complexivo...  │
│   Branch: main                                  │
│   Main file path: dashboard/app.py          ← ✅│
│   Python version: 3.11                          │
│                                                 │
│ Secrets                                         │
│   API_URL = "https://..."                   ← ✅│
│   API_TIMEOUT = 10                          ← ✅│
│                                                 │
│ Advanced                                        │
│   Memory: 1 GB                                  │
└─────────────────────────────────────────────────┘
```

## 🚦 Pasos para Redeploy

Si la app ya existe en Streamlit Cloud:

1. **Commit y push cambios:**
   ```bash
   git add .
   git commit -m "fix: Optimizar carga resiliente para Streamlit Cloud"
   git push origin main
   ```

2. **En Streamlit Cloud:**
   - Ve a tu app
   - Click en "⋮" (menú)
   - Click en "Reboot app"
   - Espera 90-120 segundos

3. **Verificar:**
   - Build logs sin errores ✅
   - App carga en < 20s ✅
   - No más "ModuleNotFoundError" ✅

Si prefieres empezar de cero:

1. **Delete app** en Streamlit Cloud
2. **New app** con configuración correcta arriba
3. Espera build completo (2-3 min)
4. ✅ Listo!

## 📁 Estructura de Archivos Críticos

```
seminario_complexivo_grupo3/
├── dashboard/
│   ├── app.py                        ← Main file ✅
│   ├── requirements.txt              ← Auto-detectado ✅
│   └── .streamlit/
│       ├── config.toml               ← Configuración UI ✅
│       └── secrets.toml.example      ← Template
├── .streamlit/
│   └── config.toml                   ← Respaldo raíz ✅
└── requirements-dashboard.txt        ← Respaldo raíz ✅
```

## ✅ Verificación Post-Despliegue

Una vez desplegado, verifica:

1. **Build exitoso:**
   - Logs muestran "Your app is live!"
   - No errores de módulos faltantes

2. **Dashboard carga rápido:**
   - UI visible en < 5 segundos
   - Mensaje claro si API offline

3. **Funcionalidad:**
   - Si API online: datos cargan correctamente
   - Si API offline: botón "Reintentar" funciona

4. **Performance:**
   - Filtros responden rápido
   - Sin recargas innecesarias
   - Session state persistente

---

**Última actualización:** 8 de noviembre de 2025

**Resultado esperado:** Dashboard desplegado en **< 2 minutos**, sin errores de módulos, con carga resiliente funcional.
