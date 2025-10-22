# scripts/data_loader.py
from __future__ import annotations
import os
import argparse
import pandas as pd
from pathlib import Path

# Ruta base del proyecto
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_RAW_DEFAULT = SCRIPT_DIR / ".." / "data" / "Hotel_Reviews.csv"
DATA_PROCESSED_DEFAULT = SCRIPT_DIR / ".." / "data" / "hotel_reviews_processed.csv"

# ------------------ Carga robusta ------------------
def cargar_datos(path: str | os.PathLike) -> pd.DataFrame | None:
    path = Path(path).resolve()
    print(f"Cargando datos desde {path}...")
    try:
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
        print("✅ Datos han sido cargados.")
        return df
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo en {path}")
        print("Asegúrate de tener el archivo en la carpeta 'data'.")
        return None
    except Exception as e:
        print(f"⚠️ Ocurrió un error inesperado: {e}")
        return None

# ------------------ Normalización para el dashboard ------------------
def _compose_review_columns(df: pd.DataFrame) -> pd.Series:
    """Si no existe review_text, lo componemos de Positive_Review + Negative_Review."""
    pos = df.get("Positive_Review", pd.Series(dtype=str)).fillna("").astype(str)
    neg = df.get("Negative_Review", pd.Series(dtype=str)).fillna("").astype(str)
    # limpiar “No Positive/No Negative”
    pos = pos.str.replace(r"^No Positive$", "", regex=True).str.strip()
    neg = neg.str.replace(r"^No Negative$", "", regex=True).str.strip()
    return (pos + ". " + neg).str.strip(". ")

def _label_from_score(score: float) -> str:
    """Etiqueta heurística si no existe sentiment_label (fallback)."""
    if pd.isna(score): return "neutro"
    if score >= 8.0:   return "positivo"
    if score <= 6.0:   return "negativo"
    return "neutro"

def normalizar_para_dashboard(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """
    Devuelve (df_normalizado, has_real_vader)
    - Asegura que existan 'review_text' y 'sentiment_label' (crea fallback si faltan).
    - Retorna un flag para indicar si 'sentiment_label' proviene realmente de VADER.
    """
    # Normalización de tipos mínimo
    if "Reviewer_Score" in df.columns:
        df["Reviewer_Score"] = pd.to_numeric(df["Reviewer_Score"], errors="coerce")

    # Determinar si ya viene con VADER real
    has_real_vader = {"review_text", "sentiment_label"}.issubset(df.columns)

    # Crear review_text si falta
    if "review_text" not in df.columns:
        df["review_text"] = _compose_review_columns(df)

    # Crear sentiment_label si falta (heurística por score)
    if "sentiment_label" not in df.columns:
        df["sentiment_label"] = df["Reviewer_Score"].apply(_label_from_score)

    # Rellenos amables
    for col in ["Hotel_Name", "Reviewer_Nationality", "Positive_Review", "Negative_Review", "review_text"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Devolver también si hay VADER real
    return df, has_real_vader

def cargar_para_dashboard(path_preferido: str | os.PathLike | None = None) -> tuple[pd.DataFrame, bool]:
    """
    Intenta cargar primero el procesado (hotel_reviews_processed.csv).
    Si no existe, carga el crudo (Hotel_Reviews.csv).
    Normaliza columnas y retorna (df, has_real_vader).
    """
    # 1) pref: el que te pasen
    if path_preferido:
        df = cargar_datos(path_preferido)
        if df is None:
            raise FileNotFoundError(f"No se pudo cargar {path_preferido}")
        return normalizar_para_dashboard(df)

    # 2) si no, intenta procesado
    if DATA_PROCESSED_DEFAULT.exists():
        df = cargar_datos(DATA_PROCESSED_DEFAULT)
        if df is None:
            raise FileNotFoundError(f"No se pudo cargar {DATA_PROCESSED_DEFAULT}")
        return normalizar_para_dashboard(df)

    # 3) último recurso: crudo
    if DATA_RAW_DEFAULT.exists():
        df = cargar_datos(DATA_RAW_DEFAULT)
        if df is None:
            raise FileNotFoundError(f"No se pudo cargar {DATA_RAW_DEFAULT}")
        return normalizar_para_dashboard(df)

    raise FileNotFoundError("No encontré ni el procesado ni el crudo en /data.")

# ---------- Utilidades de consulta ----------
def columnas(df: pd.DataFrame):
    print("🧱 Columnas:\n", df.columns.tolist())

def primeras_filas(df: pd.DataFrame, n: int = 5):
    print(df.head(n))

def dimensiones(df: pd.DataFrame):
    print("📐 Dimensiones:", df.shape)

def tipos(df: pd.DataFrame):
    print("🔤 Tipos:\n", df.dtypes)

def sample(df: pd.DataFrame, n: int = 10, seed: int = 42):
    print(df.sample(n=n, random_state=seed))

def contar(df: pd.DataFrame, columna: str, n: int = 10):
    if columna not in df.columns:
        print(f"❌ La columna '{columna}' no existe.")
        return
    print(df[columna].value_counts().head(n))

def filtrar(df: pd.DataFrame, columna: str, contiene: str, n: int = 10):
    if columna not in df.columns:
        print(f"❌ La columna '{columna}' no existe.")
        return
    mask = df[columna].astype(str).str.contains(contiene, case=False, na=False)
    out = df[mask].head(n)
    print(out if not out.empty else "No se encontraron filas.")

# ---------- CLI ----------
if __name__ == "__main__":
    print(f"Ejecutando script desde: {Path(__file__).resolve()}")
    parser = argparse.ArgumentParser(description="Consulta rápida del CSV de hoteles.")
    parser.add_argument("--path", type=str, default="", help="Ruta al CSV (opcional)")
    parser.add_argument("--dashboard", action="store_true",
                        help="Carga y normaliza como lo usa el dashboard (con fallback).")
    parser.add_argument("--head", type=int, default=0, help="Mostrar primeras N filas")
    parser.add_argument("--cols", action="store_true", help="Listar columnas")
    parser.add_argument("--shape", action="store_true", help="Mostrar dimensiones")
    parser.add_argument("--dtypes", action="store_true", help="Mostrar tipos de datos")
    parser.add_argument("--sample", type=int, default=0, help="Muestra aleatoria de N filas")
    parser.add_argument("--count", type=str, default="", help="value_counts de una columna")
    parser.add_argument("--filter-col", type=str, default="", help="Columna a filtrar (contains)")
    parser.add_argument("--filter-like", type=str, default="", help="Texto a buscar en la columna")
    parser.add_argument("--limit", type=int, default=10, help="Límite de filas al filtrar")

    args = parser.parse_args()

    if args.dashboard:
        df, has_vader = cargar_para_dashboard(args.path or None)
        print(f"✅ Cargado para dashboard. VADER real: {has_vader}")
    else:
        target = args.path or DATA_RAW_DEFAULT
        df = cargar_datos(target)
        if df is None:
            raise SystemExit(1)

    if args.cols: columnas(df)
    if args.shape: dimensiones(df)
    if args.dtypes: tipos(df)
    if args.head > 0: primeras_filas(df, args.head)
    if args.sample > 0: sample(df, args.sample)
    if args.count: contar(df, args.count)
    if args.filter_col and args.filter_like:
        filtrar(df, args.filter_col, args.filter_like, args.limit)
