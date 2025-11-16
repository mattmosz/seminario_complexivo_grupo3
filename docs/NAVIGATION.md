# Mapa de Navegación - Módulos del Proyecto

## ¿Qué quieres hacer?

---

## CARGAR DATOS

### Necesito: Cargar un CSV

**Módulo:** `data_processing.py`

```python
from scripts.data_processing import load_dataset

df = load_dataset("data/Hotel_Reviews.csv")
```

**Alternativa:** `data_loader.py`

```python
from scripts.data_loader import cargar_datos

df = cargar_datos("data/Hotel_Reviews.csv")
```

---

## LIMPIAR DATOS

### Necesito: Limpiar texto individual

**Módulo:** `text_processing.py`

```python
from scripts.text_processing import clean_text

texto_limpio = clean_text("  No Positive   Texto sucio  ")
```

### Necesito: Limpiar todo el DataFrame

**Módulo:** `data_cleaning.py`

```python
from scripts.data_cleaning import clean_and_compose_reviews

df_limpio = clean_and_compose_reviews(df)
```

### Necesito: Eliminar duplicados

**Módulo:** `data_cleaning.py`

```python
from scripts.data_cleaning import remove_duplicates

df_sin_duplicados = remove_duplicates(df)
```

### Necesito: Manejar valores nulos

**Módulo:** `data_cleaning.py`

```python
from scripts.data_cleaning import handle_missing_values

df_completo = handle_missing_values(df)
```

---

## PROCESAR TEXTO

### Necesito: Combinar reseñas positivas y negativas

**Módulo:** `text_processing.py`

```python
from scripts.text_processing import clean_dataframe_reviews

df_con_texto = clean_dataframe_reviews(df)
# Crea columna 'review_text'
```

### Necesito: Procesar una fila individual

**Módulo:** `text_processing.py`

```python
from scripts.text_processing import compose_review

texto = compose_review(df.iloc[0])
```

---

## ANÁLISIS DE SENTIMIENTOS

### Necesito: Analizar sentimientos de textos

**Módulo:** `sentiment_analysis.py`

```python
from scripts.sentiment_analysis import analyze_sentiment_batch

scores = analyze_sentiment_batch(df['review_text'])
# Retorna: compound, pos, neu, neg
```

### Necesito: Clasificar un score en categoría

**Módulo:** `sentiment_analysis.py`

```python
from scripts.sentiment_analysis import classify_sentiment

categoria = classify_sentiment(0.7)  # "positivo"
categoria = classify_sentiment(-0.3) # "negativo"
categoria = classify_sentiment(0.0)  # "neutro"
```

### Necesito: Procesar dataset completo con chunks

**Módulo:** `sentiment_analysis.py`

```python
from scripts.sentiment_analysis import sentiment_chunked

df_analizado = sentiment_chunked(
    df, 
    chunk_size=100_000,
    stream_path=None  # O Path para streaming
)
```

---

## MODELADO DE TÓPICOS

### Necesito: Extraer tópicos principales

**Módulo:** `topic_modeling.py`

```python
from scripts.topic_modeling import extract_topics, print_topics

topics = extract_topics(df, n_topics=8)
print_topics(topics)
```

### Necesito: Asignar tópico a cada documento

**Módulo:** `topic_modeling.py`

```python
from scripts.topic_modeling import assign_topics_to_documents

df_con_topics = assign_topics_to_documents(df, n_topics=8)
# Agrega columnas: dominant_topic, topic_probability
```

---

## ANÁLISIS Y ESTADÍSTICAS

### Necesito: Ver resumen del dataset

**Módulo:** `data_processing.py`

```python
from scripts.data_processing import get_data_summary

get_data_summary(df)
```

### Necesito: Ver distribución de sentimientos

**Módulo:** `data_processing.py`

```python
from scripts.data_processing import show_sentiment_distribution

show_sentiment_distribution(df)
```

### Necesito: Obtener una muestra aleatoria

**Módulo:** `data_processing.py`

```python
from scripts.data_processing import get_sample

df_muestra = get_sample(df, n=1000)
```

---

## GUARDAR RESULTADOS

### Necesito: Guardar DataFrame procesado

**Módulo:** `data_processing.py`

```python
from scripts.data_processing import save_processed_data

save_processed_data(df, "data/output.csv")
```

---

## PIPELINE COMPLETO

### Necesito: Ejecutar todo el flujo

**Opción 1: Usar main.py (Recomendado)**

```bash
python main.py --sample 1000 --topics
```

**Opción 2: Pipeline manual**

```python
# 1. Cargar
from scripts.data_processing import load_dataset, save_processed_data
df = load_dataset("data/Hotel_Reviews.csv")

# 2. Limpiar
from scripts.data_cleaning import clean_and_compose_reviews, remove_duplicates
df = remove_duplicates(df)
df = clean_and_compose_reviews(df)

# 3. Procesar texto
from scripts.text_processing import clean_dataframe_reviews
df = clean_dataframe_reviews(df)

# 4. Sentimientos
from scripts.sentiment_analysis import sentiment_chunked
df = sentiment_chunked(df, chunk_size=50_000)

# 5. Tópicos (opcional)
from scripts.topic_modeling import extract_topics
topics = extract_topics(df, n_topics=8)

# 6. Guardar
save_processed_data(df, "data/output.csv")
```

---

## EJEMPLOS Y APRENDIZAJE

### Necesito: Ver ejemplos de uso

**Módulo:** `example_usage.py`

```bash
python scripts/example_usage.py
```

**O ejecutar ejemplos individuales:**

```python
from scripts.example_usage import (
    example_1_load_and_sample,
    example_2_text_cleaning,
    example_3_dataframe_cleaning,
    example_4_sentiment_analysis,
    example_5_topic_modeling,
    example_6_full_pipeline
)

# Ejecutar el ejemplo que necesites
example_4_sentiment_analysis()
```

---

## DOCUMENTACIÓN

### Necesito: Guía de uso completa
`docs/USAGE.md`

### Necesito: Entender la estructura
`docs/PROJECT_STRUCTURE.md`

### Necesito: Ver los cambios realizados
`docs/REFACTORING.md`

### Necesito: Resumen ejecutivo
 `docs/SUMMARY.md`

---

## CASOS DE USO COMUNES

### Caso 1: Análisis Rápido
```bash
python main.py --sample 1000
```

### Caso 2: Análisis Completo
```bash
python main.py --topics
```

### Caso 3: Dataset Grande (Baja RAM)
```bash
python main.py --stream --chunk-size 50000
```

### Caso 4: Solo Limpieza
```bash
python main.py --skip-sentiment
```

### Caso 5: Experimentar con Código
```python
# Usa example_usage.py como plantilla
python scripts/example_usage.py
```

---

## Flujo de Decisión

```
┌─────────────────────────────────────┐
│ ¿Qué necesitas hacer?              │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌──────────┐
│Análisis│ │Limpiar│ │Procesar  │
│completo│ │ datos │ │parte del │
│        │ │       │ │pipeline  │
└───┬────┘ └───┬───┘ └────┬─────┘
    │          │          │
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐
│main.py │ │data_ │ │Importar  │
│        │ │clean.│ │módulos   │
│        │ │py    │ │específicos│
└────────┘ └──────┘ └──────────┘
```

---

## Ayuda Rápida

### No sé qué módulo usar
→ Lee `docs/PROJECT_STRUCTURE.md`

### No sé cómo usar un módulo
→ Lee `docs/USAGE.md` o ejecuta `example_usage.py`

### Quiero ver todos los argumentos
```bash
python main.py --help
```

### Tengo poco tiempo
```bash
python main.py --sample 100
```

### Tengo poca RAM
```bash
python main.py --stream --sample 5000
```

### Quiero entender el código
→ Cada módulo está documentado con docstrings

---

## Referencia Rápida

| Tarea | Módulo | Función |
|-------|--------|---------|
| Cargar CSV | data_processing | `load_dataset()` |
| Limpiar texto | text_processing | `clean_text()` |
| Combinar reseñas | text_processing | `clean_dataframe_reviews()` |
| Sentimientos | sentiment_analysis | `sentiment_chunked()` |
| Tópicos | topic_modeling | `extract_topics()` |
| Guardar CSV | data_processing | `save_processed_data()` |
| Muestra | data_processing | `get_sample()` |
| Duplicados | data_cleaning | `remove_duplicates()` |
| Pipeline | main | `python main.py` |
| Ejemplos | example_usage | `python scripts/example_usage.py` |

---

**Tip:** Empieza siempre con una muestra pequeña para probar

```bash
python main.py --sample 100
```

Luego escala según necesites!
