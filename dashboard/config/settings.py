import streamlit as st

# === Configuración general ===
APP_TITLE = "Análisis de Reseñas de Hoteles"
APP_ICON = "📊"

# === Paleta de colores ===
PALETTE = {
    "positivo": "#E91E8C",
    "neutro": "#C8C8C8",
    "negativo": "#1E3A5F",
}

# === API ===
BASE_API_URL = st.secrets.get("BASE_API_URL", "http://localhost:8000/v1")
TOKEN = st.secrets.get("TOKEN", "")
OFFLINE_CSV = st.secrets.get("OFFLINE_CSV", "data/hotel_reviews_processed.csv")

# === Configuración Streamlit ===
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
