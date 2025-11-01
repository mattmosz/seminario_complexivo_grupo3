# dashboard_streamlit/app.py
import os
from io import BytesIO
import requests

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud

# ======================
# 1. Configuración Inicial
# ======================
st.set_page_config(
    page_title="Booking.com - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Conectar Streamlit con scripts/analyze.py ----------
import subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # raíz del repo
RAW_PATH = ROOT / "data" / "Hotel_Reviews.csv"
PROCESSED_PATH = ROOT / "data" / "hotel_reviews_processed.csv"
ANALYZE_PY = ROOT / "scripts" / "analyze.py"

def processed_is_stale(max_age_hours: int = 24) -> bool:
    """Devuelve True si el procesado no existe o es muy viejo."""
    if not PROCESSED_PATH.exists():
        return True
    age_hours = (time.time() - PROCESSED_PATH.stat().st_mtime) / 3600.0
    return age_hours > max_age_hours

def run_analyze_cli(sample: int = 0, stream: bool = True, chunk: int = 100_000, topics: bool = False) -> tuple[bool, str]:
    """
    Ejecuta scripts/analyze.py desde Streamlit.
    Devuelve (ok, log).
    """
    if not RAW_PATH.exists():
        return False, f" No se encontró el RAW en: {RAW_PATH}"
    if not ANALYZE_PY.exists():
        return False, f" No se encontró analyze.py en: {ANALYZE_PY}"

    cmd = [sys.executable, str(ANALYZE_PY)]
    if stream: 
        cmd += ["--stream"]
    if sample > 0: 
        cmd += ["--sample", str(sample)]
    if chunk: 
        cmd += ["--chunk", str(chunk)]
    if topics: 
        cmd += ["--topics"]

    try:
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
        ok = (res.returncode == 0)
        log = res.stdout + "\n" + res.stderr
        return ok, log
    except Exception as e:
        return False, f" Error al ejecutar analyze.py: {e}"

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

@st.cache_data(show_spinner="🔄 Cargando datos...")
def load_data() -> pd.DataFrame:
    """Carga datos desde API (si está activa) o CSV local por defecto."""

    # --- 1) Intentar API ---
    if BASE_API_URL:
        try:
            headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
            res = requests.get(f"{BASE_API_URL}/reviews", headers=headers, timeout=10)
            if res.status_code == 200:
                st.success(" Datos cargados desde la API")
                df = pd.DataFrame(res.json())
            else:
                st.warning(f" API respondió con {res.status_code}. Se usará CSV local.")
                df = pd.read_csv(DATA_PATH, encoding="utf-8")
        except Exception as e:
            st.warning(f" Error conectando a la API: {e}. Se usará CSV local.")
            df = pd.read_csv(DATA_PATH, encoding="utf-8")

    # --- 2) CSV local (por defecto actual) ---
    else:
        try:
            df = pd.read_csv(DATA_PATH, encoding="utf-8")
            st.info(" Datos cargados desde el CSV local")
        except UnicodeDecodeError:
            df = pd.read_csv(DATA_PATH, encoding="latin-1")
        except FileNotFoundError:
            st.error(f" Archivo no encontrado: {DATA_PATH}")
            st.stop()

    # --- 3) Limpieza básica y manejo de nulos ---
    expected = {
        "Hotel_Name", "Reviewer_Nationality", "Positive_Review", "Negative_Review",
        "review_text", "sentiment_label", "Reviewer_Score", "lat", "lng"
    }
    miss = expected - set(df.columns)
    if miss:
        st.error(f" Faltan columnas en el dataset: {sorted(miss)}")
        st.stop()

    df["Reviewer_Score"] = pd.to_numeric(df["Reviewer_Score"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    df["Hotel_Name"] = df["Hotel_Name"].fillna("Hotel Desconocido")
    df["Reviewer_Nationality"] = df["Reviewer_Nationality"].fillna("Sin Especificar")
    df["Positive_Review"] = df["Positive_Review"].fillna("")
    df["Negative_Review"] = df["Negative_Review"].fillna("")
    df["review_text"] = df["review_text"].fillna("")
    df["sentiment_label"] = df["sentiment_label"].fillna("neutro")

    if df["Reviewer_Score"].isna().any():
        median_score = df["Reviewer_Score"].median()
        df["Reviewer_Score"] = df["Reviewer_Score"].fillna(median_score)

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

# --- Llamar a la función de carga ---
try:
    df = load_data()
    total_dataset_reviews = len(df)
except Exception as e:
    st.error(f" Error al cargar datos: {e}")
    st.stop()


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
    
    col_hotel = st.selectbox(
        "Hotel",
        ["(Todos)"] + sorted(df["Nombre del Hotel"].dropna().unique().tolist())
    )
    
    if use_vader:
        col_sent = st.radio(
            "Sentimiento",
            ["(Todos)", "positivo", "neutro", "negativo"],
            horizontal=False
        )
    else:
        col_sent = "(Todos)"
    
    col_nat = st.selectbox(
        "Nacionalidad",
        ["(Todas)"] + sorted(df["Nacionalidad del Revisor"].dropna().unique().tolist())[:50]
    )
    
    score_lo, score_hi = st.slider(
        "Rango de Puntuación",
        0.0, 10.0, (0.0, 10.0), step=0.5
    )
    
    st.markdown("---")
    
    fast_wc = st.toggle("Acelerar nubes de palabras", value=True,
                        help="Usa muestra de 3000 reseñas para generar nubes más rápido")
    
    # Expander para procesamiento VADER
    with st.expander("Procesamiento VADER", expanded=False):
        st.write("Genera/actualiza `data/hotel_reviews_processed.csv` usando `scripts/analyze.py`.")

        colA, colB = st.columns(2)
        sample_n = colA.number_input("Muestra (0 = todo)", min_value=0, value=0, step=50000)
        stream   = colB.toggle("Stream", value=True, help="Procesa por bloques")
        chunk    = st.number_input("Chunk size", min_value=10_000, value=100_000, step=10_000)
        topics   = st.toggle("Incluir LDA (tarda)", value=False)

        if st.button("Ejecutar análisis ahora"):
            with st.status("Procesando con VADER…", expanded=True) as status:
                ok, log = run_analyze_cli(sample=sample_n, stream=stream, chunk=chunk, topics=topics)
                st.code(log[-4000:], language="bash")
                if ok and PROCESSED_PATH.exists():
                    status.update(label=" Listo", state="complete")
                    st.success("CSV procesado generado/actualizado.")
                else:
                    status.update(label=" Falló", state="error")
                    st.error("Revisa el log para más detalles.")

        def _safe_rerun():
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

        if st.button("Recargar datos procesados"):
            st.cache_data.clear()
            _safe_rerun()

        if processed_is_stale():
            st.warning("El archivo CSV procesado no existe o tiene más de 24 horas. Se recomienda ejecutar el análisis nuevamente.")

# ======================
# 6. Filtrado de Datos
# ======================
dff = df.copy()

if col_hotel != "(Todos)":
    dff = dff[dff["Nombre del Hotel"] == col_hotel]

if col_nat != "(Todas)":
    dff = dff[dff["Nacionalidad del Revisor"] == col_nat]

if use_vader and col_sent != "(Todos)":
    dff = dff[dff["Etiqueta de Sentimiento"] == col_sent]

dff = dff[(dff["Puntuación del Revisor"] >= score_lo) & (dff["Puntuación del Revisor"] <= score_hi)]

# ======================
# 7. Header Principal
# ======================
st.markdown("""
<div class="main-title">
    <h1>DASHBOARD: Análisis de Sentimiento - Hoteles Europeos</h1>
</div>
""", unsafe_allow_html=True)

# ======================
# 8. KPIs Principales (Mejorados)
# ======================
filtered_reviews = len(dff)
avg_score = float(dff["Puntuación del Revisor"].mean()) if filtered_reviews else 0.0

if use_vader:
    pos_pct = round(100 * dff["Etiqueta de Sentimiento"].eq("positivo").mean(), 1) if filtered_reviews else 0.0
    neg_pct = round(100 * dff["Etiqueta de Sentimiento"].eq("negativo").mean(), 1) if filtered_reviews else 0.0
else:
    pos_pct = 0.0
    neg_pct = 0.0

unique_hotels = dff["Nombre del Hotel"].nunique()

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
        <div class="kpi-label">Únicos</div>
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

def sample_text(series: pd.Series, max_chars: int = 60000, fast: bool = True) -> str:
    """Extrae texto de la serie con opción de muestreo rápido."""
    if not fast:
        return " ".join(series.dropna().astype(str).tolist())[:max_chars]
    n = min(3000, series.dropna().shape[0])
    if n == 0:
        return ""
    arr = series.dropna().astype(str).sample(n, random_state=42).tolist()
    return " ".join(arr)[:max_chars]

def get_extended_stopwords():
    """
    Obtiene una lista extendida de stop words combinando múltiples fuentes.
    """
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    
    # Lista base de sklearn
    stop_words = set(ENGLISH_STOP_WORDS)
    
    # Intentar agregar stop words de NLTK
    try:
        import nltk
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        from nltk.corpus import stopwords
        nltk_stops = set(stopwords.words('english'))
        stop_words.update(nltk_stops)
    except:
        pass  # Si falla, solo usar sklearn
    
    # Agregar palabras adicionales comunes en reseñas de hoteles
    custom_stops = {
        'hotel', 'room', 'stay', 'stayed', 'night', 'nights',
        'booking', 'booked', 'book', 'reservation', 'reserved',
        'staff', 'service', 'location', 'place', 'time',
        'good', 'great', 'nice', 'bad', 'terrible',
        'like', 'really', 'just', 'got', 'went', 'come', 'came',
        'would', 'could', 'should', 'also', 'well', 'even',
        'however', 'although', 'though', 'still', 'yet',
        'positive', 'negative', 'review', 'reviews',
        'said', 'told', 'asked', 'did', 'does', 'done',
        'thing', 'things', 'way', 'ways', 'day', 'days',
        'bit', 'lot', 'lots', 'much', 'many', 'very', 'quite',
        'nbsp', 'one', 'two', 'nothing', 'everything',
        'the', 'and', 'was', 'were', 'that', 'this', 'for', 'with',
        'not', 'but', 'are', 'had', 'have', 'has', 'been', 'there',
        'all', 'from', 'they', 'which', 'when', 'where', 'who',
        'our', 'we', 'you', 'can', 'will', 'would', 'could',
        'no', 'yes', 'ok', 'okay', 'fine'
    }
    stop_words.update(custom_stops)
    
    return stop_words


def wc_image(text: str, colormap: str) -> BytesIO:
    """Genera imagen de nube de palabras con stop words extendidas."""
    if not text.strip():
        text = "sin datos"
    
    # Obtener stop words extendidas
    stopwords_extended = get_extended_stopwords()
    
    wc = WordCloud(
        width=1600,
        height=500,
        background_color="white",
        colormap=colormap,
        max_words=150,
        relative_scaling=0.5,
        stopwords=stopwords_extended,
        min_font_size=10,
        max_font_size=100,
        prefer_horizontal=0.7
    )
    img = wc.generate(text).to_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ======================
# 10. Dashboard con Tabs
# ======================
if use_vader:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Análisis General", 
        "Geografía", 
        "Palabras Clave", 
        "Datos Detallados",
        "Estadísticas Avanzadas"
    ])
else:
    tab1, tab2, tab3, tab4 = st.tabs([
        "Análisis General", 
        "Geografía", 
        "Datos Detallados",
        "Estadísticas Avanzadas"
    ])

# TAB 1: Análisis General
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_area_por_categoria(dff, use_vader), use_container_width=True)
    with col2:
        if use_vader:
            st.plotly_chart(fig_donut(dff["Etiqueta de Sentimiento"], "Distribución de Sentimientos"), 
                          use_container_width=True)
        else:
            st.info("💡 El análisis de sentimientos está deshabilitado. Actívalo en la barra lateral para ver la distribución.")
    
    col3, col4 = st.columns([2, 1])
    with col3:
        st.plotly_chart(fig_trend(dff), use_container_width=True)
    with col4:
        st.plotly_chart(fig_top_hoteles(dff), use_container_width=True)
    
    # Gráfico adicional de nacionalidades
    st.plotly_chart(fig_nationality_distribution(dff), use_container_width=True)

# TAB 2: Geografía
with tab2:
    st.plotly_chart(fig_map(dff, use_vader), use_container_width=True)
    
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

        pos_text = sample_text(
            dff.loc[dff["Etiqueta de Sentimiento"].eq("positivo"), "Reseña Positiva"],
            fast=fast_wc
        )
        neg_text = sample_text(
            dff.loc[dff["Etiqueta de Sentimiento"].eq("negativo"), "Reseña Negativa"],
            fast=fast_wc
        )

        with col_pos:
            st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
            st.markdown('<span class="wordcloud-label">✓ RESEÑAS POSITIVAS</span>', unsafe_allow_html=True)
            if pos_text.strip():
                st.image(wc_image(pos_text, "RdPu"), use_container_width=True)  # <- actualizado
            else:
                st.warning("No hay suficientes reseñas positivas para generar la nube de palabras.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_neg:
            st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
            st.markdown('<span class="wordcloud-label">✗ RESEÑAS NEGATIVAS</span>', unsafe_allow_html=True)
            if neg_text.strip():
                st.image(wc_image(neg_text, "Blues"), use_container_width=True)  # <- actualizado
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
            use_container_width=True,
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
            use_container_width=True
        )
    with col_btn2:
        st.download_button(
            "Descargar CSV Completo",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"hotel_reviews_complete_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
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
    st.plotly_chart(fig_hist, use_container_width=True)
    
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
            use_container_width=True,
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