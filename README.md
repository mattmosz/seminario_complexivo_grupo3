# 🏨 Análisis de Sentimientos - Reseñas de Hoteles Europeos

**Seminario Complexivo - Grupo 3**

Análisis de Sentimiento y Extracción de Tópicos en Reseñas de Hoteles Europeos usando técnicas de NLP y Machine Learning.

---

## 👥 Integrantes

- Matías Marcelo Mosquera Báez  
- Francisco Javier Quinteros Andrade  
- José Xavier Torres Cuenca

---

## 🎯 Objetivos

Construir un Dashboard interactivo que permita realizar una correcta distribución de sentimientos y facilitar la lectura de reseñas hechas por parte de los clientes a través de la plataforma de booking.com para la identificación de problemas más comunes o aspectos que generan más satisfacción.

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/mattmosz/seminario_complexivo_grupo3.git
cd seminario_complexivo_grupo3

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico

```bash
# Análisis completo del dataset
python main.py

# Prueba rápida con muestra
python main.py --sample 1000

# Con modelado de tópicos
python main.py --topics --n-topics 8

# Modo bajo consumo de RAM
python main.py --stream
```

---

## 📂 Estructura del Proyecto

```
seminario_complexivo_grupo3/
├── main.py                    # 🎯 Script principal
├── data/
│   ├── Hotel_Reviews.csv     # Dataset original
│   └── hotel_reviews_processed.csv
├── scripts/                   # 📦 Módulos de procesamiento
│   ├── data_loader.py        # Carga de datos
│   ├── data_cleaning.py      # Limpieza
│   ├── data_processing.py    # Procesamiento general
│   ├── text_processing.py    # Procesamiento de texto
│   ├── sentiment_analysis.py # Análisis VADER
│   ├── topic_modeling.py     # Modelado LDA
│   └── example_usage.py      # Ejemplos
├── dashboard/                 # 📊 Dashboard web
└── docs/                      # 📖 Documentación
```

---

## 🔄 Pipeline de Procesamiento

El proyecto implementa un pipeline modular dividido en 4 fases:

### Fase 1: 📥 Carga de Datos
- Carga del dataset desde CSV
- Opción de muestreo para pruebas rápidas
- Manejo automático de encoding

### Fase 2: 🧹 Limpieza de Datos
- Validación de tipos de datos
- Manejo de valores faltantes
- Eliminación de duplicados
- Limpieza y combinación de reseñas

### Fase 3: 🔬 Análisis de Sentimientos
- Análisis con VADER (Valence Aware Dictionary)
- Procesamiento por bloques para grandes datasets
- Clasificación: positivo, neutro, negativo
- Modo streaming para bajo consumo de RAM

### Fase 4: 🔍 Modelado de Tópicos (Opcional)
- Extracción de temas con LDA
- Identificación de palabras clave
- Asignación de tópicos dominantes

---

## 💻 Comandos Disponibles

### Opciones Principales

| Comando | Descripción |
|---------|-------------|
| `--sample N` | Usar muestra aleatoria de N filas |
| `--chunk-size N` | Tamaño de bloque para procesamiento |
| `--stream` | Modo streaming (menor uso de RAM) |
| `--topics` | Activar modelado de tópicos |
| `--n-topics N` | Número de tópicos a extraer |
| `--skip-sentiment` | Saltar análisis de sentimientos |

### Ejemplos de Uso

```bash
# Análisis completo con tópicos
python main.py --topics --n-topics 10

# Muestra pequeña para pruebas
python main.py --sample 5000

# Dataset grande con streaming
python main.py --stream --chunk-size 50000

# Solo limpieza de datos
python main.py --skip-sentiment

# Ver ejemplos de cada módulo
python scripts/example_usage.py
```

---

## 📊 Módulos del Proyecto

### 🔵 data_loader.py
Carga de datos desde archivos CSV.

### 🟢 data_cleaning.py
- Limpieza de texto
- Eliminación de duplicados
- Manejo de valores faltantes
- Validación de tipos

### 🟡 data_processing.py
- Operaciones de I/O
- Muestreo de datos
- Estadísticas y resúmenes
- Distribución de sentimientos

### 🟣 text_processing.py
- Normalización de texto
- Combinación de reseñas
- Limpieza de espacios
- Creación de columna unificada

### 🔴 sentiment_analysis.py
- Análisis VADER
- Procesamiento por bloques
- Clasificación de sentimientos
- Modo streaming

### 🟠 topic_modeling.py
- Modelado LDA
- Extracción de tópicos
- Palabras clave
- Asignación de temas

---

## 📈 Dataset

**Fuente:** Reseñas de hoteles europeos de Booking.com

**Características:**
- ~515,000 reseñas
- 1,493 hoteles diferentes
- 6 países europeos
- Reseñas en inglés

**Columnas principales:**
- Hotel_Name, Hotel_Address
- Positive_Review, Negative_Review
- Reviewer_Score, Average_Score
- Reviewer_Nationality
- Tags

**Salida procesada incluye:**
- `review_text`: Texto combinado
- `compound`, `pos`, `neu`, `neg`: Scores VADER
- `sentiment_label`: Clasificación

---

## 📖 Documentación

- 📘 [Guía de Uso](docs/USAGE.md) - Instrucciones detalladas
- 📗 [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md) - Organización del código
- 📙 [Refactorización](docs/REFACTORING.md) - Cambios y mejoras

---

## 🛠️ Requisitos

```
pandas
nltk
scikit-learn
numpy
```

Instalar con:
```bash
pip install -r requirements.txt
```

---

## 🎓 Tecnologías Utilizadas

- **Python 3.8+** - Lenguaje principal
- **Pandas** - Manipulación de datos
- **NLTK** - Procesamiento de lenguaje natural
- **VADER** - Análisis de sentimientos
- **Scikit-learn** - Machine Learning (LDA)
- **Streamlit** - Dashboard interactivo (en desarrollo)

---

## 📊 Dashboard

El proyecto incluye un dashboard interactivo construido con Streamlit que permite:
- Visualizar distribución de sentimientos
- Filtrar por hotel, nacionalidad, puntuación
- Explorar tópicos principales
- Analizar tendencias temporales

```bash
cd dashboard
streamlit run app.py
```

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es parte de un trabajo académico para el Seminario Complexivo.

---

## 📞 Contacto

**Repository:** [github.com/mattmosz/seminario_complexivo_grupo3](https://github.com/mattmosz/seminario_complexivo_grupo3)

---

## ✨ Características Destacadas

- ✅ Pipeline modular y reutilizable
- ✅ Procesamiento eficiente de grandes datasets
- ✅ Modo streaming para bajo consumo de RAM
- ✅ Análisis de sentimientos con VADER
- ✅ Modelado de tópicos con LDA
- ✅ Documentación completa
- ✅ Ejemplos de uso incluidos
- ✅ Dashboard interactivo

---

**Versión:** 2.0  
**Última actualización:** Octubre 2025  