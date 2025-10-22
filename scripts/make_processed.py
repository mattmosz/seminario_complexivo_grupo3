# scripts/make_processed.py
import argparse, sys
from pathlib import Path

import pandas as pd
import numpy as np

def try_read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")

def main():
    ap = argparse.ArgumentParser(description="Crear hotel_reviews_processed.csv minimal compatible con el dashboard.")
    ap.add_argument("--in", dest="inp", required=True, help="Ruta al CSV crudo (Hotel_Reviews.csv).")
    ap.add_argument("--out", dest="out", required=True, help="Ruta de salida para el CSV procesado.")
    args = ap.parse_args()

    inp = Path(args.inp).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    df = try_read_csv(inp)

    # Columnas que el dashboard espera (en inglés, antes de renombrar dentro de app.py)
    need_cols = ["Hotel_Name","Reviewer_Nationality","Positive_Review","Negative_Review","Reviewer_Score"]
    missing = [c for c in need_cols if c not in df.columns]
    if missing:
        print(f"[ERROR] Faltan columnas en el RAW: {missing}", file=sys.stderr)
        sys.exit(2)

    # review_text (concat POS+NEG) y sentiment_label (regla por score)
    proc = pd.DataFrame()
    proc["Hotel_Name"] = df["Hotel_Name"].fillna("Unknown Hotel")
    proc["Reviewer_Nationality"] = df["Reviewer_Nationality"].fillna("Unspecified")
    proc["Positive_Review"] = df["Positive_Review"].fillna("")
    proc["Negative_Review"] = df["Negative_Review"].fillna("")
    proc["review_text"] = (proc["Positive_Review"].astype(str).str.strip() + " " +
                           proc["Negative_Review"].astype(str).str.strip()).str.strip()

    # Score a num
    proc["Reviewer_Score"] = pd.to_numeric(df["Reviewer_Score"], errors="coerce")

    # Etiqueta de sentimiento simple por umbrales: >=8 pos, <=4 neg, sino neutro
    def label(x):
        if pd.isna(x): return "neutro"
        if x >= 8: return "positivo"
        if x <= 4: return "negativo"
        return "neutro"
    proc["sentiment_label"] = proc["Reviewer_Score"].apply(label)

    # lat/lng si existen; si no, crea columnas vacías (NaN)
    for col in ("lat","lng"):
        if col in df.columns:
            proc[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            proc[col] = np.nan

    # Reordenar columnas principales
    cols = ["Hotel_Name","Reviewer_Nationality","Positive_Review","Negative_Review",
            "review_text","sentiment_label","Reviewer_Score","lat","lng"]
    proc = proc[cols]

    proc.to_csv(out, index=False, encoding="utf-8")
    print(f"[OK] Escribí {out}")
    print(f"Filas: {len(proc):,} | Positivas: {(proc['sentiment_label']=='positivo').sum():,} | "
          f"Negativas: {(proc['sentiment_label']=='negativo').sum():,} | Neutras: {(proc['sentiment_label']=='neutro').sum():,}")

if __name__ == "__main__":
    main()
