"""
API REST completa para Hotel Reviews Analysis
Maneja toda la lógica de negocio: datos, filtros, estadísticas, análisis, visualizaciones
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de rutas
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
DATA_PATH = ROOT / "data" / "hotel_reviews_processed.csv"

# Importar módulos del pipeline
from text_processing import clean_text
from sentiment_analysis import ensure_vader, analyze_sentiment_batch, classify_sentiment
from topic_modeling import extract_topics, get_extended_stop_words

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ReviewInput(BaseModel):
    """Modelo para recibir una reseña a analizar"""
    text: str = Field(..., min_length=10, description="Texto de la reseña a analizar")

class SentimentResult(BaseModel):
    """Resultado del análisis de sentimiento"""
    sentiment: str
    compound_score: float
    positive_score: float
    negative_score: float
    neutral_score: float

class TopicResult(BaseModel):
    """Tópico detectado con sus palabras clave"""
    topic_id: int
    keywords: str

class AnalyzeResponse(BaseModel):
    """Respuesta completa del análisis de una reseña"""
    cleaned_text: str
    sentiment: SentimentResult
    topics: List[TopicResult]

class DatasetStats(BaseModel):
    """Estadísticas generales del dataset"""
    total_reviews: int
    total_hotels: int
    total_countries: int
    average_score: float
    sentiment_distribution: Dict[str, int]
    score_distribution: Dict[str, int]

class FilterParams(BaseModel):
    """Parámetros de filtrado con soporte para paginación"""
    hotel: Optional[str] = None
    sentiment: Optional[str] = None
    nationality: Optional[str] = None
    score_min: float = 0.0
    score_max: float = 10.0
    offset: int = 0  # Desplazamiento para paginación
    limit: Optional[int] = None  # Límite de resultados

class ReviewsResponse(BaseModel):
    """Respuesta con reseñas filtradas"""
    total_available: int
    returned: int
    filters_applied: Dict[str, Any]
    reviews: List[Dict[str, Any]]

class HotelsList(BaseModel):
    """Lista de hoteles disponibles"""
    total: int
    hotels: List[str]

class NationalitiesList(BaseModel):
    """Lista de nacionalidades disponibles"""
    total: int
    nationalities: List[str]

class TopicsAggregateResponse(BaseModel):
    """Respuesta del endpoint de tópicos agregados"""
    positive_topics: Dict[str, Any]
    negative_topics: Dict[str, Any]
    total_reviews_analyzed: int

class WordCloudData(BaseModel):
    """Datos para generar word cloud"""
    words: Dict[str, int]
    total_words: int

class AggregatedMetrics(BaseModel):
    """Métricas agregadas con filtros aplicados"""
    total_reviews: int
    filters_applied: Dict[str, Any]
    sentiment_distribution: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    score_distribution: Dict[str, int]
    average_score: float
    median_score: float
    top_hotels: List[Dict[str, Any]]
    top_nationalities: List[Dict[str, Any]]

class TimeSeriesData(BaseModel):
    """Datos de serie temporal"""
    dates: List[str]
    values: List[int]
    metric: str

class DistributionData(BaseModel):
    """Datos de distribución para gráficos"""
    labels: List[str]
    values: List[int]
    percentages: List[float]
    metric: str

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Hotel Reviews Analysis API - Full Backend",
    description="API completa para análisis de reseñas de hoteles. Maneja datos, filtros, estadísticas y ML.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://*.streamlit.app",
        "https://*.streamlitapp.com",
        "*"  # En producción, especificar dominio exacto
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CACHE Y ESTADO GLOBAL
# ============================================================================

_cached_data: Optional[pd.DataFrame] = None
_cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 300  # 5 minutos

def get_cached_data() -> pd.DataFrame:
    """Obtiene datos con cache"""
    global _cached_data, _cache_timestamp
    
    now = datetime.now()
    
    # Si hay cache válido, retornar
    if _cached_data is not None and _cache_timestamp is not None:
        if (now - _cache_timestamp).total_seconds() < CACHE_TTL_SECONDS:
            return _cached_data.copy()
    
    # Cargar datos
    logger.info(f"Cargando datos desde {DATA_PATH}")
    
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Dataset no encontrado en {DATA_PATH}")
    
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
        logger.info(f"Dataset cargado: {len(df)} reseñas")
        
        # Normalizar nombres de columnas (solo las que existen)
        rename_map = {}
        if "Hotel_Name" in df.columns:
            rename_map["Hotel_Name"] = "Nombre del Hotel"
        if "Reviewer_Nationality" in df.columns:
            rename_map["Reviewer_Nationality"] = "Nacionalidad del Revisor"
        if "Positive_Review" in df.columns:
            rename_map["Positive_Review"] = "Reseña Positiva"
        if "Negative_Review" in df.columns:
            rename_map["Negative_Review"] = "Reseña Negativa"
        if "review_text" in df.columns:
            rename_map["review_text"] = "Texto de Reseña"
        if "sentiment_label" in df.columns:
            rename_map["sentiment_label"] = "Etiqueta de Sentimiento"
        if "Reviewer_Score" in df.columns:
            rename_map["Reviewer_Score"] = "Puntuación del Revisor"
        
        df = df.rename(columns=rename_map)
        
        # Limpiar datos
        df["Puntuación del Revisor"] = pd.to_numeric(df["Puntuación del Revisor"], errors="coerce")
        df["lat"] = pd.to_numeric(df.get("lat", pd.Series()), errors="coerce")
        df["lng"] = pd.to_numeric(df.get("lng", pd.Series()), errors="coerce")
        
        # Rellenar nulos
        df["Nombre del Hotel"] = df["Nombre del Hotel"].fillna("Hotel Desconocido")
        df["Nacionalidad del Revisor"] = df["Nacionalidad del Revisor"].fillna("Sin Especificar")
        df["Reseña Positiva"] = df["Reseña Positiva"].fillna("")
        df["Reseña Negativa"] = df["Reseña Negativa"].fillna("")
        
        # Crear columna "Texto de Reseña" si no existe
        if "Texto de Reseña" not in df.columns or df["Texto de Reseña"].isna().all():
            logger.info("Creando columna 'Texto de Reseña' combinando positivas y negativas")
            df["Texto de Reseña"] = (
                df["Reseña Positiva"].astype(str) + " " + df["Reseña Negativa"].astype(str)
            ).str.strip()
        
        df["Texto de Reseña"] = df["Texto de Reseña"].fillna("")
        
        # Calcular sentiment si no existe la columna
        if "Etiqueta de Sentimiento" not in df.columns:
            logger.info("Calculando sentimiento para todas las reseñas (esto puede tardar)...")
            def calc_sentiment_label(score):
                """Calcula sentiment basado en la puntuación"""
                if score >= 7.5:
                    return "positivo"
                elif score <= 5.0:
                    return "negativo"
                else:
                    return "neutro"
            
            df["Etiqueta de Sentimiento"] = df["Puntuación del Revisor"].apply(calc_sentiment_label)
            logger.info("Sentimiento calculado basado en puntuaciones")
        else:
            df["Etiqueta de Sentimiento"] = df["Etiqueta de Sentimiento"].fillna("neutro")
        
        median_score = df["Puntuación del Revisor"].median()
        df["Puntuación del Revisor"] = df["Puntuación del Revisor"].fillna(median_score)
        
        _cached_data = df
        _cache_timestamp = now
        
        return df.copy()
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error cargando dataset: {str(e)}")

def apply_filters(df: pd.DataFrame, filters: FilterParams) -> pd.DataFrame:
    """Aplica filtros al dataframe con soporte para paginación (offset/limit)"""
    result = df.copy()
    
    # Aplicar filtros de criterios
    if filters.hotel and filters.hotel != "(Todos)":
        result = result[result["Nombre del Hotel"] == filters.hotel]
    
    if filters.sentiment and filters.sentiment != "(Todos)":
        result = result[result["Etiqueta de Sentimiento"] == filters.sentiment]
    
    if filters.nationality and filters.nationality != "(Todas)":
        result = result[result["Nacionalidad del Revisor"] == filters.nationality]
    
    # Filtro por score
    result = result[
        (result["Puntuación del Revisor"] >= filters.score_min) &
        (result["Puntuación del Revisor"] <= filters.score_max)
    ]
    
    # Reset index antes de aplicar offset (importante para iloc)
    result = result.reset_index(drop=True)
    
    # Aplicar paginación: offset + limit
    if filters.offset > 0:
        if filters.offset < len(result):
            result = result.iloc[filters.offset:]
        else:
            # Offset fuera de rango, retornar DataFrame vacío
            result = result.iloc[0:0]
    
    if filters.limit and filters.limit > 0:
        result = result.head(filters.limit)
    
    return result

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Información de la API"""
    return {
        "name": "Hotel Reviews Analysis API - Full Backend",
        "version": "2.0.0",
        "status": "online",
        "description": "API completa que maneja toda la lógica de negocio",
        "endpoints": {
            "GET /health": "Health check",
            "GET /stats": "Estadísticas del dataset",
            "GET /hotels": "Lista de hoteles",
            "GET /nationalities": "Lista de nacionalidades",
            "POST /reviews/filter": "Obtener reseñas filtradas",
            "POST /reviews/analyze": "Analizar una reseña individual",
            "POST /reviews/topics": "Obtener tópicos agregados por sentimiento",
            "POST /reviews/wordcloud": "Datos para word cloud"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificar salud de la API"""
    try:
        df = get_cached_data()
        ensure_vader()
        
        return {
            "status": "healthy",
            "dataset_loaded": True,
            "total_reviews": len(df),
            "vader_available": True,
            "cache_age_seconds": (datetime.now() - _cache_timestamp).total_seconds() if _cache_timestamp else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/stats", response_model=DatasetStats, tags=["Dataset"])
async def get_stats():
    """Obtener estadísticas generales del dataset"""
    try:
        df = get_cached_data()
        
        # Calcular distribución de sentimientos
        sentiment_dist = df["Etiqueta de Sentimiento"].value_counts().to_dict()
        
        # Calcular distribución de puntuaciones
        score_bins = pd.cut(df["Puntuación del Revisor"], bins=[0, 2, 4, 6, 8, 10])
        score_dist = score_bins.value_counts().to_dict()
        score_dist = {str(k): int(v) for k, v in score_dist.items()}
        
        return DatasetStats(
            total_reviews=len(df),
            total_hotels=df["Nombre del Hotel"].nunique(),
            total_countries=df["Nacionalidad del Revisor"].nunique(),
            average_score=float(df["Puntuación del Revisor"].mean()),
            sentiment_distribution=sentiment_dist,
            score_distribution=score_dist
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotels", response_model=HotelsList, tags=["Dataset"])
async def get_hotels(limit: int = Query(None, ge=1, le=1000, description="Limitar número de hoteles")):
    """Obtener lista de hoteles disponibles"""
    try:
        df = get_cached_data()
        hotels = sorted(df["Nombre del Hotel"].unique().tolist())
        
        if limit:
            hotels = hotels[:limit]
        
        return HotelsList(
            total=len(hotels),
            hotels=hotels
        )
        
    except Exception as e:
        logger.error(f"Error getting hotels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nationalities", response_model=NationalitiesList, tags=["Dataset"])
async def get_nationalities(limit: int = Query(50, ge=1, le=500, description="Limitar número de nacionalidades")):
    """Obtener lista de nacionalidades disponibles"""
    try:
        df = get_cached_data()
        nationalities = sorted(df["Nacionalidad del Revisor"].unique().tolist())[:limit]
        
        return NationalitiesList(
            total=len(nationalities),
            nationalities=nationalities
        )
        
    except Exception as e:
        logger.error(f"Error getting nationalities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reviews/filter", response_model=ReviewsResponse, tags=["Reviews"])
async def filter_reviews(filters: FilterParams):
    """
    Obtener reseñas filtradas según criterios con soporte para paginación
    
    - **hotel**: Filtrar por nombre de hotel específico
    - **sentiment**: Filtrar por sentimiento (positivo, negativo, neutro)
    - **nationality**: Filtrar por nacionalidad del revisor
    - **score_min**: Puntuación mínima (0-10)
    - **score_max**: Puntuación máxima (0-10)
    - **offset**: Desplazamiento para paginación (por defecto 0)
    - **limit**: Número máximo de reseñas a retornar (por defecto 10,000 para evitar "Response too large")
    
    NOTA: Cloud Run tiene límite de respuesta HTTP de ~32MB. Con 10K registros estamos seguros.
    """
    try:
        logger.info(f"Received filter request: offset={filters.offset}, limit={filters.limit}")
        
        df = get_cached_data()
        total_before = len(df)
        logger.info(f"Total reviews in dataset: {total_before}")
        
        # Aplicar filtros (incluye offset y limit internamente)
        df_filtered = apply_filters(df, filters)
        logger.info(f"After filters: {len(df_filtered)} reviews")
        
        # Si no se especifica limit, usar límite seguro por defecto
        # Cloud Run tiene límite de respuesta HTTP de ~32MB
        DEFAULT_LIMIT = 10000  # Límite seguro para evitar "Response too large"
        if not filters.limit or filters.limit <= 0:
            logger.info(f"No limit specified, applying default: {DEFAULT_LIMIT}")
            # El límite ya se aplica en apply_filters, solo ajustamos el objeto filters
            if len(df_filtered) > DEFAULT_LIMIT:
                df_filtered = df_filtered.head(DEFAULT_LIMIT)
        
        # Convertir a lista de diccionarios (optimizado para JSON)
        logger.info(f"Converting {len(df_filtered)} rows to dict...")
        reviews = df_filtered.to_dict('records')
        
        logger.info(f"Returning {len(reviews)} reviews (offset={filters.offset}, limit={filters.limit or DEFAULT_LIMIT})")
        
        return ReviewsResponse(
            total_available=total_before,
            returned=len(reviews),
            filters_applied=filters.dict(),
            reviews=reviews
        )
        
    except Exception as e:
        logger.error(f"Error filtering reviews: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reviews/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_review(review: ReviewInput):
    """
    Analizar una reseña individual
    
    - Limpia el texto
    - Calcula sentimiento (VADER)
    - Extrae tópicos principales
    """
    try:
        # Limpiar texto
        cleaned_text = clean_text(review.text)
        
        if len(cleaned_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Texto muy corto después de limpieza")
        
        # Análisis de sentimiento
        ensure_vader()
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(cleaned_text)
        
        sentiment_label = classify_sentiment(scores['compound'])
        
        # Extraer tópicos
        topics = []
        try:
            df_context = get_cached_data()
            sample_size = min(5000, len(df_context))
            df_for_topics = pd.concat([
                df_context.sample(n=sample_size, random_state=42)[["Texto de Reseña"]].rename(columns={"Texto de Reseña": "review_text"}),
                pd.DataFrame({"review_text": [cleaned_text]})
            ]).reset_index(drop=True)
            
            topics_raw = extract_topics(
                df_for_topics,
                text_column='review_text',
                n_topics=3,
                max_features=2000,
                max_iter=10
            )
            
            topics = [
                TopicResult(
                    topic_id=i+1,
                    keywords=topic.split(": ", 1)[1] if ": " in topic else topic
                )
                for i, topic in enumerate(topics_raw)
            ]
        except Exception as e:
            logger.warning(f"Error extrayendo tópicos: {e}")
        
        return AnalyzeResponse(
            cleaned_text=cleaned_text,
            sentiment=SentimentResult(
                sentiment=sentiment_label,
                compound_score=scores['compound'],
                positive_score=scores['pos'],
                negative_score=scores['neg'],
                neutral_score=scores['neu']
            ),
            topics=topics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing review: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando reseña: {str(e)}")

@app.post("/reviews/topics", response_model=TopicsAggregateResponse, tags=["Analysis"])
async def get_aggregated_topics(
    filters: FilterParams,
    n_topics: int = Query(5, ge=3, le=15, description="Número de tópicos a extraer"),
):
    """
    Obtener tópicos agregados por sentimiento (positivo/negativo)
    Aplica filtros antes de extraer tópicos
    """
    try:
        df = get_cached_data()
        
        # Aplicar filtros base
        df_filtered = apply_filters(df, filters)
        
        if len(df_filtered) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Muy pocas reseñas después de filtrar ({len(df_filtered)}). Se necesitan al menos 100."
            )
        
        # Separar por sentimiento
        df_positive = df_filtered[df_filtered["Etiqueta de Sentimiento"] == "positivo"]
        df_negative = df_filtered[df_filtered["Etiqueta de Sentimiento"] == "negativo"]
        
        result = {}
        
        # Tópicos positivos
        if len(df_positive) >= 50:
            logger.info(f"Extrayendo tópicos de {len(df_positive)} reseñas positivas")
            topics_pos_raw = extract_topics(
                df_positive.rename(columns={"Texto de Reseña": "review_text"}),
                text_column='review_text',
                n_topics=n_topics,
                max_features=3000,
                max_iter=15
            )
            
            result['positive_topics'] = {
                "sentiment_type": "positivo",
                "total_reviews": len(df_positive),
                "topics": [
                    {
                        "topic_id": i+1,
                        "keywords": topic.split(": ", 1)[1] if ": " in topic else topic
                    }
                    for i, topic in enumerate(topics_pos_raw)
                ]
            }
        
        # Tópicos negativos
        if len(df_negative) >= 50:
            logger.info(f"Extrayendo tópicos de {len(df_negative)} reseñas negativas")
            topics_neg_raw = extract_topics(
                df_negative.rename(columns={"Texto de Reseña": "review_text"}),
                text_column='review_text',
                n_topics=n_topics,
                max_features=3000,
                max_iter=15
            )
            
            result['negative_topics'] = {
                "sentiment_type": "negativo",
                "total_reviews": len(df_negative),
                "topics": [
                    {
                        "topic_id": i+1,
                        "keywords": topic.split(": ", 1)[1] if ": " in topic else topic
                    }
                    for i, topic in enumerate(topics_neg_raw)
                ]
            }
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No hay suficientes reseñas para extraer tópicos"
            )
        
        return TopicsAggregateResponse(
            positive_topics=result.get('positive_topics', {"sentiment_type": "positivo", "total_reviews": 0, "topics": []}),
            negative_topics=result.get('negative_topics', {"sentiment_type": "negativo", "total_reviews": 0, "topics": []}),
            total_reviews_analyzed=len(df_filtered)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating topics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/reviews/wordcloud", response_model=WordCloudData, tags=["Analysis"])
async def get_wordcloud_data(
    filters: FilterParams,
    max_words: int = Query(100, ge=10, le=500, description="Número máximo de palabras"),
    sample_size: int = Query(3000, ge=100, le=10000, description="Número de reseñas para samplear")
):
    """
    Obtener datos para generar word cloud
    Retorna frecuencia de palabras para visualización
    """
    try:
        logger.info(f"Generando wordcloud con filtros: {filters.dict()}")
        df = get_cached_data()
        logger.info(f"Dataset cargado: {len(df)} reseñas")
        
        df_filtered = apply_filters(df, filters)
        logger.info(f"Después de filtros: {len(df_filtered)} reseñas")
        
        if len(df_filtered) == 0:
            logger.warning("No hay reseñas después de aplicar filtros")
            raise HTTPException(status_code=404, detail="No hay reseñas con los filtros aplicados")
        
        # Samplear si es necesario
        if len(df_filtered) > sample_size:
            df_filtered = df_filtered.sample(n=sample_size, random_state=42)
            logger.info(f"Sampleado a {len(df_filtered)} reseñas")
        
        # Combinar todo el texto
        logger.info("Combinando texto de reseñas...")
        text_column = "Texto de Reseña"
        if text_column not in df_filtered.columns:
            logger.error(f"Columna '{text_column}' no encontrada. Columnas disponibles: {df_filtered.columns.tolist()}")
            raise HTTPException(status_code=500, detail=f"Columna '{text_column}' no encontrada en dataset")
        
        all_text = " ".join(df_filtered[text_column].dropna().astype(str).tolist())
        logger.info(f"Texto combinado: {len(all_text)} caracteres")
        
        if len(all_text.strip()) == 0:
            logger.warning("Texto vacío después de combinar reseñas")
            return WordCloudData(words={}, total_words=0)
        
        # Limitar tamaño del texto para evitar problemas de memoria
        max_chars = 500000  # 500K caracteres max
        if len(all_text) > max_chars:
            logger.info(f"Texto muy largo ({len(all_text)} chars), limitando a {max_chars}")
            all_text = all_text[:max_chars]
        
        # Limpiar y tokenizar
        logger.info("Limpiando y tokenizando texto...")
        try:
            cleaned = clean_text(all_text)
            logger.info(f"Texto limpio: {len(cleaned)} caracteres")
        except Exception as e:
            logger.error(f"Error limpiando texto: {e}")
            # Si falla la limpieza, usar el texto tal cual en minúsculas
            cleaned = all_text.lower()
        
        words = cleaned.split()
        logger.info(f"Total de palabras después de limpiar: {len(words)}")
        
        # Normalizar palabras a minúsculas para mejor procesamiento
        words = [word.lower() for word in words if word]
        
        # Contar frecuencias
        from collections import Counter
        word_freq = Counter(words)
        logger.info(f"Palabras únicas antes de filtrar stopwords: {len(word_freq)}")
        
        # Filtrar stopwords extendidas
        try:
            stopwords = get_extended_stop_words()
            logger.info(f"Stopwords cargadas: {len(stopwords)}")
        except Exception as e:
            logger.warning(f"Error cargando stopwords: {e}, usando set básico")
            stopwords = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
                'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                'hotel', 'room', 'stay', 'stayed', 'night', 'nights', 'very',
                'good', 'great', 'nice', 'really', 'just', 'got', 'also', 'well'
            }
        
        # Asegurar que todas las stopwords estén en minúsculas
        stopwords = {word.lower() for word in stopwords}
        
        # Filtrar y mantener como Counter para usar most_common
        filtered_freq = Counter({word: count for word, count in word_freq.items() 
                                if word.lower() not in stopwords and len(word) > 2})
        logger.info(f"Palabras únicas después de filtrar stopwords: {len(filtered_freq)}")
        
        # Top N palabras
        top_words = dict(filtered_freq.most_common(max_words))
        logger.info(f"Retornando top {len(top_words)} palabras")
        
        return WordCloudData(
            words=top_words,
            total_words=len(word_freq)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating wordcloud data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - MÉTRICAS AGREGADAS
# ============================================================================

@app.post("/metrics/aggregated", response_model=AggregatedMetrics, tags=["Metrics"])
async def get_aggregated_metrics(filters: FilterParams):
    """
    Obtiene métricas agregadas aplicando filtros.
    Calcula distribuciones, promedios y rankings sin retornar reseñas individuales.
    """
    try:
        logger.info(f"Calculating aggregated metrics with filters: {filters.dict()}")
        
        # Obtener datos
        df = get_cached_data()
        
        # Aplicar filtros
        filtered_df = apply_filters(df, filters)
        
        if filtered_df.empty:
            return AggregatedMetrics(
                total_reviews=0,
                filters_applied=filters.dict(exclude={'offset', 'limit'}),
                sentiment_distribution={},
                sentiment_percentages={},
                score_distribution={},
                average_score=0.0,
                median_score=0.0,
                top_hotels=[],
                top_nationalities=[]
            )
        
        # Distribución de sentimientos
        sentiment_counts = filtered_df["Etiqueta de Sentimiento"].value_counts().to_dict()
        total = len(filtered_df)
        sentiment_percentages = {k: round((v/total)*100, 2) for k, v in sentiment_counts.items()}
        
        # Distribución de puntuaciones
        score_distribution = filtered_df["Puntuación del Revisor"].value_counts().sort_index().to_dict()
        score_distribution = {str(k): int(v) for k, v in score_distribution.items()}
        
        # Promedios
        avg_score = float(filtered_df["Puntuación del Revisor"].mean())
        median_score = float(filtered_df["Puntuación del Revisor"].median())
        
        # Top 10 hoteles
        top_hotels_data = filtered_df.groupby("Nombre del Hotel").agg({
            "Puntuación del Revisor": ["count", "mean"]
        }).reset_index()
        top_hotels_data.columns = ["hotel", "review_count", "avg_score"]
        top_hotels_data = top_hotels_data.sort_values("review_count", ascending=False).head(10)
        top_hotels = top_hotels_data.to_dict('records')
        for hotel in top_hotels:
            hotel["review_count"] = int(hotel["review_count"])
            hotel["avg_score"] = round(float(hotel["avg_score"]), 2)
        
        # Top 10 nacionalidades
        top_nationalities_data = filtered_df["Nacionalidad del Revisor"].value_counts().head(10)
        top_nationalities = [
            {"nationality": str(nat), "review_count": int(count)}
            for nat, count in top_nationalities_data.items()
        ]
        
        logger.info(f"Aggregated metrics calculated: {total} reviews")
        
        return AggregatedMetrics(
            total_reviews=total,
            filters_applied=filters.dict(exclude={'offset', 'limit'}),
            sentiment_distribution=sentiment_counts,
            sentiment_percentages=sentiment_percentages,
            score_distribution=score_distribution,
            average_score=round(avg_score, 2),
            median_score=round(median_score, 2),
            top_hotels=top_hotels,
            top_nationalities=top_nationalities
        )
        
    except Exception as e:
        logger.error(f"Error calculating aggregated metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metrics/distribution", response_model=DistributionData, tags=["Metrics"])
async def get_distribution(
    filters: FilterParams,
    metric: str = Query(..., description="Métrica a distribuir: 'sentiment', 'score', 'hotel', 'nationality'")
):
    """
    Obtiene distribución de una métrica específica con filtros.
    Útil para generar gráficos de barras/pie.
    """
    try:
        logger.info(f"Getting distribution for '{metric}' with filters")
        
        # Obtener datos
        df = get_cached_data()
        
        filtered_df = apply_filters(df, filters)
        
        if filtered_df.empty:
            return DistributionData(
                labels=[],
                values=[],
                percentages=[],
                metric=metric
            )
        
        total = len(filtered_df)
        
        if metric == "sentiment":
            dist = filtered_df["Etiqueta de Sentimiento"].value_counts()
        elif metric == "score":
            dist = filtered_df["Puntuación del Revisor"].value_counts().sort_index()
        elif metric == "hotel":
            dist = filtered_df["Nombre del Hotel"].value_counts().head(20)
        elif metric == "nationality":
            dist = filtered_df["Nacionalidad del Revisor"].value_counts().head(20)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid metric: {metric}")
        
        labels = [str(label) for label in dist.index.tolist()]
        values = [int(val) for val in dist.values.tolist()]
        percentages = [round((val/total)*100, 2) for val in values]
        
        logger.info(f"Distribution calculated: {len(labels)} categories")
        
        return DistributionData(
            labels=labels,
            values=values,
            percentages=percentages,
            metric=metric
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Cargar datos al iniciar"""
    logger.info("Iniciando API Full Backend...")
    try:
        df = get_cached_data()
        logger.info(f"API iniciada exitosamente. Dataset: {len(df)} reseñas")
        ensure_vader()
        logger.info("VADER inicializado")
    except Exception as e:
        logger.error(f"Error en startup: {e}")
        raise

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Iniciando servidor en puerto {port}")
    uvicorn.run(
        "api_app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
