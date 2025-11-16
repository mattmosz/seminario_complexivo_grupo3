# Estructura del Proyecto - Análisis de Sentimientos

## Árbol de Directorios

```
seminario_complexivo_grupo3/
│
├── main.py                          ← SCRIPT PRINCIPAL (ORQUESTADOR)
├── README.md
├── requirements.txt
│
├── data/
│   ├── Hotel_Reviews.csv          ← Dataset original
│   └── hotel_reviews_processed.csv ← Salida procesada
│
├── scripts/                         ← MÓDULOS DE PROCESAMIENTO
│   ├── data_loader.py              ← Carga de datos
│   ├── data_cleaning.py            ← Limpieza y validación
│   ├── data_processing.py          ← Procesamiento general
│   ├── text_processing.py          ← Procesamiento de texto
│   ├── sentiment_analysis.py       ← Análisis VADER
│   ├── topic_modeling.py           ← Modelado LDA
│   ├── example_usage.py            ← Ejemplos de uso
│   └── analyze_old.py              ← Respaldo (antiguo)
│
├── dashboard/                       ← Dashboard web
│   ├── app.py
│   ├── requirements.txt
│   ├── config/
│   │   └── settings.py
│   └── services/
│       └── api_client.py
│
└── docs/                            ← Documentación
    ├── USAGE.md                    ← Guía de uso
    ├── REFACTORING.md              ← Cambios realizados
    ├── api_endpoints.md
    ├── arquitectura.md
    ├── changelog.md
    ├── deploy_guía.md
    └── modelo_bd.sql
```

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                         PIPELINE DE DATOS                        │
└─────────────────────────────────────────────────────────────────┘

    ENTRADA                          SALIDA
    ┌──────────┐                       ┌──────────┐
    │ Hotel_   │                       │ hotel_   │
    │ Reviews  │                       │ reviews_ │
    │ .csv     │                       │processed │
    └────┬─────┘                       └─────▲────┘
         │                                   │
         ▼                                   │
    ┌────────────────────────────────────────┴────┐
    │                                              │
    │  FASE 1: CARGA                              │
    │  ├─ data_loader.py                          │
    │  └─ data_processing.py                      │
    │                                              │
    ├──────────────────────────────────────────────┤
    │                                              │
    │  FASE 2: LIMPIEZA                           │
    │  ├─ data_cleaning.py                        │
    │  │  ├─ Validar tipos                        │
    │  │  ├─ Manejar nulos                        │
    │  │  └─ Eliminar duplicados                  │
    │  │                                           │
    │  └─ text_processing.py                      │
    │     ├─ Limpiar texto                        │
    │     └─ Combinar reseñas                     │
    │                                              │
    ├──────────────────────────────────────────────┤
    │                                              │
    │  FASE 3: ANÁLISIS DE SENTIMIENTOS           │
    │  └─ sentiment_analysis.py                   │
    │     ├─ Calcular scores VADER                │
    │     └─ Clasificar sentimientos              │
    │                                              │
    ├──────────────────────────────────────────────┤
    │                                              │
    │  FASE 4: TÓPICOS (OPCIONAL)                 │
    │  └─ topic_modeling.py                       │
    │     ├─ Extraer tópicos LDA                  │
    │     └─ Asignar tópicos dominantes           │
    │                                              │
    └──────────────────────────────────────────────┘
```

---

## Responsabilidades de Módulos

### `data_loader.py`
```
Carga datos desde archivos CSV
└─ cargar_datos(path) → DataFrame
```

### `data_cleaning.py`
```
Limpieza y validación de datos
├─ clean_text(text) → str
├─ clean_and_compose_reviews(df) → DataFrame
├─ remove_duplicates(df) → DataFrame
├─ handle_missing_values(df) → DataFrame
└─ validate_data_types(df) → DataFrame
```

### `data_processing.py`
```
Procesamiento general y utilidades
├─ load_dataset(path) → DataFrame
├─ get_sample(df, n) → DataFrame
├─ save_processed_data(df, path)
├─ show_sentiment_distribution(df)
├─ get_data_summary(df)
└─ prepare_output_columns(df) → DataFrame
```

### `text_processing.py`
```
Procesamiento especializado de texto
├─ clean_text(text) → str
├─ compose_review(row) → str
└─ clean_dataframe_reviews(df) → DataFrame
```

### `sentiment_analysis.py`
```
Análisis de sentimientos con VADER
├─ ensure_vader()
├─ analyze_sentiment_batch(texts) → DataFrame
├─ classify_sentiment(score) → str
└─ sentiment_chunked(df, chunk_size, stream_path) → DataFrame
```

### `topic_modeling.py`
```
Modelado de tópicos con LDA
├─ extract_topics(df, n_topics) → list
├─ print_topics(topics)
└─ assign_topics_to_documents(df) → DataFrame
```

---

## Casos de Uso

### Caso 1: Análisis Simple
```bash
python main.py --sample 1000
```
```
┌─────────┐    ┌─────────┐    ┌──────────┐
│ Cargar  │───▶│ Limpiar │───▶│Sentimiento│
└─────────┘    └─────────┘    └──────────┘
```

### Caso 2: Análisis Completo
```bash
python main.py --topics
```
```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│ Cargar  │───▶│ Limpiar │───▶│Sentimiento│───▶│ Tópicos │
└─────────┘    └─────────┘    └──────────┘    └─────────┘
```

### Caso 3: Datasets Grandes
```bash
python main.py --stream --chunk-size 50000
```
```
┌─────────┐    ┌─────────┐    ┌──────────┐
│ Cargar  │───▶│ Limpiar │───▶│Sentimiento│
└─────────┘    └─────────┘    │(Streaming)│
                               └─────┬─────┘
                                     │
                              Escribe incremental
                                     │
                                     ▼
                              ┌──────────┐
                              │   CSV    │
                              └──────────┘
```

### Caso 4: Solo Limpieza
```bash
python main.py --skip-sentiment
```
```
┌─────────┐    ┌─────────┐
│ Cargar  │───▶│ Limpiar │───▶ Guardar
└─────────┘    └─────────┘
```

---

## Columnas del Dataset

### Entrada (Hotel_Reviews.csv)
```
- Hotel_Name
- Hotel_Address
- Reviewer_Nationality
- Positive_Review
- Negative_Review
- Average_Score
- Reviewer_Score
- Tags
- lat
- lng
- ... (otras columnas)
```

### Salida (hotel_reviews_processed.csv)
```
[Columnas originales] +
- review_text          ← Reseñas combinadas
- compound             ← Score VADER (-1 a 1)
- pos                  ← Score positivo
- neu                  ← Score neutro
- neg                  ← Score negativo
- sentiment_label      ← positivo/neutro/negativo
```

---

## Guía Rápida de Inicio

### 1. Instalación
```bash
cd seminario_complexivo_grupo3
pip install -r requirements.txt
```

### 2. Prueba Rápida (1000 filas)
```bash
python main.py --sample 1000
```

### 3. Análisis Completo
```bash
python main.py
```

### 4. Con Tópicos
```bash
python main.py --topics --n-topics 8
```

### 5. Ver Ejemplos
```bash
python scripts/example_usage.py
```

---

## Personalización

### Cambiar Tamaño de Chunk
```bash
python main.py --chunk-size 50000
```

### Cambiar Número de Tópicos
```bash
python main.py --topics --n-topics 12
```

### Modo Bajo Consumo de RAM
```bash
python main.py --stream --sample 10000
```

---

## Soporte

- Documentación: `/docs/USAGE.md`
- Cambios: `/docs/REFACTORING.md`
- Ejemplos: `/scripts/example_usage.py`

---

**Versión:** 2.0  
**Última actualización:** Octubre 2025
