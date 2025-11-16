# Pipeline de Análisis de Sentimientos - Reseñas de Hoteles

Este proyecto implementa un pipeline completo para análisis de sentimientos de reseñas de hoteles, con módulos separados para cada fase del procesamiento.

## Estructura del Proyecto

```
seminario_complexivo_grupo3/
├── main.py                          # Script principal que orquesta el pipeline
├── data/
│   ├── Hotel_Reviews.csv           # Dataset original
│   └── hotel_reviews_processed.csv # Dataset procesado (generado)
├── scripts/
│   ├── data_loader.py              # Carga de datos
│   ├── data_cleaning.py            # Limpieza y preparación
│   ├── data_processing.py          # Procesamiento general
│   ├── text_processing.py          # Procesamiento de texto
│   ├── sentiment_analysis.py       # Análisis de sentimientos (VADER)
│   └── topic_modeling.py           # Modelado de tópicos (LDA)
└── dashboard/                       # Dashboard de visualización
```

## Uso

### Ejecución Básica

Procesar todo el dataset con análisis de sentimientos:

```bash
python main.py
```

### Opciones Avanzadas

**Usar una muestra de datos:**
```bash
python main.py --sample 10000
```

**Modo streaming (menor uso de RAM):**
```bash
python main.py --stream
```

**Incluir modelado de tópicos:**
```bash
python main.py --topics
```

**Especificar número de tópicos:**
```bash
python main.py --topics --n-topics 10
```

**Cambiar tamaño de bloque para procesamiento:**
```bash
python main.py --chunk-size 50000
```

**Solo limpieza de datos (sin sentimientos):**
```bash
python main.py --skip-sentiment
```

**Combinación de opciones:**
```bash
python main.py --sample 50000 --topics --n-topics 8 --chunk-size 10000
```

## Módulos

### 1. `data_loader.py`
Carga de datos desde archivos CSV.

### 2. `data_cleaning.py`
- Limpieza de texto
- Eliminación de duplicados
- Manejo de valores faltantes
- Validación de tipos de datos

### 3. `data_processing.py`
- Carga y guardado de datasets
- Muestreo de datos
- Resúmenes y estadísticas
- Distribución de sentimientos

### 4. `text_processing.py`
- Limpieza de texto individual
- Combinación de reseñas positivas y negativas
- Normalización de espacios y caracteres

### 5. `sentiment_analysis.py`
- Análisis de sentimientos con VADER
- Procesamiento por bloques (chunked)
- Modo streaming para grandes datasets
- Clasificación: positivo, neutro, negativo

### 6. `topic_modeling.py`
- Modelado de tópicos con LDA
- Extracción de palabras clave
- Asignación de tópicos dominantes

## Flujo del Pipeline

1. **Carga de Datos** → Carga el CSV original
2. **Limpieza** → Valida tipos, maneja nulos, elimina duplicados
3. **Procesamiento de Texto** → Limpia y combina reseñas
4. **Análisis de Sentimientos** → Calcula scores VADER y clasifica
5. **Modelado de Tópicos** *(opcional)* → Extrae temas principales
6. **Guardado** → Exporta dataset procesado

## Salida

El archivo procesado `hotel_reviews_processed.csv` contiene:

- Todas las columnas originales
- `review_text`: Texto combinado de reseñas
- `compound`, `pos`, `neu`, `neg`: Scores de VADER
- `sentiment_label`: Clasificación (positivo/neutro/negativo)

## Requisitos

```bash
pip install -r requirements.txt
```

Paquetes principales:
- pandas
- nltk
- scikit-learn

## Ejemplos de Uso

### Análisis Rápido con Muestra
```bash
python main.py --sample 5000 --topics
```

### Procesamiento Completo con Streaming
```bash
python main.py --stream --topics --n-topics 12
```

### Solo Limpieza y Preparación
```bash
python main.py --skip-sentiment
```

## Notas

- El modo `--stream` es recomendado para datasets muy grandes (>1GB)
- El análisis de tópicos puede tardar varios minutos en datasets completos
- Los scores de VADER van de -1 (muy negativo) a +1 (muy positivo)
- La clasificación usa umbrales: <-0.05 = negativo, >0.05 = positivo, resto = neutro
