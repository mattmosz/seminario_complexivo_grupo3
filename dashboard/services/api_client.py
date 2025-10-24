# PENDIENTE LA CONSTRUCCIPON DE LA API
# COMO EJEMPPLO, ESTE CÓDIGO INTENTA CONECTARSE A UNA API
import requests
import pandas as pd
import streamlit as st
from config.settings import BASE_API_URL, TOKEN, OFFLINE_CSV

def fetch_reviews():
    """
    Intenta obtener datos desde la API; si falla, usa CSV local.
    """
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        res = requests.get(f"{BASE_API_URL}/reviews", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return pd.DataFrame(data)
        else:
            st.warning(f"⚠️ API respondió con código {res.status_code}. Se usa CSV local.")
    except Exception as e:
        st.warning(f"⚠️ No se pudo conectar con la API ({e}). Se usa CSV local.")

    # Fallback a CSV local
    try:
        return pd.read_csv(OFFLINE_CSV)
    except Exception as e:
        st.error(f" No se pudo cargar CSV local: {e}")
        return pd.DataFrame()
