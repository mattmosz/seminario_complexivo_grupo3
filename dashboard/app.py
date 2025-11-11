# dashboard_streamlit/app.py
import os
from io import BytesIO
import requests
import json

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud

# ======================
# 1. Configuración Inicial - PRIMERO
# ======================
st.set_page_config(
    page_title="Booking.com - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mostrar algo INMEDIATAMENTE para que Streamlit Cloud sepa que estamos vivos
st.title("📊 Cargando Dashboard...")
st.caption("Inicializando componentes...")

# ---------- Configuración de API (DESPUÉS de st.set_page_config) ----------
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
        API_TIMEOUT = st.secrets.get("API_TIMEOUT", 60)  # 60s para datasets grandes
    else:
        # Desarrollo local
        API_URL = os.getenv("API_URL", "http://localhost:8000")
        API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))  # 60s timeout
except Exception as e:
    # Si falla, usar valores por defecto
    API_URL = "http://localhost:8000"
    API_TIMEOUT = 60

# ---------- Funciones para integración con API ----------

def check_api_available_fast() -> bool:
    """Verifica si la API está disponible con timeout de 5 segundos"""
    try:
        res = requests.get(f"{API_URL}/health", timeout=5)  # 5 segundos para health check
        return res.status_code == 200
    except Exception as e:
        # Fallar silenciosamente y rápido
        return False
        return False

@st.cache_data(ttl=60)
def check_api_available() -> bool:
    """Verifica si la API está disponible (con cache)"""
    return check_api_available_fast()

@st.cache_data(ttl=300)
def get_stats_from_api() -> dict | None:
    """Obtiene estadísticas generales desde la API"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=30)  # 30s para stats
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en /stats: Status {response.status_code}")
            return None
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"Error parseando JSON de /stats: {e}")
        return None
    except Exception as e:
        st.error(f"Error en get_stats_from_api: {type(e).__name__}: {e}")
        return None

@st.cache_data(ttl=300)
def get_hotels_from_api() -> list:
    """Obtiene lista de hoteles desde la API"""
    try:
        response = requests.get(f"{API_URL}/hotels", timeout=30)  # 30s para lista de hoteles
        if response.status_code == 200:
            return response.json().get("hotels", [])
        return []
    except:
        return []

@st.cache_data(ttl=300)
def get_nationalities_from_api(limit: int = 50) -> list:
    """Obtiene lista de nacionalidades desde la API"""
    try:
        response = requests.get(f"{API_URL}/nationalities", params={"limit": limit}, timeout=30)  # 30s
        if response.status_code == 200:
            return response.json().get("nationalities", [])
        return []
    except:
        return []

@st.cache_data(ttl=300)
def get_aggregated_metrics(hotel=None, sentiment=None, nationality=None, 
                          score_min=0.0, score_max=10.0) -> dict | None:
    """
    Obtiene métricas agregadas pre-calculadas desde la API.
    Retorna distribuciones, promedios y rankings SIN cargar reseñas individuales.
    Perfecto para KPIs y visualizaciones sin consumir memoria.
    """
    try:
        filters = {
            "hotel": hotel if hotel != "(Todos)" else None,
            "sentiment": sentiment if sentiment != "(Todos)" else None,
            "nationality": nationality if nationality != "(Todas)" else None,
            "score_min": score_min,
            "score_max": score_max
        }
        
        response = requests.post(
            f"{API_URL}/metrics/aggregated",
            json=filters,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en /metrics/aggregated: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error obteniendo métricas agregadas: {e}")
        return None

@st.cache_data(ttl=300)
def get_distribution_data(metric: str, hotel=None, sentiment=None, nationality=None,
                         score_min=0.0, score_max=10.0) -> dict | None:
    """
    Obtiene distribución de un metric específico (sentiment, score, hotel, nationality).
    Retorna labels, values y percentages listos para gráficos.
    """
    try:
        filters = {
            "hotel": hotel if hotel != "(Todos)" else None,
            "sentiment": sentiment if sentiment != "(Todos)" else None,
            "nationality": nationality if nationality != "(Todas)" else None,
            "score_min": score_min,
            "score_max": score_max
        }
        
        response = requests.post(
            f"{API_URL}/metrics/distribution?metric={metric}",
            json=filters,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en /metrics/distribution: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error obteniendo distribución: {e}")
        return None

def get_filtered_reviews_from_api(hotel=None, sentiment=None, nationality=None, 
                                  score_min=0.0, score_max=10.0, limit=None) -> dict | None:
    """Obtiene reseñas filtradas desde la API (modo simple sin debug)"""
    try:
        filters = {
            "hotel": hotel if hotel != "(Todos)" else None,
            "sentiment": sentiment if sentiment != "(Todos)" else None,
            "nationality": nationality if nationality != "(Todas)" else None,
            "score_min": score_min,
            "score_max": score_max,
            "limit": limit
        }
        
        timeout_value = API_TIMEOUT
        
        response = requests.post(
            f"{API_URL}/reviews/filter",
            json=filters,
            timeout=timeout_value
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail', 'Error desconocido')}")
            return None
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Timeout ({timeout_value}s). Intenta con filtros más específicos.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 No se pudo conectar a la API.")
        return None
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"❌ Error parseando JSON: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {type(e).__name__}: {e}")
        return None

def get_filtered_reviews_with_offset(offset: int = 0, limit: int = 10000, 
                                     hotel=None, sentiment=None, nationality=None,
                                     score_min=0.0, score_max=10.0) -> dict | None:
    """Obtiene reseñas filtradas con paginación (offset/limit) para carga por lotes
    
    NOTA: limit por defecto 10K para evitar "Response too large" de Cloud Run (límite ~32MB)
    """
    try:
        filters = {
            "hotel": hotel if hotel != "(Todos)" else None,
            "sentiment": sentiment if sentiment != "(Todos)" else None,
            "nationality": nationality if nationality != "(Todas)" else None,
            "score_min": score_min,
            "score_max": score_max,
            "offset": offset,
            "limit": limit
        }
        
        response = requests.post(
            f"{API_URL}/reviews/filter",
            json=filters,
            timeout=120  # Timeout más largo para lotes grandes
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code} en lote offset={offset}")
            return None
            
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Timeout cargando lote offset={offset}")
        return None
    except Exception as e:
        st.error(f"❌ Error en lote offset={offset}: {e}")
        return None

def analyze_review_with_api(review_text: str) -> dict | None:
    """Analiza una reseña usando la API"""
    try:
        response = requests.post(
            f"{API_URL}/reviews/analyze",
            json={"text": review_text},
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail', 'Error desconocido')}")
            return None
    except requests.exceptions.Timeout:
        st.error(f"⏱️ La petición excedió el tiempo límite ({API_TIMEOUT}s)")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 No se pudo conectar a la API en {API_URL}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return None

# OPTIMIZACIÓN: Función cacheada para análisis (evita llamadas duplicadas)
@st.cache_data(ttl=600, show_spinner=False)
def analyze_cached(review_text: str) -> dict | None:
    """Versión cacheada del análisis (10 min TTL, máx 5K chars)"""
    # Limitar texto a 5K caracteres
    text_to_analyze = review_text[:5000] if len(review_text) > 5000 else review_text
    return analyze_review_with_api(text_to_analyze)

def get_topics_from_api(filters: dict, n_topics: int = 8) -> dict | None:
    """Obtiene resumen de tópicos desde la API con filtros"""
    try:
        response = requests.post(
            f"{API_URL}/reviews/topics",
            json=filters,
            params={"n_topics": n_topics},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail', 'Error desconocido')}")
            return None
    except requests.exceptions.Timeout:
        st.error("⏱️ La petición excedió el tiempo límite (120s)")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 No se pudo conectar a la API")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return None

def get_wordcloud_data_from_api(filters: dict, max_words: int = 100, sample_size: int = 3000) -> dict | None:
    """Obtiene datos para word cloud desde la API"""
    try:
        response = requests.post(
            f"{API_URL}/reviews/wordcloud",
            json=filters,
            params={"max_words": max_words, "sample_size": sample_size},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ======================
# 2. CSS Profesional Ejecutivo
# ======================
st.markdown("""
<style>
    /* Reset y base */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Contenedor principal */
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Sidebar personalizado */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f1419 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #E91E8C;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: rgba(255,255,255,0.7);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSlider label {
        color: rgba(255,255,255,0.95) !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem !important;
    }
    
    /* Logo circular en sidebar */
    .sidebar-logo {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #E91E8C, #1E3A5F);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(233, 30, 140, 0.4);
    }
    
    /* Título principal */
    .main-title {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        text-align: center;
        border-bottom: 4px solid #E91E8C;
    }
    
    .main-title h1 {
        color: #1E3A5F;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        text-align: center;
    }
        
    /* KPIs Grid Mejorado */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-left-color: #E91E8C;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(233,30,140,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .kpi-icon-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #E91E8C, #1E3A5F);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(233,30,140,0.3);
        position: relative;
        color: white;
        font-size: 24px;
        font-weight: bold;
    }
    
    .kpi-icon-circle.dataset::before {
        content: '📊';
        font-size: 24px;
    }
    
    .kpi-icon-circle.filtered::before {
        content: '✓';
        font-size: 28px;
    }
    
    .kpi-icon-circle.star::before {
        content: '★';
        font-size: 26px;
    }
    
    .kpi-icon-circle.check::before {
        content: '✓';
        font-size: 28px;
    }
    
    .kpi-icon-circle.hotel::before {
        content: '🏢';
        font-size: 24px;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A5F;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .kpi-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: #E91E8C;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    /* Cards de contenido */
    .content-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #E91E8C;
        padding-bottom: 0.5rem;
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #64748b;
        font-weight: 600;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E91E8C, #1E3A5F);
        color: white !important;
    }
    
    /* Métricas de Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #FFFFFF !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        opacity: 0.95;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #E91E8C, #1E3A5F);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233,30,140,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233,30,140,0.4);
    }
    
    /* Radio buttons horizontales */
    .stRadio > div {
        flex-direction: row;
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        background: rgba(233,30,140,0.2);
    }
    
    /* DataFrames */
    .dataframe {
        font-size: 0.85rem !important;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #E91E8C, #1E3A5F);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #E91E8C;
    }
    
    /* Wordcloud containers mejorados */
    .wordcloud-container {
        background: linear-gradient(135deg, rgba(233,30,140,0.08), rgba(30,58,95,0.08));
        border-radius: 16px;
        padding: 1.5rem;
        border: 3px solid rgba(233,30,140,0.25);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .wordcloud-label {
        font-size: 1.1rem;
        font-weight: 800;
        color: #1E3A5F;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
        background: white;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.15);
        border-left: 5px solid #E91E8C;
    }
    
    /* API Section Styles */
    .api-status-online {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .api-status-offline {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 800;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 1rem 0;
    }
    
    .sentiment-positive {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    
    .sentiment-negative {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    }
    
    .sentiment-neutral {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(107, 114, 128, 0.4);
    }
    
    .topic-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 15px;
        margin: 0.3rem;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .api-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #E91E8C;
    }
    
    /* Responsive */
    @media (max-width: 1400px) {
        .kpi-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    
    @media (max-width: 1000px) {
        .kpi-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .kpi-container {
            grid-template-columns: 1fr;
        }
        
        .main-title h1 {
            font-size: 1.4rem;
        }
        
        .kpi-value {
            font-size: 2rem;
        }
    }
    /* Forzar sidebar siempre visible y sin colapsar */
[data-testid="stSidebar"] {
  visibility: visible !important;
  transform: none !important;
  opacity: 1 !important;
}

/* Evitar que Streamlit lo colapse en breakpoints pequeños */
@media (max-width: 768px) {
  [data-testid="stSidebar"] {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    z-index: 999 !important;
  }
  /* Deja espacio al contenido principal para que no quede debajo */
  .stApp > div:nth-child(1) .block-container {
    margin-left: 18rem !important; /* ajusta al ancho real del sidebar */
  }
}

</style>
""", unsafe_allow_html=True)

# ======================
# 3. Paleta de Colores
# ======================
PALETTE = {
    "positivo": "#E91E8C",
    "neutro": "#C8C8C8",
    "negativo": "#1E3A5F",
}
PLOTLY_TEMPLATE = "plotly"

# ======================
# 4. Carga de Datos (Modo Local + API Comentada)
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "hotel_reviews_processed.csv"))

# --- Configuración para modo dual ---
BASE_API_URL = None  # Ejemplo: "http://localhost:8000/v1"
TOKEN = None          # Ejemplo: "tu_token_si_usas_auth"

# ============================================================================
# FUNCIONES DE CARGA - NUEVA ARQUITECTURA (SOLO API, NO CARGAR DATASET COMPLETO)
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_aggregated_metrics(filters: dict) -> dict | None:
    """
    Obtiene métricas agregadas desde la API (NO carga reseñas completas).
    Usa filtros para calcular estadísticas del lado del servidor.
    TTL: 5 minutos
    """
    try:
        response = requests.post(
            f"{API_URL}/metrics/aggregated",
            json=filters,
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error obteniendo métricas: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error conectando con API: {e}")
        return None
# ELIMINADA: get_distribution_data() antigua - usar la nueva versión en línea 131
@st.cache_data(ttl=600, show_spinner=False)
def get_sample_reviews(filters: dict, limit: int = 100) -> dict | None:
    """
    Obtiene una muestra pequeña de reseñas para mostrar en tablas.
    Solo se usa para visualización, NO para análisis masivo.
    TTL: 10 minutos
    """
    try:
        filters_with_limit = {**filters, "limit": limit, "offset": 0}
        response = requests.post(
            f"{API_URL}/reviews/filter",
            json=filters_with_limit,
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error obteniendo muestra: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error conectando con API: {e}")
        return None

# LEGACY: Mantener por compatibilidad pero NO USAR para análisis
@st.cache_data(show_spinner="🔄 Cargando datos desde API...")
def load_data() -> pd.DataFrame | None:
    """
    DEPRECATED: Esta función carga TODO el dataset (512K reseñas).
    SOLO usar para tabs legacy que aún no se migraron.
    NUEVO: Usar get_aggregated_metrics() y get_sample_reviews() en su lugar.
    """
    
    # Verificar que API esté disponible
    if not check_api_available():
        st.error("❌ API no disponible")
        return None
    
    try:
        # ESTRATEGIA: Carga por lotes con tamaño reducido para evitar "Response too large"
        # Cloud Run tiene límite de ~32MB por respuesta HTTP
        BATCH_SIZE = 10000  # Lotes de 10K reseñas (seguro para límite de respuesta HTTP)
        all_reviews = []
        batch_num = 0
        
        # Obtener el total de reseñas disponibles
        stats = get_stats_from_api()
        if not stats:
            st.error("❌ No se pudo obtener estadísticas de la API")
            return None
        
        total_reviews = stats.get("total_reviews", 0)
        total_batches = (total_reviews + BATCH_SIZE - 1) // BATCH_SIZE  # Redondeo hacia arriba
        
        st.info(f"📊 Cargando {total_reviews:,} reseñas en {total_batches} lotes de hasta {BATCH_SIZE:,} cada uno")
        
        # Crear barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Cargar en lotes usando offset
        for offset in range(0, total_reviews, BATCH_SIZE):
            batch_num += 1
            limit = min(BATCH_SIZE, total_reviews - offset)
            
            status_text.text(f"⏳ Lote {batch_num}/{total_batches}: cargando registros {offset:,} - {offset+limit:,}...")
            
            # Llamar a la API con offset y limit
            result = get_filtered_reviews_with_offset(offset=offset, limit=limit)
            
            if result is None:
                st.error(f"❌ Error cargando lote {batch_num}")
                break
            
            reviews = result.get("reviews", [])
            all_reviews.extend(reviews)
            
            # Actualizar progreso
            progress = min(1.0, len(all_reviews) / total_reviews)
            progress_bar.progress(progress)
        
        progress_bar.empty()
        status_text.empty()
        
        if not all_reviews:
            st.error("❌ No se pudieron cargar reseñas")
            return None
        
        st.success(f"✅ {len(all_reviews):,} reseñas cargadas exitosamente")
        
        # Crear DataFrame
        df = pd.DataFrame(all_reviews)
        
        # Asegurar que las columnas estén en español (ya deberían venir así de la API)
        if "Hotel_Name" in df.columns:
            df = df.rename(columns={
                "Hotel_Name": "Nombre del Hotel",
                "Reviewer_Nationality": "Nacionalidad del Revisor",
                "Positive_Review": "Reseña Positiva",
                "Negative_Review": "Reseña Negativa",
                "review_text": "Texto de Reseña",
                "sentiment_label": "Etiqueta de Sentimiento",
                "Reviewer_Score": "Puntuación del Revisor"
            })
        
        return df
        
    except Exception as e:
        st.error(f"⚠️ Error cargando datos: {type(e).__name__}: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

# --- Inicialización INSTANTÁNEA del dashboard ---
# ESTRATEGIA: Dashboard inicia inmediatamente, sin esperar API

# Limpiar el título temporal
st.empty()

# Inicializar session_state PRIMERO (antes de cualquier consulta)
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.api_checked = False
    st.session_state.api_online = False  # Asumir offline por defecto
    
    # Mostrar que estamos vivos
    with st.spinner("⚡ Inicializando dashboard..."):
        pass  # Pasar inmediatamente

# NO verificar API en el primer render (para que Streamlit Cloud cargue rápido)
# Solo verificar cuando el usuario interactúe
if st.session_state.api_checked:
    # Ya verificamos antes, usar el resultado cacheado
    pass
else:
    # Primera carga - NO verificar API para acelerar deploy
    # El usuario puede hacer clic en "Reintentar" después
    st.session_state.api_checked = True
    st.session_state.api_online = False
    st.session_state.skip_first_check = True  # Flag para saber que saltamos el check

# Obtener datos del session_state
df = st.session_state.df
api_available = df is not None and st.session_state.data_loaded

if not api_available:
    # Modo sin API - Mostrar mensaje y deshabilitar funcionalidades
    st.warning("""
    ### ⚠️ API No Disponible
    
    El dashboard no pudo conectarse a la API de backend. Esto puede deberse a:
    
    - 🔌 La API no está corriendo
    - 😴 El servicio está en modo "sleep" (Render Free Tier - tarda 30-60s en despertar)
    - 🌐 Problemas de red o configuración
    
    **API URL configurada:** `{}`
    
    ---
    
    ### 🔄 ¿Qué hacer?
    
    1. **Si usas Render Free Tier:** Espera 1 minuto y haz clic en "Reintentar"
    2. **Si desarrollas localmente:** Inicia la API con `python api_app.py`
    3. **Verifica la conexión:** Accede a {}/health
    
    ---
    """.format(API_URL, API_URL))
    
    # Botón para reintentar la conexión
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 Reintentar Conexión", type="primary", width='stretch'):
            # Limpiar cache y estado
            st.cache_data.clear()
            
            # Intentar conectar ahora
            with st.spinner("🔄 Verificando API..."):
                api_check = check_api_available_fast()
            
            if api_check:
                # API respondió - intentar cargar datos
                with st.spinner("📥 Cargando datos..."):
                    df_temp = load_data()
                    if df_temp is not None:
                        st.session_state.df = df_temp
                        st.session_state.data_loaded = True
                        st.session_state.api_online = True
                        st.success("✅ ¡Conectado! Recargando...")
                        st.rerun()
                    else:
                        st.error("❌ API respondió pero no hay datos")
            else:
                st.error("❌ API sigue sin responder. Espera 1 minuto más si usas Render.")
    
    with col2:
        if st.button("ℹ️ Info", width='stretch'):
            st.info("""
            **Render Free Tier:**
            - Servicios inactivos se duermen
            - Primer request tarda 30-60s
            - Solución: Espera y recarga
            
            **Local:**
            - Verifica que la API esté corriendo
            - Comando: `python api_app.py`
            """)
    
    # Inicializar df vacío para evitar errores
    df = pd.DataFrame()
    total_dataset_reviews = 0
else:
    total_dataset_reviews = len(df)
    st.success(f"✅ **{total_dataset_reviews:,} reseñas** cargadas desde la API")


# ======================
# 5. Sidebar (Filtros y Controles)
# ======================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">AN</div>', unsafe_allow_html=True)
    st.markdown("## ANALÍTICA CON PYTHON")
    st.caption("Análisis de Sentimiento y Extracción de Tópicos en Reseñas de Hoteles Europeos")
    
    st.markdown("---")
    
    # Toggle para activar/desactivar procesamiento VADER
    use_vader = st.toggle("Usar Análisis VADER", value=True, 
                          help="Desactiva para ver solo datos originales sin procesamiento de sentimiento")
    
    if not use_vader:
        st.info("Modo de consulta básica activado. Análisis de sentimiento deshabilitado.")
    
    st.markdown("---")
    
    # Obtener listas desde la API (solo si está disponible)
    if api_available:
        hotels_list = get_hotels_from_api()
        nationalities_list = get_nationalities_from_api(limit=50)
    else:
        hotels_list = []
        nationalities_list = []
    
    col_hotel = st.selectbox(
        "Hotel",
        ["(Todos)"] + hotels_list,
        disabled=not api_available
    )
    
    if use_vader:
        col_sent = st.radio(
            "Sentimiento",
            ["(Todos)", "positivo", "neutro", "negativo"],
            horizontal=False,
            disabled=not api_available
        )
    else:
        col_sent = "(Todos)"
    
    col_nat = st.selectbox(
        "Nacionalidad",
        ["(Todas)"] + nationalities_list,
        disabled=not api_available
    )
    
    score_lo, score_hi = st.slider(
        "Rango de Puntuación",
        0.0, 10.0, (0.0, 10.0), step=0.5,
        disabled=not api_available
    )
    
    st.markdown("---")
    
    st.markdown("---")
    
    fast_wc = st.toggle("Acelerar nubes de palabras", value=True,
                        help="Usa muestra de 3000 reseñas para generar nubes más rápido",
                        disabled=not api_available)
    
    # Información de la API
    st.markdown("---")
    st.markdown("### 🔌 Estado de la API")
    
    if api_available:
        st.success("✅ API Online")
        st.caption(f"URL: {API_URL}")
    else:
        st.error("❌ API Offline")
        st.caption(f"URL: {API_URL}")
        
        if "localhost" in API_URL:
            st.code("python api_app.py", language="bash")
        else:
            st.info("Si usas Render Free Tier, espera 1 min y recarga la página.")

# ======================
# 6. Aplicar Filtros (HÍBRIDO: API para métricas + muestra local para visuales legacy)
# ======================

if not api_available:
    st.error("⚠️ No se pueden aplicar filtros sin conexión a la API")
    st.stop()

# Crear filtros para API
api_filters = {
    "hotel": col_hotel if col_hotel != "(Todos)" else None,
    "sentiment": col_sent if use_vader and col_sent != "(Todos)" else None,
    "nationality": col_nat if col_nat != "(Todas)" else None,
    "score_min": score_lo,
    "score_max": score_hi,
    "offset": 0,
    "limit": None
}

# NUEVO: Obtener métricas agregadas desde la API (más eficiente)
with st.spinner("📊 Calculando métricas desde API..."):
    metrics = get_aggregated_metrics(api_filters)

if not metrics or metrics["total_reviews"] == 0:
    st.warning("⚠️ No hay reseñas que coincidan con los filtros aplicados")
    st.stop()

# Extraer métricas pre-calculadas
total_filtered = metrics["total_reviews"]
sentiment_distribution = metrics["sentiment_distribution"]
sentiment_percentages = metrics["sentiment_percentages"]
score_distribution = metrics["score_distribution"]
avg_score_api = metrics["average_score"]
median_score_api = metrics["median_score"]
top_hotels_api = metrics["top_hotels"]
top_nationalities_api = metrics["top_nationalities"]

# LEGACY: Para tabs que aún necesitan DataFrame (ej: wordclouds, mapas)
# Cargar solo una MUESTRA (no todo) para visuales
# TODO: Migrar estas tabs a usar endpoints específicos de la API
current_filters = {
    "hotel": col_hotel if col_hotel != "(Todos)" else None,
    "sentiment": col_sent if use_vader and col_sent != "(Todos)" else None,
    "nationality": col_nat if col_nat != "(Todas)" else None,
    "score_min": score_lo,
    "score_max": score_hi
}

dff = df.copy() if df is not None else pd.DataFrame()

if not dff.empty:
    if current_filters["hotel"]:
        dff = dff[dff["Nombre del Hotel"] == current_filters["hotel"]]

    if current_filters["sentiment"]:
        dff = dff[dff["Etiqueta de Sentimiento"] == current_filters["sentiment"]]

    if current_filters["nationality"]:
        dff = dff[dff["Nacionalidad del Revisor"] == current_filters["nationality"]]

    dff = dff[
        (dff["Puntuación del Revisor"] >= current_filters["score_min"]) &
        (dff["Puntuación del Revisor"] <= current_filters["score_max"])
    ]

# ======================
# 7. Header Principal
# ======================
st.markdown("""
<div class="main-title">
    <h1>DASHBOARD: Análisis de Sentimiento - Hoteles Europeos</h1>
</div>
""", unsafe_allow_html=True)

# ======================
# 8. KPIs Principales - USO DE MÉTRICAS AGREGADAS
# ======================

# Las métricas ya se obtuvieron antes (línea ~1161), usar esas
# metrics = get_aggregated_metrics(api_filters)  <-- Ya existe arriba

if metrics:
    # Usar datos de métricas agregadas
    filtered_reviews = metrics.get("total_reviews", 0)
    avg_score = metrics.get("average_score", 0.0)
    
    # Distribución de sentimientos
    sentiment_dist = metrics.get("sentiment_distribution", {})
    sentiment_pcts = metrics.get("sentiment_percentages", {})
    
    pos_pct = sentiment_pcts.get("positivo", 0.0)
    neg_pct = sentiment_pcts.get("negativo", 0.0)
    neu_pct = sentiment_pcts.get("neutro", 0.0)
    
    # Top hoteles
    top_hotels_from_metrics = metrics.get("top_hotels", [])
    unique_hotels = len(top_hotels_from_metrics) if len(top_hotels_from_metrics) < 10 else "10+"
else:
    # Fallback a valores por defecto
    st.error("⚠️ No se pudieron obtener las métricas agregadas de la API")
    filtered_reviews = 0
    avg_score = 0.0
    pos_pct = 0.0
    neg_pct = 0.0
    neu_pct = 0.0
    unique_hotels = "0"
    top_hotels_from_metrics = []

# Obtener total del dataset
if 'total_dataset_reviews' not in st.session_state:
    stats = get_stats_from_api()
    st.session_state.total_dataset_reviews = stats.get("total_reviews", 0) if stats else 0

total_dataset_reviews = st.session_state.total_dataset_reviews

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-badge">DATASET</div>
        <div class="kpi-icon-circle dataset"></div>
        <div class="kpi-value">{total_dataset_reviews:,}</div>
        <div class="kpi-label">Total Reseñas</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">FILTRADO</div>
        <div class="kpi-icon-circle filtered"></div>
        <div class="kpi-value">{filtered_reviews:,}</div>
        <div class="kpi-label">Reseñas Filtradas</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">PROMEDIO</div>
        <div class="kpi-icon-circle star"></div>
        <div class="kpi-value">{avg_score:.1f}</div>
        <div class="kpi-label">Puntuación</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">{'POSITIVO' if use_vader else 'N/A'}</div>
        <div class="kpi-icon-circle check"></div>
        <div class="kpi-value">{pos_pct:.1f}%</div>
        <div class="kpi-label">Satisfacción</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">HOTELES</div>
        <div class="kpi-icon-circle hotel"></div>
        <div class="kpi-value">{unique_hotels}</div>
        <div class="kpi-label">Top Filtrados</div>
    </div>
</div>
""", unsafe_allow_html=True)

if filtered_reviews == 0:
    st.warning("No hay datos disponibles para los filtros seleccionados. Por favor, ajusta los criterios de búsqueda.")
    st.stop()

# ======================
# 9. Funciones de Visualización
# ======================
def fig_area_por_categoria(data: pd.DataFrame, vader_enabled: bool) -> go.Figure:
    """Gráfico de área por categorías de puntuación (estable, sin px.area)."""
    order = ["Bajo", "Medio", "Alto"]
    bins = pd.cut(
        data["Puntuación del Revisor"],
        bins=[0, 4, 7, 10],
        labels=order,
        include_lowest=True,
        right=True
    )

    fig = go.Figure()

    if vader_enabled:
        # Tabla pivote: filas = categoría, columnas = sentimiento
        tmp = (
            pd.DataFrame({"Categoría": bins, "Sentimiento": data["Etiqueta de Sentimiento"]})
            .value_counts()
            .reset_index(name="Cantidad")
        )
        pivot = (
            tmp.pivot(index="Categoría", columns="Sentimiento", values="Cantidad")
               .reindex(order)
               .fillna(0)
        )

        # Asegura columnas en orden (si faltan, las crea en 0)
        for senti in ["negativo", "neutro", "positivo"]:
            if senti not in pivot.columns:
                pivot[senti] = 0

        # Añade trazas apiladas (stacked area)
        fig.add_trace(go.Scatter(
            x=order, y=pivot["negativo"].values,
            name="negativo", mode="lines",
            line=dict(width=1, color=PALETTE["negativo"]),
            stackgroup="one", groupnorm=""  # "" = valores absolutos
        ))
        fig.add_trace(go.Scatter(
            x=order, y=pivot["neutro"].values,
            name="neutro", mode="lines",
            line=dict(width=1, color=PALETTE["neutro"]),
            stackgroup="one"
        ))
        fig.add_trace(go.Scatter(
            x=order, y=pivot["positivo"].values,
            name="positivo", mode="lines",
            line=dict(width=1, color=PALETTE["positivo"]),
            stackgroup="one"
        ))

    else:
        counts = pd.Series(bins).value_counts().reindex(order).fillna(0)
        fig.add_trace(go.Scatter(
            x=order, y=counts.values.astype(float),
            name="Cantidad", mode="lines",
            line=dict(width=2, color=PALETTE["negativo"]),
            fill="tozeroy"
        ))

    fig.update_layout(
        template=PLOTLY_TEMPLATE if PLOTLY_TEMPLATE else "plotly",
        title="Análisis por Categorías de Puntuación",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(categoryorder="array", categoryarray=order, title="")
    fig.update_yaxes(title="Cantidad")
    return fig

def fig_trend(data: pd.DataFrame) -> go.Figure:
    """Tendencia de puntuaciones."""
    t = data.groupby("Puntuación del Revisor", dropna=True).size().reset_index(name="count")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t["Puntuación del Revisor"], y=t["count"],
        mode="lines+markers",
        line=dict(color=PALETTE["negativo"], width=3),
        marker=dict(size=8, color=PALETTE["positivo"]),
        fill='tonexty',
        fillcolor='rgba(30, 58, 95, 0.1)'
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Tendencia de Puntuaciones",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        xaxis_title="Puntuación",
        yaxis_title="Frecuencia",
        margin=dict(l=20, r=20, t=50, b=20),
        height=300
    )
    return fig

def fig_donut(series: pd.Series, title: str) -> go.Figure:
    """Gráfico donut para distribución."""
    counts = series.value_counts()
    colors = [PALETTE.get(label, "#C8C8C8") for label in counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.65,
        marker=dict(colors=colors),
        textinfo="percent+label",
        textfont=dict(size=11, color="white", family="Arial Black")
    )])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=title,
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
        showlegend=False
    )
    return fig

def fig_map(data: pd.DataFrame, vader_enabled: bool) -> go.Figure:
    """Mapa de distribución geográfica."""
    m = data.dropna(subset=["lat", "lng"]).copy()
    if len(m) > 500:
        m = m.sample(500, random_state=42)
    
    if vader_enabled:
        fig = px.scatter_mapbox(
            m, lat="lat", lon="lng",
            color="Etiqueta de Sentimiento",
            color_discrete_map=PALETTE,
            hover_name="Nombre del Hotel",
            hover_data={"Puntuación del Revisor": True, "lat": False, "lng": False},
            zoom=3,
            height=450
        )
    else:
        fig = px.scatter_mapbox(
            m, lat="lat", lon="lng",
            hover_name="Nombre del Hotel",
            hover_data={"Puntuación del Revisor": True, "lat": False, "lng": False},
            zoom=3,
            height=450,
            color_discrete_sequence=["#1E3A5F"]
        )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        template=PLOTLY_TEMPLATE,
        margin=dict(l=0, r=0, t=30, b=0),
        title="Distribución Geográfica de Reseñas",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black")
    )
    return fig

def fig_top_hoteles(data: pd.DataFrame) -> go.Figure:
    """Top 10 hoteles por volumen."""
    top = data["Nombre del Hotel"].value_counts().head(10)
    
    fig = go.Figure(data=[go.Bar(
        y=top.index[::-1],
        x=top.values[::-1],
        orientation="h",
        marker=dict(
            color=top.values[::-1],
            colorscale=[[0, PALETTE["positivo"]], [1, PALETTE["negativo"]]],
            showscale=False
        ),
        text=top.values[::-1],
        textposition="outside"
    )])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Top 10 Hoteles por Volumen de Reseñas",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=150, r=20, t=50, b=20),
        height=350,
        xaxis_title="",
        yaxis_title=""
    )
    return fig

def fig_nationality_distribution(data: pd.DataFrame) -> go.Figure:
    """Distribución por nacionalidad (Top 15)."""
    top_nat = data["Nacionalidad del Revisor"].value_counts().head(15)
    
    fig = go.Figure(data=[go.Bar(
        x=top_nat.index,
        y=top_nat.values,
        marker=dict(
            color=top_nat.values,
            colorscale=[[0, PALETTE["positivo"]], [1, PALETTE["negativo"]]],
            showscale=False
        ),
        text=top_nat.values,
        textposition="outside"
    )])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Top 15 Nacionalidades de Revisores",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=50),
        height=350,
        xaxis_title="",
        yaxis_title="Número de Reseñas",
        xaxis_tickangle=-45
    )
    return fig

# ======================
# NUEVAS FUNCIONES PARA DISTRIBUCIONES DESDE API
# ======================

def fig_donut_from_api_distribution(distribution: dict, title: str) -> go.Figure:
    """Genera gráfico donut desde distribución de API."""
    if not distribution or not distribution.get("labels"):
        return go.Figure()
    
    labels = distribution["labels"]
    values = distribution["values"]
    percentages = distribution["percentages"]
    
    # Colores según sentimiento
    colors = []
    for label in labels:
        if label.lower() in ["positivo", "positive"]:
            colors.append(PALETTE["positivo"])
        elif label.lower() in ["negativo", "negative"]:
            colors.append(PALETTE["negativo"])
        elif label.lower() in ["neutro", "neutral"]:
            colors.append(PALETTE["neutro"])
        else:
            colors.append("#95A5A6")
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#FFF", family="Arial"),
        hovertemplate="<b>%{label}</b><br>%{value:,} reseñas<br>%{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=title,
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
        showlegend=False
    )
    return fig

def fig_top_hoteles_from_metrics(top_hotels: list) -> go.Figure:
    """Top 10 hoteles desde métricas agregadas de API."""
    if not top_hotels:
        return go.Figure()
    
    # Extraer datos
    hotels = [h["hotel"] for h in top_hotels]
    counts = [h["review_count"] for h in top_hotels]
    avg_scores = [h["avg_score"] for h in top_hotels]
    
    fig = go.Figure(data=[go.Bar(
        y=hotels[::-1],  # Invertir para mostrar el mayor arriba
        x=counts[::-1],
        orientation="h",
        marker=dict(
            color=counts[::-1],
            colorscale=[[0, PALETTE["positivo"]], [1, PALETTE["negativo"]]],
            showscale=False
        ),
        text=[f"{c:,}" for c in counts[::-1]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Reseñas: %{x:,}<extra></extra>"
    )])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Top 10 Hoteles por Volumen de Reseñas",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=150, r=20, t=50, b=20),
        height=350,
        xaxis_title="",
        yaxis_title=""
    )
    return fig

def fig_nationality_distribution_from_api(hotel=None, sentiment=None, nationality=None,
                                          score_min=0.0, score_max=10.0) -> go.Figure:
    """Distribución de nacionalidades desde API."""
    distribution = get_distribution_data(
        metric="nationality",
        hotel=hotel,
        sentiment=sentiment,
        nationality=nationality,
        score_min=score_min,
        score_max=score_max
    )
    
    if not distribution or not distribution.get("labels"):
        return go.Figure()
    
    labels = distribution["labels"][:15]  # Top 15
    values = distribution["values"][:15]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=values,
            colorscale=[[0, PALETTE["positivo"]], [1, PALETTE["negativo"]]],
            showscale=False
        ),
        text=values,
        textposition="outside"
    )])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="Top 15 Nacionalidades de Revisores",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=50),
        height=350,
        xaxis_title="",
        yaxis_title="Número de Reseñas",
        xaxis_tickangle=-45
    )
    return fig


def wc_image_from_api(filters: dict, colormap: str, sample_size: int = 3000) -> BytesIO:
    """Genera imagen de nube de palabras usando datos de la API."""
    
    # Obtener datos para word cloud desde la API
    wc_data = get_wordcloud_data_from_api(filters, max_words=150, sample_size=sample_size)
    
    if wc_data is None or not wc_data.get("words"):
        # Si no hay datos, generar una imagen en blanco con mensaje
        wc = WordCloud(
            width=1600,
            height=500,
            background_color="white"
        ).generate("sin datos disponibles")
    else:
        # Generar word cloud desde frecuencias
        wc = WordCloud(
            width=1600,
            height=500,
            background_color="white",
            colormap=colormap,
            relative_scaling=0.5,
            min_font_size=10,
            prefer_horizontal=0.7,
            contour_width=1,
            contour_color="#1E3A5F"
        ).generate_from_frequencies(wc_data["words"])
    
    # Convertir a imagen
    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)
    return buf

# ======================
# 10. Dashboard con Tabs
# ======================
if use_vader:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Análisis General", 
        "🌍 Geografía", 
        "☁️ Palabras Clave", 
        "📋 Datos Detallados",
        "📈 Estadísticas Avanzadas",
        "🔌 Análisis con API"
    ])
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Análisis General", 
        "🌍 Geografía", 
        "📋 Datos Detallados",
        "📈 Estadísticas Avanzadas",
        "🔌 Análisis con API"
    ])

# TAB 1: Análisis General (usando métricas de API)
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        # Nota: fig_area_por_categoria requiere DataFrame, mantenemos carga limitada para esta visualización
        st.plotly_chart(fig_area_por_categoria(dff, use_vader), width='stretch')
    with col2:
        if use_vader and metrics:
            # Obtener distribución de sentimientos desde API
            sentiment_dist = get_distribution_data(
                metric="sentiment",
                hotel=col_hotel if col_hotel != "(Todos)" else None,
                sentiment=col_sent if use_vader and col_sent != "(Todos)" else None,
                nationality=col_nat if col_nat != "(Todas)" else None,
                score_min=score_lo,
                score_max=score_hi
            )
            if sentiment_dist:
                st.plotly_chart(
                    fig_donut_from_api_distribution(sentiment_dist, "Distribución de Sentimientos"),
                    width='stretch'
                )
            else:
                st.error("No se pudo obtener la distribución de sentimientos")
        else:
            st.info("💡 El análisis de sentimientos está deshabilitado. Actívalo en la barra lateral para ver la distribución.")
    
    col3, col4 = st.columns([2, 1])
    with col3:
        # Trend requiere DataFrame temporal
        st.plotly_chart(fig_trend(dff), width='stretch')
    with col4:
        # Top hoteles desde métricas agregadas
        if metrics and top_hotels_from_metrics:
            st.plotly_chart(fig_top_hoteles_from_metrics(top_hotels_from_metrics), width='stretch')
        else:
            st.plotly_chart(fig_top_hoteles(dff), width='stretch')
    
    # Gráfico de nacionalidades desde API
    st.plotly_chart(
        fig_nationality_distribution_from_api(
            hotel=col_hotel if col_hotel != "(Todos)" else None,
            sentiment=col_sent if use_vader and col_sent != "(Todos)" else None,
            nationality=col_nat if col_nat != "(Todas)" else None,
            score_min=score_lo,
            score_max=score_hi
        ),
        width='stretch'
    )

# TAB 2: Geografía
with tab2:
    st.plotly_chart(fig_map(dff, use_vader), width='stretch')
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Ubicaciones Únicas", dff[["lat", "lng"]].dropna().drop_duplicates().shape[0])
    with col_info2:
        st.metric("Países Representados", dff["Nacionalidad del Revisor"].nunique())
    with col_info3:
        st.metric("Hoteles con Geolocalización", 
                 dff.dropna(subset=["lat", "lng"])["Nombre del Hotel"].nunique())
    
    st.info("El mapa muestra hasta 500 puntos para optimizar el rendimiento. "
           "Los colores representan el sentimiento cuando el análisis VADER está activo.")

# TAB 3: Palabras Clave (solo si VADER está activo)
if use_vader:
    with tab3:
        st.markdown("### Análisis de Palabras Frecuentes")
        st.caption("Palabras más comunes en reseñas positivas y negativas (excluye stopwords comunes)")

        col_pos, col_neg = st.columns(2)

        # Preparar filtros para word clouds
        sample_size_wc = 3000 if fast_wc else len(dff)
        
        # Filtro para positivas
        filters_pos = {
            **current_filters,
            "sentiment": "positivo"
        }
        
        # Filtro para negativas
        filters_neg = {
            **current_filters,
            "sentiment": "negativo"
        }

        with col_pos:
            st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
            st.markdown('<span class="wordcloud-label">✓ RESEÑAS POSITIVAS</span>', unsafe_allow_html=True)
            with st.spinner("Generando nube de palabras positivas..."):
                wc_img = wc_image_from_api(filters_pos, "RdPu", sample_size=sample_size_wc)
                if wc_img:
                    st.image(wc_img, width='stretch')
                else:
                    st.warning("No hay suficientes reseñas positivas para generar la nube de palabras.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_neg:
            st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
            st.markdown('<span class="wordcloud-label">✗ RESEÑAS NEGATIVAS</span>', unsafe_allow_html=True)
            with st.spinner("Generando nube de palabras negativas..."):
                wc_img = wc_image_from_api(filters_neg, "Blues", sample_size=sample_size_wc)
                if wc_img:
                    st.image(wc_img, width='stretch')
                else:
                    st.warning("No hay suficientes reseñas negativas para generar la nube de palabras.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Estadísticas de palabras
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            avg_pos_length = dff.loc[dff["Etiqueta de Sentimiento"].eq("positivo"), "Reseña Positiva"].str.split().str.len().mean()
            st.metric("Longitud Promedio (Positivas)", f"{avg_pos_length:.0f} palabras")
        with col_stat2:
            avg_neg_length = dff.loc[dff["Etiqueta de Sentimiento"].eq("negativo"), "Reseña Negativa"].str.split().str.len().mean()
            st.metric("Longitud Promedio (Negativas)", f"{avg_neg_length:.0f} palabras")

# TAB 4: Datos Detallados
tab_datos = tab4 if use_vader else tab3
with tab_datos:
    st.markdown("### Muestra de Reseñas Filtradas")
    
    # Selector de columnas a mostrar
    available_cols = ["Nombre del Hotel", "Nacionalidad del Revisor", "Puntuación del Revisor"]
    if use_vader:
        available_cols.append("Etiqueta de Sentimiento")
    available_cols.extend(["Reseña Positiva", "Reseña Negativa", "Texto de Reseña"])
    
    selected_cols = st.multiselect(
        "Selecciona las columnas a mostrar:",
        available_cols,
        default=available_cols[:5]
    )
    
    if selected_cols:
        display_df = dff[selected_cols].head(1000).copy()
        
        # Truncar texto largo para mejor visualización
        for col in ["Reseña Positiva", "Reseña Negativa", "Texto de Reseña"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].str[:200] + "..."
        
        st.dataframe(
            display_df,
            width='stretch',
            height=500
        )
        
        st.caption(f"Mostrando {min(1000, len(dff))} de {len(dff)} reseñas filtradas")
    else:
        st.warning("⚠️ Selecciona al menos una columna para mostrar.")
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
    with col_btn1:
        st.download_button(
            "Descargar CSV Filtrado",
            data=dff.to_csv(index=False).encode("utf-8"),
            file_name=f"hotel_reviews_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width='stretch'
        )
    with col_btn2:
        st.download_button(
            "Descargar CSV Completo",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"hotel_reviews_complete_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width='stretch'
        )

# TAB 5: Estadísticas Avanzadas
tab_stats = tab5 if use_vader else tab4
with tab_stats:
    st.markdown("### Estadísticas Avanzadas")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric(
            "Mediana de Puntuación",
            f"{dff['Puntuación del Revisor'].median():.1f}",
            help="Valor central de todas las puntuaciones"
        )
    
    with col_s2:
        st.metric(
            "Desviación Estándar",
            f"{dff['Puntuación del Revisor'].std():.2f}",
            help="Medida de dispersión de las puntuaciones"
        )
    
    with col_s3:
        st.metric(
            "Puntuación Mínima",
            f"{dff['Puntuación del Revisor'].min():.1f}"
        )
    
    with col_s4:
        st.metric(
            "Puntuación Máxima",
            f"{dff['Puntuación del Revisor'].max():.1f}"
        )
    
    st.markdown("---")
    
    # Histograma detallado
    fig_hist = px.histogram(
        dff, 
        x="Puntuación del Revisor",
        nbins=20,
        color="Etiqueta de Sentimiento" if use_vader else None,
        color_discrete_map=PALETTE if use_vader else None,
        template=PLOTLY_TEMPLATE
    )
    fig_hist.update_layout(
        title="Distribución Detallada de Puntuaciones",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        xaxis_title="Puntuación",
        yaxis_title="Frecuencia",
        height=400,
        bargap=0.1
    )
    st.plotly_chart(fig_hist, width='stretch')
    
    st.markdown("---")
    
    # Tabla de estadísticas por hotel (top 10)
    if len(dff) > 0:
        st.markdown("#### Estadísticas por Hotel (Top 10)")
        
        hotel_stats = dff.groupby("Nombre del Hotel").agg({
            "Puntuación del Revisor": ["count", "mean", "std", "min", "max"]
        }).round(2)
        
        hotel_stats.columns = ["Reseñas", "Promedio", "Desv. Est.", "Mín", "Máx"]
        hotel_stats = hotel_stats.sort_values("Reseñas", ascending=False).head(10)
        hotel_stats = hotel_stats.reset_index()
        
        st.dataframe(
            hotel_stats,
            width='stretch',
            height=400
        )
    
    # Información sobre calidad de datos
    st.markdown("---")
    st.markdown("#### Calidad de Datos")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        null_scores = dff["Puntuación del Revisor"].isna().sum()
        st.metric("Puntuaciones Nulas", null_scores)
    
    with col_q2:
        null_geo = dff[["lat", "lng"]].isna().any(axis=1).sum()
        st.metric("Sin Geolocalización", null_geo)
    
    with col_q3:
        empty_reviews = (dff["Reseña Positiva"].str.strip() == "").sum() + \
                       (dff["Reseña Negativa"].str.strip() == "").sum()
        st.metric("Reseñas Vacías", empty_reviews)

    # --- Evaluación general del dataset ---
    st.markdown("---")
    st.markdown("#### Índice Global de Calidad del Dataset")

    # Calcular proporciones
    total_registros = len(dff)
    peso_geo = 0.3
    peso_texto = 0.4
    peso_score = 0.3

    pct_geo = 1 - (null_geo / total_registros)
    pct_texto = 1 - (empty_reviews / total_registros)
    pct_score = 1 - (null_scores / total_registros)

    data_health = round((pct_geo*peso_geo + pct_texto*peso_texto + pct_score*peso_score) * 100, 1)

    # Barra de progreso con color dinámico
    bar_color = "#10B981" if data_health >= 85 else "#F59E0B" if data_health >= 70 else "#EF4444"

    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        border-left: 5px solid {bar_color};
        margin-bottom: 1.5rem;">
        <h3 style="color:white; margin-bottom:0.5rem;">Calidad Global de los Datos</h3>
        <p style="color:rgba(255,255,255,0.85); font-weight:500;">
            Este índice combina la completitud de puntuaciones, texto y geolocalización.
        </p>
        <div style="width:100%; background:rgba(255,255,255,0.15); border-radius:10px; height:20px; overflow:hidden; margin-top:10px;">
            <div style="width:{data_health}%; background:{bar_color}; height:100%; transition:width 1s ease;"></div>
        </div>
        <h2 style="color:white; margin-top:0.75rem;">{data_health}%</h2>
    </div>
    """, unsafe_allow_html=True)

    if data_health >= 85:
        st.success(" Excelente calidad de datos — el dataset está listo para análisis confiables.")
    elif data_health >= 70:
        st.warning(" Calidad de datos aceptable — podrías mejorar completitud o texto.")
    else:
        st.error(" Baja calidad de datos — revisa nulos o reseñas vacías.")

# TAB 6: Análisis con API
tab_api = tab6 if use_vader else tab5
with tab_api:
    st.markdown("### 🔌 Análisis de Reseñas con API REST")
    st.markdown("Esta sección utiliza la API REST de FastAPI para análisis en tiempo real")
    
    # Verificar estado de la API
    api_available = check_api_available()
    
    col_status1, col_status2 = st.columns([3, 1])
    with col_status1:
        if api_available:
            st.markdown('<div class="api-status-online">✅ API CONECTADA</div>', unsafe_allow_html=True)
            st.caption(f"Endpoint: {API_URL}")
        else:
            st.markdown('<div class="api-status-offline">❌ API NO DISPONIBLE</div>', unsafe_allow_html=True)
            st.caption(f"Intenta iniciar la API: `python api_app.py`")
    
    with col_status2:
        if st.button("🔄 Verificar API", width='stretch'):
            st.cache_data.clear()
            st.rerun()
    
    if not api_available:
        st.error("""
        **La API no está disponible.** Para usar esta funcionalidad:
        
        1. Abre una terminal en la raíz del proyecto
        2. Ejecuta: `python api_app.py`
        3. Espera a que inicie en http://localhost:8000
        4. Recarga esta página
        
        La API permite análisis de reseñas individuales y resúmenes de tópicos agregados.
        """)
        
        st.info("""
        **📖 Documentación de la API:**
        - Swagger UI: http://localhost:8000/docs
        - README: API_README.md
        - Guía rápida: QUICKSTART_API.md
        """)
        
        st.stop()
    
    # Dos secciones: Análisis Individual y Resumen de Tópicos
    st.markdown("---")
    
    subtab1, subtab2 = st.tabs(["🔍 Análisis Individual", "📊 Resumen de Tópicos"])
    
    # SUBTAB 1: Análisis de reseña individual (OPTIMIZADO)
    with subtab1:
        st.markdown("#### Analiza una reseña del dataset")
        
        # OPTIMIZACIÓN 1: Limitar reseñas a mostrar (de 100 a 20)
        MAX_REVIEWS_TO_SHOW = 20
        
        # Filtros para seleccionar reseña
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            # Filtro por hotel (limitado a top 50 para performance)
            hotel_counts = dff["Nombre del Hotel"].value_counts().head(50)
            hotel_options = ["(Todos)"] + hotel_counts.index.tolist()
            selected_hotel = st.selectbox(
                "🏨 Filtrar por Hotel (Top 50):",
                hotel_options,
                key="api_hotel_select",
                help="Mostrando solo los 50 hoteles con más reseñas para mejor rendimiento"
            )
        
        with col_filter2:
            # Filtro por sentimiento
            if use_vader and "Etiqueta de Sentimiento" in dff.columns:
                sentiment_options = ["(Todos)", "positivo", "negativo", "neutro"]
                selected_sentiment = st.selectbox(
                    "😊 Filtrar por Sentimiento:",
                    sentiment_options,
                    key="api_sentiment_select"
                )
            else:
                selected_sentiment = "(Todos)"
        
        # OPTIMIZACIÓN 2: Función cacheada para filtrar muestra
        @st.cache_data(ttl=300)
        def get_filtered_sample(hotel, sentiment, limit=MAX_REVIEWS_TO_SHOW):
            """Obtiene muestra filtrada con caché (5 min)"""
            temp_df = dff.copy()
            
            if hotel != "(Todos)":
                temp_df = temp_df[temp_df["Nombre del Hotel"] == hotel]
            
            if sentiment != "(Todos)" and use_vader:
                temp_df = temp_df[temp_df["Etiqueta de Sentimiento"] == sentiment]
            
            # Tomar solo las primeras N reseñas
            return temp_df.head(limit)
        
        # Obtener muestra filtrada
        dff_sample = get_filtered_sample(selected_hotel, selected_sentiment)
        
        # Calcular total disponible (sin cargar todo)
        if selected_hotel == "(Todos)" and selected_sentiment == "(Todos)":
            total_available = len(dff)
        else:
            temp_mask = pd.Series([True] * len(dff))
            if selected_hotel != "(Todos)":
                temp_mask &= (dff["Nombre del Hotel"] == selected_hotel)
            if selected_sentiment != "(Todos)" and use_vader:
                temp_mask &= (dff["Etiqueta de Sentimiento"] == selected_sentiment)
            total_available = temp_mask.sum()
        
        st.info(f"📊 Total disponible: **{total_available:,}** | Mostrando: **{len(dff_sample)}** (optimizado para rendimiento)")
        
        if len(dff_sample) == 0:
            st.warning("⚠️ No hay reseñas con estos filtros.")
        else:
            # OPTIMIZACIÓN 3: Crear opciones de forma más eficiente
            review_options = []
            review_data = []
            
            for idx, row in dff_sample.iterrows():
                hotel_name = str(row["Nombre del Hotel"])[:25]
                score = row["Puntuación del Revisor"]
                
                # Preview corto (50 chars máximo)
                if "review_text" in row and pd.notna(row["review_text"]):
                    preview = str(row["review_text"])[:50]
                else:
                    pos = str(row.get("Reseña Positiva", ""))
                    neg = str(row.get("Reseña Negativa", ""))
                    preview = f"{pos} {neg}"[:50]
                
                preview = preview.replace("\n", " ").strip()
                
                if preview:
                    option_text = f"{hotel_name}... | ⭐{score} | {preview}..."
                    review_options.append(option_text)
                    review_data.append(row.to_dict())
            
            if len(review_options) == 0:
                st.warning("⚠️ No se encontraron reseñas con texto válido. Ajusta los filtros.")
            else:
                # Selector de reseña (compacto)
                st.markdown("---")
                st.markdown("##### 📝 Selecciona una Reseña")
                
                selected_review_idx = st.selectbox(
                    "Reseña:",
                    range(len(review_options)),
                    format_func=lambda x: review_options[x],
                    help="Selecciona una reseña para analizar",
                    key="api_review_select"
                )
                
                # Obtener la reseña seleccionada (desde dict pre-cargado)
                selected_row = review_data[selected_review_idx]
                
                # Mostrar detalles de la reseña seleccionada (compacto)
                with st.expander("📋 Detalles de la Reseña", expanded=False):
                    col_det1, col_det2, col_det3 = st.columns(3)
                    
                    with col_det1:
                        hotel_name = str(selected_row.get("Nombre del Hotel", "N/A"))
                        st.metric("🏨 Hotel", hotel_name[:30] + ("..." if len(hotel_name) > 30 else ""))
                    
                    with col_det2:
                        score = selected_row.get("Puntuación del Revisor", 0)
                        st.metric("⭐ Puntuación", f"{score}/10")
                    
                    with col_det3:
                        sentiment = selected_row.get("Etiqueta de Sentimiento")
                        if sentiment and pd.notna(sentiment):
                            st.metric("😊 Sentimiento", str(sentiment).capitalize())
                        else:
                            st.metric("😊 Sentimiento", "N/A")
                    
                    # Texto completo (limitado a 5K para análisis)
                    if "review_text" in selected_row and pd.notna(selected_row.get("review_text")) and str(selected_row.get("review_text", "")).strip():
                        review_text = str(selected_row["review_text"])[:5000]
                    else:
                        pos_text = str(selected_row.get("Reseña Positiva", "")).strip()
                        neg_text = str(selected_row.get("Reseña Negativa", "")).strip()
                        review_text = f"{pos_text}. {neg_text}".strip(". ")[:5000]
                    
                    st.text_area(
                        "Reseña:",
                        value=review_text,
                        height=120,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
                # Botón de análisis
                st.markdown("---")
                col_btn1, col_btn2 = st.columns([1, 3])
                
                with col_btn1:
                    analyze_btn = st.button("🚀 Analizar con API", type="primary", width='stretch')
        
                if analyze_btn:
                    if len(review_text.strip()) < 10:
                        st.warning("⚠️ La reseña seleccionada es demasiado corta para analizar")
                    else:
                        with st.spinner("🔄 Analizando reseña con la API..."):
                            # Usar versión cacheada (máx 5K chars)
                            result = analyze_cached(review_text)
                        
                        if result:
                            st.success("✅ Análisis completado")
                            
                            # Mostrar comparación con datos originales si están disponibles
                            original_sentiment = selected_row.get("Etiqueta de Sentimiento")
                            if original_sentiment and pd.notna(original_sentiment):
                                st.markdown("---")
                                st.markdown("#### 🔄 Comparación: Dataset vs API")
                                
                                col_comp1, col_comp2 = st.columns(2)
                                
                                with col_comp1:
                                    st.markdown("**Sentimiento en Dataset (VADER original):**")
                                    sentiment_class_orig = f"sentiment-{str(original_sentiment).lower()}"
                                    st.markdown(
                                        f'<div class="sentiment-badge {sentiment_class_orig}">{str(original_sentiment).upper()}</div>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    compound_score = selected_row.get("compound")
                                    if compound_score and pd.notna(compound_score):
                                        st.metric("Score Compuesto", f"{compound_score:.3f}")
                                
                                with col_comp2:
                                    st.markdown("**Sentimiento calculado por API:**")
                                    api_sentiment = result['sentiment']['sentiment']
                                    sentiment_class_api = f"sentiment-{api_sentiment.lower()}"
                                    st.markdown(
                                        f'<div class="sentiment-badge {sentiment_class_api}">{api_sentiment.upper()}</div>',
                                        unsafe_allow_html=True
                                    )
                                    st.metric("Score Compuesto", f"{result['sentiment']['compound_score']:.3f}")
                                
                                # Verificar si coinciden
                                if original_sentiment == api_sentiment:
                                    st.success("✅ Los sentimientos coinciden!")
                                else:
                                    st.info("ℹ️ Los sentimientos difieren. Esto puede deberse a diferencias en el procesamiento del texto.")
                            
                            # Mostrar texto limpio
                            with st.expander("📝 Texto procesado por la API", expanded=False):
                                st.code(result['cleaned_text'], language=None)
                            
                            st.markdown("---")
                            
                            # Sentimiento detallado de la API
                            st.markdown("#### 📊 Análisis de Sentimiento Detallado (API)")
                            
                            sentiment = result['sentiment']
                            sentiment_label = sentiment['sentiment']
                            
                            # Badge de sentimiento
                            sentiment_class = f"sentiment-{sentiment_label.lower()}"
                            st.markdown(
                                f'<div class="sentiment-badge {sentiment_class}">{sentiment_label.upper()}</div>',
                                unsafe_allow_html=True
                            )
                            
                            # Métricas de sentimiento
                            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                            
                            with col_s1:
                                st.metric(
                                    "Score Compuesto",
                                    f"{sentiment['compound_score']:.3f}",
                                    help="Score general de sentimiento (-1 a 1)"
                                )
                            
                            with col_s2:
                                st.metric(
                                    "😊 Positivo",
                                    f"{sentiment['positive_score'] * 100:.1f}%",
                                    help="Proporción de palabras positivas"
                                )
                            
                            with col_s3:
                                st.metric(
                                    "😐 Neutral",
                                    f"{sentiment['neutral_score'] * 100:.1f}%",
                                    help="Proporción de palabras neutrales"
                                )
                            
                            with col_s4:
                                st.metric(
                                    "😞 Negativo",
                                    f"{sentiment['negative_score'] * 100:.1f}%",
                                    help="Proporción de palabras negativas"
                                )
                            
                            # Gráfico de barras
                            fig_sentiment = go.Figure(data=[
                                go.Bar(
                                    x=['Positivo', 'Neutral', 'Negativo'],
                                    y=[sentiment['positive_score'] * 100, sentiment['neutral_score'] * 100, sentiment['negative_score'] * 100],
                                    marker_color=['#10b981', '#6b7280', '#ef4444'],
                                    text=[f"{sentiment['positive_score']:.2%}", 
                                          f"{sentiment['neutral_score']:.2%}", 
                                          f"{sentiment['negative_score']:.2%}"],
                                    textposition='outside'
                                )
                            ])
                            
                            fig_sentiment.update_layout(
                                title="Distribución de Sentimientos",
                                yaxis_title="Porcentaje",
                                yaxis=dict(ticksuffix="%"),
                                height=350,
                                showlegend=False,
                                template="plotly_white"
                            )
                            
                            st.plotly_chart(fig_sentiment, width='stretch')
                            
                            st.markdown("---")
                            
                            # Tópicos (mostrar solo top 3 para rendimiento)
                            st.markdown("#### 🎯 Tópicos Detectados (LDA)")
                            
                            if result['topics']:
                                # Limitar a 3 tópicos para evitar sobrecarga
                                topics_to_show = result['topics'][:3]
                                total_topics = len(result['topics'])
                                
                                if total_topics > 3:
                                    st.markdown(f"Se detectaron **{total_topics}** tópicos. Mostrando los **3 principales:**")
                                else:
                                    st.markdown(f"Se detectaron **{total_topics}** tópicos en esta reseña:")
                                
                                for topic in topics_to_show:
                                    with st.expander(f"🏷️ Tema {topic['topic_id']}", expanded=False):
                                        keywords = topic['keywords'].split(", ")
                                        
                                        # Crear badges HTML para palabras clave
                                        badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">'
                                        for word in keywords:
                                            badges_html += f'<span class="topic-badge">{word}</span>'
                                        badges_html += '</div>'
                                        
                                        st.markdown(badges_html, unsafe_allow_html=True)
                            else:
                                st.info("No se detectaron tópicos específicos en esta reseña.")
                            
                            # Botón para descargar resultado
                            st.markdown("---")
                            result_json = json.dumps(result, indent=2, ensure_ascii=False)
                            st.download_button(
                                label="💾 Descargar resultado (JSON)",
                                data=result_json,
                                file_name=f"analisis_resena_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                width='stretch'
                            )
    
    # SUBTAB 2: Resumen de tópicos agregados
    with subtab2:
        st.markdown("#### Resumen de Tópicos Más Mencionados")
        st.markdown("Obtén un resumen de los tópicos más frecuentes en reseñas positivas y negativas del dataset.")
        
        # Configuración
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            n_topics = st.slider(
                "Número de tópicos por categoría:",
                min_value=3,
                max_value=15,
                value=8,
                help="Más tópicos = más detalle pero más tiempo de procesamiento"
            )
        
        with col_cfg2:
            max_reviews = st.select_slider(
                "Máximo de reseñas a analizar:",
                options=[1000, 2000, 5000, 10000, 20000, 50000],
                value=10000,
                help="Menos reseñas = más rápido pero menos representativo"
            )
        
        col_btn_sum1, col_btn_sum2 = st.columns([1, 3])
        with col_btn_sum1:
            generate_summary = st.button("📈 Generar Resumen", type="primary", width='stretch')
        
        if generate_summary:
            # Preparar filtros para la API
            topics_filters = current_filters.copy()
            topics_filters["sample_size"] = max_reviews
            
            with st.spinner(f"🔄 Analizando hasta {max_reviews:,} reseñas... Esto puede tardar 30-90 segundos"):
                topics_data = get_topics_from_api(topics_filters, n_topics=n_topics)
            
            if topics_data:
                st.success("✅ Resumen generado exitosamente")
                
                # Información general
                st.markdown("---")
                st.markdown("#### 📊 Información General")
                
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                
                with col_info1:
                    st.metric(
                        "📚 Fuente",
                        topics_data['data_source'].replace('hotel_reviews_processed.csv', 'Procesado').replace('Hotel_Reviews.csv', 'Raw')
                    )
                
                with col_info2:
                    st.metric(
                        "📊 Total Analizado",
                        f"{topics_data['total_reviews_analyzed']:,}"
                    )
                
                with col_info3:
                    pos_count = topics_data['positive_topics']['total_reviews']
                    st.metric(
                        "😊 Positivas",
                        f"{pos_count:,}",
                        delta=f"{pos_count/topics_data['total_reviews_analyzed']*100:.1f}%"
                    )
                
                with col_info4:
                    neg_count = topics_data['negative_topics']['total_reviews']
                    st.metric(
                        "😞 Negativas",
                        f"{neg_count:,}",
                        delta=f"{neg_count/topics_data['total_reviews_analyzed']*100:.1f}%"
                    )
                
                st.markdown("---")
                
                # Tópicos en dos columnas
                col_pos, col_neg = st.columns(2)
                
                with col_pos:
                    st.markdown("### 😊 TÓPICOS EN RESEÑAS POSITIVAS")
                    st.markdown(f"*{topics_data['positive_topics']['total_reviews']:,} reseñas analizadas*")
                    
                    for topic in topics_data['positive_topics']['topics']:
                        with st.container():
                            st.markdown(f"""
                            <div class="api-card" style="border-left-color: #10b981;">
                                <h4 style="color: #10b981; margin-bottom: 10px;">🏷️ Tema {topic['topic_id']}</h4>
                                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 8px;">Palabras clave:</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            keywords = topic['keywords'].split(", ")
                            badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: -10px; margin-bottom: 15px;">'
                            for word in keywords[:10]:  # Mostrar máximo 10 palabras
                                badges_html += f'<span class="topic-badge" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">{word}</span>'
                            badges_html += '</div>'
                            st.markdown(badges_html, unsafe_allow_html=True)
                
                with col_neg:
                    st.markdown("### 😞 TÓPICOS EN RESEÑAS NEGATIVAS")
                    st.markdown(f"*{topics_data['negative_topics']['total_reviews']:,} reseñas analizadas*")
                    
                    for topic in topics_data['negative_topics']['topics']:
                        with st.container():
                            st.markdown(f"""
                            <div class="api-card" style="border-left-color: #ef4444;">
                                <h4 style="color: #ef4444; margin-bottom: 10px;">🏷️ Tema {topic['topic_id']}</h4>
                                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 8px;">Palabras clave:</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            keywords = topic['keywords'].split(", ")
                            badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: -10px; margin-bottom: 15px;">'
                            for word in keywords[:10]:
                                badges_html += f'<span class="topic-badge" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">{word}</span>'
                            badges_html += '</div>'
                            st.markdown(badges_html, unsafe_allow_html=True)
                
                # Comparación visual
                st.markdown("---")
                st.markdown("#### 📊 Comparación de Tópicos")
                
                # Crear tabla comparativa
                comparison_data = []
                
                for i, (pos_topic, neg_topic) in enumerate(zip(
                    topics_data['positive_topics']['topics'],
                    topics_data['negative_topics']['topics']
                ), 1):
                    comparison_data.append({
                        'Tema #': i,
                        '😊 Positivo': pos_topic['keywords'][:60] + "...",
                        '😞 Negativo': neg_topic['keywords'][:60] + "..."
                    })
                
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, width='stretch', hide_index=True)
                
                # Botón para descargar
                st.markdown("---")
                topics_json = json.dumps(topics_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="💾 Descargar resumen completo (JSON)",
                    data=topics_json,
                    file_name=f"resumen_topicos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    width='stretch'
                )
        else:
            st.info("👆 Configura los parámetros y haz clic en 'Generar Resumen' para obtener el análisis de tópicos.")
            
            # Mostrar información de la API
            st.markdown("---")
            st.markdown("#### 📖 Sobre esta funcionalidad")
            
            st.markdown("""
            Esta sección utiliza la **API REST de FastAPI** para:
            
            1. **Cargar el dataset procesado** (o raw si no está disponible)
            2. **Filtrar reseñas** por sentimiento (positivo/negativo)
            3. **Extraer tópicos** usando LDA (Latent Dirichlet Allocation)
            4. **Retornar resultados** en formato JSON estructurado
            
            **Ventajas de usar la API:**
            - ✅ Procesamiento centralizado y optimizado
            - ✅ Reutilizable desde otras aplicaciones
            - ✅ Cache de resultados para mejor rendimiento
            - ✅ Documentación automática (Swagger)
            
            **Documentación completa:**
            - 📖 [API_README.md](API_README.md)
            - 🚀 [QUICKSTART_API.md](QUICKSTART_API.md)
            - 📊 [API_SUMMARY.md](API_SUMMARY.md)
            - 🌐 [Swagger UI](http://localhost:8000/docs)
            """)

# ======================
# 11. Footer
# ======================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: white; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 8px;">
    <p style="margin: 0; font-size: 0.9rem; font-weight: 600;">
        Análisis de Sentimiento y Extracción de Tópicos - Hoteles Europeos | Mosquera • Quinteros • Torres | 2025
    </p>
    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; opacity: 0.8;">
        Seminario de Analítica con Python | Powered by Streamlit, Plotly & NLP
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.7rem; opacity: 0.7;">
        Dataset: {total_dataset_reviews:,} reseñas | Filtrado: {filtered_reviews:,} reseñas | 
        Modo: {'VADER Activo' if use_vader else 'Consulta Básica'}
    </p>
</div>
""", unsafe_allow_html=True)