# Script de Prueba - Sistema Completo

Este documento contiene los comandos exactos para probar el sistema completo.

## Pre-requisitos

```powershell
# Verificar Python
python --version  # Debe ser 3.8+

# Verificar dependencias
pip list | Select-String -Pattern "fastapi|streamlit|pandas|uvicorn"
```

Si falta alguna dependencia:
```powershell
pip install -r requirements.txt
pip install -r dashboard/requirements.txt
```

---

## Paso 1: Iniciar Backend API

### Abrir Terminal 1 (PowerShell):

```powershell
# Navegar a la raíz del proyecto
cd c:\Users\MSi\Documents\SOFTWARE\SEMINARIO\seminario_complexivo_grupo3

# Iniciar API
python api_app.py
```

**Resultado esperado:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Mantén esta terminal abierta**

---

## Paso 2: Probar API (Opcional pero recomendado)

### Abrir Terminal 2 (PowerShell):

```powershell
# Test 1: Health check
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET | Select-Object -ExpandProperty Content

# Test 2: Stats del dataset
Invoke-WebRequest -Uri "http://localhost:8000/stats" -Method GET | Select-Object -ExpandProperty Content

# Test 3: Lista de hoteles
Invoke-WebRequest -Uri "http://localhost:8000/hotels" -Method GET | Select-Object -ExpandProperty Content

# Test 4: Filtrar reseñas (ejemplo: hoteles específicos)
$body = @{
    hotels = @("Britannia International Hotel Canary Wharf")
    min_score = 8.0
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/reviews/filter" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Resultados esperados:**
- Health: `{"status":"healthy", "dataset_loaded":true, ...}`
- Stats: `{"total_reviews": XXXXX, "columns": [...], ...}`
- Hotels: `["Hotel A", "Hotel B", ...]`
- Filter: JSON con reseñas filtradas

---

## Paso 3: Iniciar Dashboard

### En la misma Terminal 2 (o abrir Terminal 3):

```powershell
# Navegar a la raíz del proyecto
cd c:\Users\MSi\Documents\SOFTWARE\SEMINARIO\seminario_complexivo_grupo3

# Iniciar dashboard
streamlit run dashboard/app.py
```

**Resultado esperado:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

El navegador se abrirá automáticamente en http://localhost:8501

**Dashboard está corriendo**

---

## Paso 4: Verificar Integración

### En el Dashboard (navegador):

1. **Verificar Conexión API**:
   - En la parte superior derecha del dashboard
   - Debe aparecer: ** API CONECTADA** (en verde)
   - Si aparece rojo , la API no está accesible

2. **Probar Carga de Datos**:
   - El dashboard debería cargar automáticamente
   - Deberías ver métricas en la parte superior
   - Ejemplo: "Total de Reseñas: XXX,XXX"

3. **Probar Filtros (Sidebar)**:
   - Abre el sidebar (flecha en la esquina superior izquierda)
   - Selecciona un hotel específico
   - Selecciona una nacionalidad
   - Las métricas deberían actualizarse

4. **Probar Tabs**:
   - **Análisis General**: Gráficos de distribución, top hoteles
   - **Geografía**: Mapas y análisis por país
   - **Palabras Clave**: Word clouds (puede tardar unos segundos)
   - **Datos Detallados**: Tabla con reseñas filtradas
   - **Sentimiento**: Análisis detallado (si VADER está activo)
   - **Análisis con API**: Análisis de reseñas individuales

5. **Probar Word Clouds**:
   - Ve al tab "Palabras Clave"
   - Espera a que se generen las nubes (puede tardar 10-30 segundos)
   - Deberías ver dos word clouds: positivo y negativo

6. **Probar Análisis Individual** (Tab API):
   - Ve al tab "🔌 Análisis con API"
   - Debe aparecer **API CONECTADA**
   - Sub-tab "🔍 Análisis Individual":
     - Selecciona un hotel
     - Selecciona una reseña
     - Haz clic en "Analizar con API"
     - Espera el resultado (5-15 segundos)
     - Deberías ver sentimiento y tópicos

7. **Probar Resumen de Tópicos** (Tab API):
   - Ve al sub-tab "Resumen de Tópicos"
   - Ajusta número de tópicos (ej: 8)
   - Ajusta máximo de reseñas (ej: 10,000)
   - Haz clic en "Generar Resumen"
   - Espera el resultado (30-90 segundos)
   - Deberías ver tópicos positivos y negativos

---

## Monitoreo de Logs

### Terminal 1 (API):
Deberías ver logs de las peticiones:
```
INFO:     127.0.0.1:XXXXX - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "POST /reviews/filter HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "POST /reviews/wordcloud HTTP/1.1" 200 OK
```

### Terminal 2/3 (Dashboard):
Streamlit mostrará mensajes cuando recarga:
```
2025-01-XX XX:XX:XX.XXX 
Rerun triggered
```

---

## Tests de Funcionalidad Específicos

### Test 1: Filtrado Funciona
1. Sidebar → Selecciona 1 hotel específico
2. Revisa el número en "Total de Reseñas Filtradas"
3. Debe ser menor que el total original
4. Tab "Datos Detallados" → Solo debe mostrar ese hotel

### Test 2: Word Clouds Usan API
1. Tab "Palabras Clave"
2. Ajusta filtros (ej: solo hoteles de 5 estrellas)
3. Word clouds deberían regenerarse
4. Terminal API debe mostrar: `POST /reviews/wordcloud`

### Test 3: Análisis Individual Funciona
1. Tab "Análisis con API"
2. Selecciona una reseña
3. "Analizar con API"
4. Terminal API debe mostrar: `POST /reviews/analyze`
5. Dashboard debe mostrar: sentimiento + tópicos

### Test 4: Tópicos Agregados Funcionan
1. Tab "Análisis con API" → Sub-tab "Resumen de Tópicos"
2. "Generar Resumen"
3. Terminal API debe mostrar: `POST /reviews/topics`
4. Dashboard debe mostrar dos columnas: positivos y negativos

### Test 5: Cache Funciona
1. Haz clic en "Aplicar Filtros" varias veces
2. Primera vez: puede tardar 1-2 segundos
3. Siguientes veces: debe ser instantáneo (< 0.5s)
4. Terminal API: Solo debe procesar la primera vez

---

## Métricas de Performance Esperadas

| Operación | Tiempo Esperado | Nota |
|-----------|----------------|------|
| Health Check | < 100ms | Cache 60s |
| Get Stats | < 200ms | Cache 5min |
| Get Hotels/Nationalities | < 100ms | Cache 5min |
| Filter Reviews (primera vez) | 1-3s | Depende de filtros |
| Filter Reviews (cache) | < 100ms | Dentro de 5min |
| Word Cloud | 10-30s | Depende de sample_size |
| Análisis Individual | 5-15s | Procesamiento NLP |
| Resumen Tópicos (10k reviews) | 30-90s | LDA + múltiples documentos |

---

## Detener Servicios

### Detener API (Terminal 1):
```
CTRL + C
```

### Detener Dashboard (Terminal 2/3):
```
CTRL + C
```

---

## Checklist de Validación

Marca cada item después de probarlo:

- [ ] API inicia sin errores
- [ ] Health check responde correctamente
- [ ] Dashboard inicia sin errores
- [ ] Dashboard muestra "API CONECTADA"
- [ ] Métricas se cargan en la página principal
- [ ] Filtros en sidebar funcionan
- [ ] Métricas se actualizan al filtrar
- [ ] Tab "Análisis General" muestra gráficos
- [ ] Tab "Geografía" muestra mapas
- [ ] Tab "Palabras Clave" genera word clouds
- [ ] Tab "Datos Detallados" muestra tabla
- [ ] Tab "Sentimiento" muestra análisis (si VADER activo)
- [ ] Tab "Análisis con API" - Análisis individual funciona
- [ ] Tab "Análisis con API" - Resumen de tópicos funciona
- [ ] Terminal API muestra logs de peticiones
- [ ] Cache funciona (segundas peticiones son rápidas)
- [ ] No hay errores en ninguna terminal

---

## Problemas Comunes

### "ModuleNotFoundError: No module named 'fastapi'"
```powershell
pip install fastapi uvicorn[standard]
```

### "Address already in use" (Puerto 8000)
```powershell
# Ver qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# Matar el proceso (reemplaza XXXXX con el PID del comando anterior)
taskkill /PID XXXXX /F

# O cambiar puerto en api_app.py
```

### Dashboard muestra "API NO DISPONIBLE"
1. Verifica que la API esté corriendo (Terminal 1)
2. Prueba http://localhost:8000/health en el navegador
3. Haz clic en "Verificar API" en el dashboard

### "FileNotFoundError: data/Hotel_Reviews.csv"
```powershell
# Verificar que el archivo existe
Test-Path .\data\Hotel_Reviews.csv
Test-Path .\data\hotel_reviews_processed.csv

# Si falta, asegúrate de estar en la carpeta correcta
```

---

##  Registro de Pruebas

Fecha: _______________

| Test | Estado | Tiempo | Notas |
|------|--------|--------|-------|
| API inicia | X | | |
| Health check | X | | |
| Dashboard inicia | X | | |
| Conexión API | X | | |
| Filtros | X | | |
| Word clouds | X | | |
| Análisis individual | X | | |
| Resumen tópicos | X | | |
| Performance | X | | |

**Estado**:  |  Con problemas | Falló

---

**¡Éxito!** Si todos los tests pasan, el sistema está funcionando correctamente. 
