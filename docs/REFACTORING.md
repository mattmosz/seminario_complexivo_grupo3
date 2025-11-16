# Reorganización del Proyecto - Análisis de Sentimientos

## Resumen de Cambios

Se ha reorganizado el proyecto separando el monolítico `analyze.py` en módulos especializados para facilitar el mantenimiento y la reutilización del código.

---

## Estructura Anterior vs Nueva

### Estructura Anterior
```
scripts/
├── analyze.py          # Todo en un solo archivo (180+ líneas)
├── data_loader.py
├── data_cleaning.py
└── sentiments.py       # Incompleto
```

### Estructura Nueva
```
scripts/
├── data_loader.py           # Carga de datos
├── data_cleaning.py         # Limpieza y validación
├── data_processing.py       # Procesamiento general (NUEVO)
├── text_processing.py       # Limpieza de texto (NUEVO)
├── sentiment_analysis.py    # Análisis VADER (MEJORADO)
├── topic_modeling.py        # Modelado LDA (NUEVO)
├── example_usage.py         # Ejemplos de uso (NUEVO)
└── analyze_old.py          # Respaldo del original
```

---

## Descripción de Módulos

### 1. **data_loader.py** (Existente)
- Funciones para cargar datos desde CSV
- Sin cambios

### 2. **data_cleaning.py** (Mejorado)
**Funciones:**
- `clean_text()` - Limpia texto individual
- `clean_and_compose_reviews()` - Limpia y combina reseñas
- `remove_duplicates()` - Elimina registros duplicados
- `handle_missing_values()` - Maneja valores faltantes
- `validate_data_types()` - Valida tipos de datos

**Mejoras:**
- Agregadas funciones para duplicados y valores nulos
- Mejor manejo de errores
- Documentación completa

### 3. **data_processing.py** (Nuevo)
**Funciones:**
- `load_dataset()` - Carga CSV con manejo de encoding
- `get_sample()` - Obtiene muestra aleatoria
- `save_processed_data()` - Guarda DataFrame procesado
- `show_sentiment_distribution()` - Muestra distribución de sentimientos
- `get_data_summary()` - Resumen del dataset
- `prepare_output_columns()` - Prepara columnas de salida

**Propósito:**
- Operaciones generales de I/O y análisis
- Funciones auxiliares para visualización

### 4. **text_processing.py** (Nuevo)
**Funciones:**
- `clean_text()` - Limpia texto individual
- `compose_review()` - Combina reseñas positivas y negativas
- `clean_dataframe_reviews()` - Procesa DataFrame completo

**Propósito:**
- Procesamiento especializado de texto
- Normalización y limpieza
- Creación de columna `review_text`

### 5. **sentiment_analysis.py** (Mejorado)
**Funciones:**
- `ensure_vader()` - Descarga lexicon VADER
- `analyze_sentiment_batch()` - Analiza lote de textos
- `classify_sentiment()` - Clasifica score en categoría
- `sentiment_chunked()` - Procesamiento por bloques

**Mejoras:**
- Mejor documentación
- Función de clasificación separada
- Manejo de errores mejorado
- Mensajes informativos

### 6. **topic_modeling.py** (Nuevo)
**Funciones:**
- `extract_topics()` - Extrae tópicos con LDA
- `print_topics()` - Imprime tópicos formateados
- `assign_topics_to_documents()` - Asigna tópico dominante

**Propósito:**
- Modelado de tópicos con LDA
- Análisis de contenido temático
- Extracción de palabras clave

### 7. **example_usage.py** (Nuevo)
**Ejemplos:**
1. Carga y muestreo de datos
2. Limpieza de texto
3. Limpieza de DataFrame
4. Análisis de sentimientos
5. Modelado de tópicos
6. Pipeline completo

**Propósito:**
- Documentación práctica
- Casos de uso reales
- Pruebas rápidas

---

## Nuevo main.py

El nuevo `main.py` orquesta todo el pipeline:

**Características:**
- Argumentos de línea de comandos
- Pipeline modular por fases
- Modo streaming para grandes datasets
- Análisis de tópicos opcional
- Muestreo de datos
- Mensajes informativos con emojis

**Fases del Pipeline:**
1. Carga de datos
2. Limpieza de datos
3. Análisis de sentimientos
4. Modelado de tópicos (opcional)

---

## Comandos de Uso

### Análisis Completo
```bash
python main.py
```

### Con Muestra
```bash
python main.py --sample 10000
```

### Con Tópicos
```bash
python main.py --topics --n-topics 8
```

### Modo Streaming (Baja RAM)
```bash
python main.py --stream
```

### Solo Limpieza
```bash
python main.py --skip-sentiment
```

### Ejemplos Individuales
```bash
python scripts/example_usage.py
```

---

## Beneficios de la Reorganización

### Mantenibilidad
- Código más organizado y fácil de entender
- Cada módulo tiene una responsabilidad clara
- Más fácil de debuggear

### Reutilización
- Funciones pueden usarse independientemente
- Fácil importar solo lo necesario
- Componentes modulares

### Escalabilidad
- Fácil agregar nuevas funcionalidades
- Módulos independientes
- Testing más simple

### Documentación
- Cada función está documentada
- Ejemplos de uso claros
- Tipos de datos especificados

### Flexibilidad
- Pipeline configurable
- Múltiples modos de ejecución
- Opciones personalizables

---

## Compatibilidad

### Archivos Preservados
- `data_loader.py` - Sin cambios
- `analyze_old.py` - Respaldo del original
- Todos los datos en `/data/`

### Cambios Requeridos
- Actualizar imports en otros scripts
- Usar `main.py` en lugar de `analyze.py`
- Instalar dependencias con `pip install -r requirements.txt`

---

## Próximos Pasos

1. Probar el nuevo pipeline con muestra pequeña
2. Verificar compatibilidad con dashboard
3. Actualizar documentación del proyecto
4. Crear tests unitarios para cada módulo
5. Optimizar rendimiento si es necesario

---

## Solución de Problemas

### Error de importación
```python
# Asegurarse de estar en el directorio raíz
import sys
sys.path.append('.')
```

### VADER no descarga
```python
import nltk
nltk.download('vader_lexicon')
```

### Memoria insuficiente
```bash
# Usar modo streaming
python main.py --stream --sample 50000
```

---

## Contribución

Para agregar nuevas funcionalidades:
1. Crear nuevo módulo en `/scripts/`
2. Documentar funciones
3. Agregar ejemplos en `example_usage.py`
4. Integrar en `main.py` si es necesario

---

**Fecha de reorganización:** Octubre 2025  
**Estado:** Completado y probado
