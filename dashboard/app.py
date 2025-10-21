# dashboard_streamlit/app.py
import os
from io import BytesIO

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
    header {visibility: hidden;}
    
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
        grid-template-columns: repeat(4, 1fr);
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
        font-size: 1.5rem;
        box-shadow: 0 4px 10px rgba(233,30,140,0.3);
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
        color: #1E3A5F;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
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
    
    /* Wordcloud containers */
    .wordcloud-container {
        background: linear-gradient(135deg, rgba(233,30,140,0.05), rgba(30,58,95,0.05));
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid rgba(233,30,140,0.2);
    }
    
    .wordcloud-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #1E3A5F;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        display: inline-block;
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
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
PLOTLY_TEMPLATE = "plotly_white"

# ======================
# 4. Carga de Datos
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "hotel_reviews_processed.csv"))

@st.cache_data(show_spinner="🔄 Cargando datos...")
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    
    expected = {
        "Hotel_Name", "Reviewer_Nationality", "Positive_Review", "Negative_Review",
        "review_text", "sentiment_label", "Reviewer_Score", "lat", "lng"
    }
    miss = expected - set(df.columns)
    if miss:
        raise ValueError(f"Faltan columnas: {sorted(miss)}")
    
    df["Reviewer_Score"] = pd.to_numeric(df["Reviewer_Score"], errors="coerce")
    
    # Traducir nombres de columnas al español
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

df = load_data(DATA_PATH)

# ======================
# 5. Sidebar (Filtros)
# ======================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📊</div>', unsafe_allow_html=True)
    st.markdown("## ANALÍTICA CON PYTHON")
    st.caption("Análisis de Sentimiento y Extracción de Tópicos en Reseñas de Hoteles Europeos")
    
    st.markdown("---")
    
    col_hotel = st.selectbox(
        "🏨 Hotel",
        ["(Todos)"] + sorted(df["Nombre del Hotel"].dropna().unique().tolist())
    )
    
    col_sent = st.radio(
        " Sentimiento",
        ["(Todos)", "positivo", "neutro", "negativo"],
        horizontal=False
    )
    
    col_nat = st.selectbox(
        " Nacionalidad",
        ["(Todas)"] + sorted(df["Nacionalidad del Revisor"].dropna().unique().tolist())[:30]
    )
    
    score_lo, score_hi = st.slider(
        " Rango de Puntuación",
        0.0, 10.0, (0.0, 10.0), step=0.5
    )
    
    st.markdown("---")
    
    fast_wc = st.toggle("⚡ Acelerar nubes de palabras", value=True)

# ======================
# 6. Filtrado de Datos
# ======================
dff = df.copy()
if col_hotel != "(Todos)":
    dff = dff[dff["Nombre del Hotel"] == col_hotel]
if col_nat != "(Todas)":
    dff = dff[dff["Nacionalidad del Revisor"] == col_nat]
if col_sent != "(Todos)":
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
# 8. KPIs Principales
# ======================
total_reviews = len(dff)
avg_score = float(dff["Puntuación del Revisor"].mean()) if total_reviews else 0.0
pos_pct = round(100 * dff["Etiqueta de Sentimiento"].eq("positivo").mean(), 1) if total_reviews else 0.0
neg_pct = round(100 * dff["Etiqueta de Sentimiento"].eq("negativo").mean(), 1) if total_reviews else 0.0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-badge">TOTAL</div>
        <div class="kpi-icon-circle">📝</div>
        <div class="kpi-value">{total_reviews:,}</div>
        <div class="kpi-label">Total Reseñas</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">PROMEDIO</div>
        <div class="kpi-icon-circle">⭐</div>
        <div class="kpi-value">{avg_score:.1f}</div>
        <div class="kpi-label">Puntuación</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">POSITIVO</div>
        <div class="kpi-icon-circle">✓</div>
        <div class="kpi-value">{pos_pct:.1f}%</div>
        <div class="kpi-label">Satisfacción</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-badge">NEGATIVO</div>
        <div class="kpi-icon-circle">✗</div>
        <div class="kpi-value">{neg_pct:.1f}%</div>
        <div class="kpi-label">Insatisfacción</div>
    </div>
</div>
""", unsafe_allow_html=True)

if total_reviews == 0:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
    st.stop()

# ======================
# 9. Funciones de Visualización
# ======================
def fig_area_por_categoria(data: pd.DataFrame) -> go.Figure:
    bins = pd.cut(data["Puntuación del Revisor"], bins=[0, 4, 7, 10], labels=["Bajo", "Medio", "Alto"])
    tmp = pd.DataFrame({
        "Categoría": bins,
        "Sentimiento": data["Etiqueta de Sentimiento"]
    })
    area = tmp.value_counts().reset_index(name="Cantidad").sort_values(["Categoría", "Sentimiento"])
    
    fig = px.area(
        area, x="Categoría", y="Cantidad", color="Sentimiento",
        color_discrete_map=PALETTE, template=PLOTLY_TEMPLATE
    )
    fig.update_layout(
        title="Análisis por Categorías de Puntuación",
        title_font=dict(size=14, color="#1E3A5F", family="Arial Black"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(categoryorder="array", categoryarray=["Bajo", "Medio", "Alto"])
    return fig

def fig_trend(data: pd.DataFrame) -> go.Figure:
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

def fig_map(data: pd.DataFrame) -> go.Figure:
    m = data.dropna(subset=["lat", "lng"]).copy()
    if len(m) > 500:
        m = m.sample(500, random_state=42)
    
    fig = px.scatter_mapbox(
        m, lat="lat", lon="lng",
        color="Etiqueta de Sentimiento",
        color_discrete_map=PALETTE,
        hover_name="Nombre del Hotel",
        hover_data={"Puntuación del Revisor": True, "lat": False, "lng": False},
        zoom=3,
        height=450
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

def sample_text(series: pd.Series, max_chars: int = 60000) -> str:
    if not fast_wc:
        return " ".join(series.dropna().astype(str).tolist())[:max_chars]
    n = min(3000, series.dropna().shape[0])
    if n == 0:
        return ""
    arr = series.dropna().astype(str).sample(n, random_state=42).tolist()
    return " ".join(arr)[:max_chars]

def wc_image(text: str, colormap: str) -> BytesIO:
    if not text.strip():
        text = "no data"
    wc = WordCloud(
        width=1400,
        height=400,
        background_color="white",
        colormap=colormap,
        max_words=200,
        relative_scaling=0.5,
        stopwords=['hotel', 'room', 'stay', 'stayed', 'would', 'could', 'one', 'also']
    )
    img = wc.generate(text).to_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ======================
# 10. Dashboard con Tabs
# ======================
tab1, tab2, tab3, tab4 = st.tabs([" Análisis General", " Geografía", " Palabras Clave", " Datos Detallados"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_area_por_categoria(dff), use_container_width=True)
    with col2:
        st.plotly_chart(fig_donut(dff["Etiqueta de Sentimiento"], "Distribución de Sentimientos"), use_container_width=True)
    
    col3, col4 = st.columns([2, 1])
    with col3:
        st.plotly_chart(fig_trend(dff), use_container_width=True)
    with col4:
        st.plotly_chart(fig_top_hoteles(dff), use_container_width=True)

with tab2:
    st.plotly_chart(fig_map(dff), use_container_width=True)
    st.info("ℹ️ Muestra limitada a 500 puntos para optimizar el rendimiento.")

with tab3:
    st.markdown("### 🔍 Análisis de Palabras Frecuentes")
    
    col_pos, col_neg = st.columns(2)
    
    pos_text = sample_text(dff.loc[dff["Etiqueta de Sentimiento"].eq("positivo"), "Reseña Positiva"])
    neg_text = sample_text(dff.loc[dff["Etiqueta de Sentimiento"].eq("negativo"), "Reseña Negativa"])
    
    with col_pos:
        st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
        st.markdown('<span class="wordcloud-label">✓ RESEÑAS POSITIVAS</span>', unsafe_allow_html=True)
        st.image(wc_image(pos_text, "RdPu"), use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_neg:
        st.markdown('<div class="wordcloud-container">', unsafe_allow_html=True)
        st.markdown('<span class="wordcloud-label">✗ RESEÑAS NEGATIVAS</span>', unsafe_allow_html=True)
        st.image(wc_image(neg_text, "Blues"), use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown("### 📋 Muestra de Reseñas Filtradas")
    cols = ["Nombre del Hotel", "Nacionalidad del Revisor", "Puntuación del Revisor", "Etiqueta de Sentimiento", "Reseña Positiva", "Reseña Negativa"]
    st.dataframe(
        dff[cols].head(1000),
        use_container_width=True,
        height=500
    )
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        st.download_button(
            "📥 Descargar CSV",
            data=dff.to_csv(index=False).encode("utf-8"),
            file_name="hotel_reviews_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )

# ======================
# 11. Footer
# ======================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 8px;">
    <p style="margin: 0; font-size: 0.9rem; font-weight: 600;">
        Análisis de Sentimiento y Extracción de Tópicos - Hoteles Europeos | Mosquera • Quinteros • Torres | 2025
    </p>
    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; opacity: 0.8;">
        Seminario de Analítica con Python | Powered by Streamlit, Plotly & NLP
    </p>
</div>
""", unsafe_allow_html=True)