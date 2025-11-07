import pandas as pd
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Agregar el directorio de scripts al path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

# Importar módulos del pipeline
from text_processing import clean_text
from sentiment_analysis import ensure_vader, analyze_sentiment_batch, classify_sentiment
from topic_modeling import extract_topics, get_extended_stop_words


# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reviews Analysis API",
    description="API para análisis de sentimientos y tópicos en reseñas de hoteles",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic
class ReviewInput(BaseModel):
    """Modelo para recibir una reseña a analizar"""
    text: str = Field(..., min_length=10, description="Texto de la reseña a analizar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The hotel was amazing! The staff was very friendly and the room was clean. Location is perfect."
            }
        }

class SentimentResult(BaseModel):
    """Resultado del análisis de sentimiento"""
    sentiment: str = Field(..., description="Clasificación del sentimiento: positivo, negativo, neutro")
    compound_score: float = Field(..., description="Score compuesto VADER (-1 a 1)")
    positive_score: float = Field(..., description="Score positivo (0 a 1)")
    negative_score: float = Field(..., description="Score negativo (0 a 1)")
    neutral_score: float = Field(..., description="Score neutral (0 a 1)")

class TopicResult(BaseModel):
    """Tópico detectado con sus palabras clave"""
    topic_id: int = Field(..., description="Identificador del tópico")
    keywords: str = Field(..., description="Palabras clave del tópico separadas por comas")

class AnalyzeResponse(BaseModel):
    """Respuesta completa del análisis de una reseña"""
    cleaned_text: str = Field(..., description="Texto limpio de la reseña")
    sentiment: SentimentResult
    topics: List[TopicResult]

class TopicSummary(BaseModel):
    """Resumen de tópicos por tipo de sentimiento"""
    sentiment_type: str = Field(..., description="Tipo de sentimiento: positivo o negativo")
    total_reviews: int = Field(..., description="Total de reseñas con este sentimiento")
    topics: List[TopicResult]

class TopicsAggregateResponse(BaseModel):
    """Respuesta del endpoint de tópicos agregados"""
    positive_topics: TopicSummary
    negative_topics: TopicSummary
    data_source: str = Field(..., description="Fuente de los datos")
    total_reviews_analyzed: int


# Variables globales y cache
_cached_data: Optional[pd.DataFrame] = None
_lda_models_cache = {}


# Funciones auxiliares
def load_processed_data() -> pd.DataFrame:
    """Carga el dataset procesado o genera uno básico si no existe"""
    global _cached_data
    
    if _cached_data is not None:
        return _cached_data
    
    processed_path = ROOT / "data" / "hotel_reviews_processed.csv"
    raw_path = ROOT / "data" / "Hotel_Reviews.csv"
    
    if processed_path.exists():
        print(f"Cargando dataset procesado desde {processed_path}")
        _cached_data = pd.read_csv(processed_path)
        return _cached_data
    elif raw_path.exists():
        print(f"Dataset procesado no encontrado. Cargando raw desde {raw_path}")
        _cached_data = pd.read_csv(raw_path, nrows=10000)  # Limitar para no sobrecargar
        
        # Procesar básicamente
        for col in ['Positive_Review', 'Negative_Review']:
            if col in _cached_data.columns:
                _cached_data[col] = _cached_data[col].apply(clean_text)
        
        # Crear review_text combinada
        if 'Positive_Review' in _cached_data.columns and 'Negative_Review' in _cached_data.columns:
            _cached_data['review_text'] = _cached_data.apply(
                lambda row: f"{row['Positive_Review']}. {row['Negative_Review']}".strip(". "),
                axis=1
            )
        
        # Analizar sentimientos si no existen
        if 'sentiment_label' not in _cached_data.columns:
            print("Analizando sentimientos...")
            ensure_vader()
            scores = analyze_sentiment_batch(_cached_data['review_text'])
            _cached_data = pd.concat([_cached_data, scores], axis=1)
            _cached_data['sentiment_label'] = _cached_data['compound'].apply(classify_sentiment)
        
        return _cached_data
    else:
        raise FileNotFoundError("No se encontró ningún dataset (procesado ni raw)")

def analyze_single_review(text: str) -> dict:
    """Analiza una reseña individual y retorna sentimiento + tópicos"""
    # Limpiar texto
    cleaned = clean_text(text)
    
    if not cleaned or len(cleaned) < 10:
        raise ValueError("El texto es demasiado corto después de limpiarlo")
    
    # Analizar sentimiento
    ensure_vader()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(cleaned)
    
    sentiment_label = classify_sentiment(scores['compound'])
    
    # Extraer tópicos (usando muestra del dataset para entrenar)
    try:
        df_sample = pd.DataFrame({'review_text': [cleaned]})
        
        # Cargar datos para contexto si están disponibles
        try:
            df_context = load_processed_data()
            # Usar muestra del contexto + la nueva reseña
            sample_size = min(5000, len(df_context))
            df_for_topics = pd.concat([
                df_context.sample(n=sample_size, random_state=42)[['review_text']],
                df_sample
            ]).reset_index(drop=True)
        except:
            df_for_topics = df_sample
        
        # Extraer tópicos
        topics_raw = extract_topics(
            df_for_topics,
            text_column='review_text',
            n_topics=5,
            max_features=3000,
            max_iter=10
        )
        
        topics_list = [
            {"topic_id": i+1, "keywords": topic.split(": ", 1)[1] if ": " in topic else topic}
            for i, topic in enumerate(topics_raw)
        ]
        
    except Exception as e:
        print(f"Error extrayendo tópicos: {e}")
        topics_list = []
    
    return {
        "cleaned_text": cleaned,
        "sentiment": {
            "sentiment": sentiment_label,
            "compound_score": scores['compound'],
            "positive_score": scores['pos'],
            "negative_score": scores['neg'],
            "neutral_score": scores['neu']
        },
        "topics": topics_list
    }


# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Hotel Reviews Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/reviews/analyze": "POST - Analiza una reseña individual",
            "/reviews/topics": "GET - Obtiene resumen de tópicos agregados",
            "/docs": "Documentación interactiva"
        }
    }

@app.post("/reviews/analyze", response_model=AnalyzeResponse)
async def analyze_review(review: ReviewInput):
    """
    Analiza una reseña y devuelve su sentimiento y los temas detectados.
    
    - **text**: Texto de la reseña a analizar (mínimo 10 caracteres)
    
    Retorna:
    - **cleaned_text**: Texto limpio de la reseña
    - **sentiment**: Clasificación del sentimiento con scores VADER
    - **topics**: Lista de tópicos detectados con palabras clave
    """
    try:
        result = analyze_single_review(review.text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la reseña: {str(e)}")

@app.get("/reviews/topics", response_model=TopicsAggregateResponse)
async def get_aggregated_topics(n_topics: int = 8, max_reviews: int = 10000):
    """
    Provee un resumen agregado de los tópicos más mencionados en reseñas positivas y negativas.
    
    Parámetros:
    - **n_topics**: Número de tópicos a extraer por categoría (default: 8)
    - **max_reviews**: Máximo número de reseñas a analizar (default: 10000)
    
    Retorna:
    - **positive_topics**: Tópicos extraídos de reseñas positivas
    - **negative_topics**: Tópicos extraídos de reseñas negativas
    - **data_source**: Fuente de los datos utilizados
    - **total_reviews_analyzed**: Total de reseñas analizadas
    """
    try:
        # Cargar datos
        df = load_processed_data()
        
        # Limitar número de reseñas si es necesario
        if len(df) > max_reviews:
            df = df.sample(n=max_reviews, random_state=42)
        
        # Verificar que existan las columnas necesarias
        if 'sentiment_label' not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="El dataset no tiene análisis de sentimientos. Ejecute el pipeline principal primero."
            )
        
        if 'review_text' not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="El dataset no tiene la columna 'review_text'"
            )
        
        # Filtrar reseñas positivas y negativas
        df_positive = df[df['sentiment_label'] == 'positivo'].copy()
        df_negative = df[df['sentiment_label'] == 'negativo'].copy()
        
        # Extraer tópicos de reseñas positivas
        print(f"Extrayendo tópicos de {len(df_positive)} reseñas positivas...")
        topics_pos_raw = extract_topics(
            df_positive,
            text_column='review_text',
            n_topics=n_topics,
            max_features=5000,
            max_iter=15
        )
        
        topics_positive = [
            {"topic_id": i+1, "keywords": topic.split(": ", 1)[1] if ": " in topic else topic}
            for i, topic in enumerate(topics_pos_raw)
        ]
        
        # Extraer tópicos de reseñas negativas
        print(f"Extrayendo tópicos de {len(df_negative)} reseñas negativas...")
        topics_neg_raw = extract_topics(
            df_negative,
            text_column='review_text',
            n_topics=n_topics,
            max_features=5000,
            max_iter=15
        )
        
        topics_negative = [
            {"topic_id": i+1, "keywords": topic.split(": ", 1)[1] if ": " in topic else topic}
            for i, topic in enumerate(topics_neg_raw)
        ]
        
        # Construir respuesta
        return {
            "positive_topics": {
                "sentiment_type": "positivo",
                "total_reviews": len(df_positive),
                "topics": topics_positive
            },
            "negative_topics": {
                "sentiment_type": "negativo",
                "total_reviews": len(df_negative),
                "topics": topics_negative
            },
            "data_source": "hotel_reviews_processed.csv" if (ROOT / "data" / "hotel_reviews_processed.csv").exists() else "Hotel_Reviews.csv (muestra)",
            "total_reviews_analyzed": len(df)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen de tópicos: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    try:
        # Verificar que VADER está disponible
        ensure_vader()
        
        # Verificar que hay datos disponibles
        df = load_processed_data()
        
        return {
            "status": "healthy",
            "vader_available": True,
            "data_loaded": True,
            "total_reviews": len(df)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("Iniciando API en http://localhost:8000")
    print("Documentación disponible en http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

