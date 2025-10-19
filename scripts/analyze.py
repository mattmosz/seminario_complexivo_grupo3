# scripts/analyze.py
import os, re, argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_IN  = ROOT / "data" / "Hotel_Reviews.csv"
DATA_OUT = ROOT / "data" / "hotel_reviews_processed.csv"

# ---------- Utils ----------
def clean_text(s: str) -> str:
    if not isinstance(s, str): return ""
    s = s.strip().replace("No Negative","").replace("No Positive","")
    return re.sub(r"\s+"," ", s)

def compose_review(row) -> str:
    pos = clean_text(row.get("Positive_Review", ""))
    neg = clean_text(row.get("Negative_Review", ""))
    return f"{pos}. {neg}".strip(". ")

def ensure_vader():
    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon")

def sentiment_chunked(df, chunk_size=100_000, stream_path: Path | None = None):
    """Procesa sentimiento por bloques. Si stream_path != None, escribe CSV incremental."""
    ensure_vader()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

    outs = []
    wrote_header = False
    n = len(df)

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = df.iloc[start:end].copy()

        # preparar texto + puntajes VADER
        chunk["review_text"] = chunk.apply(compose_review, axis=1).fillna("").astype(str)
        scores = chunk["review_text"].apply(sia.polarity_scores).apply(pd.Series)
        chunk = pd.concat([chunk, scores], axis=1)
        chunk["sentiment_label"] = pd.cut(
            chunk["compound"], bins=[-1.0, -0.05, 0.05, 1.0],
            labels=["negativo", "neutro", "positivo"]
        )

        # columnas de salida
        cols_keep = [
            "Hotel_Name","Hotel_Address","Reviewer_Nationality",
            "Positive_Review","Negative_Review","review_text",
            "compound","pos","neu","neg","sentiment_label",
            "Average_Score","Reviewer_Score","Tags","lat","lng"
        ]
        chunk_out = chunk[[c for c in cols_keep if c in chunk.columns]].copy()

        # streaming a CSV o acumular en memoria
        if stream_path:
            mode = "a" if wrote_header else "w"
            chunk_out.to_csv(stream_path, index=False, encoding="utf-8", mode=mode, header=not wrote_header)
            wrote_header = True
        else:
            outs.append(chunk_out)

        print(f"   🔹 bloque {start:,}–{end:,} listo")

    return None if stream_path else pd.concat(outs, ignore_index=True)

def run_topics(df: pd.DataFrame,
               n_topics=8, max_features=6000, max_df=0.92, min_df=20, n_top_words=12):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    texts = df["review_text"].fillna("").astype(str).tolist()
    vectorizer = CountVectorizer(stop_words="english", lowercase=True,
                                 max_df=max_df, min_df=min_df, max_features=max_features)
    X = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=n_topics, learning_method="batch",
                                    random_state=42, max_iter=15)
    lda.fit(X)

    terms = vectorizer.get_feature_names_out()
    topics = []
    for i, comp in enumerate(lda.components_):
        top_idx = comp.argsort()[-n_top_words:][::-1]
        words = ", ".join(terms[j] for j in top_idx)
        topics.append(f"Tema {i+1}: {words}")
    return topics

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", action="store_true", help="Ejecuta LDA (puede tardar).")
    ap.add_argument("--sample", type=int, default=0, help="Muestra aleatoria N filas.")
    ap.add_argument("--chunk", type=int, default=100_000, help="Tamaño de bloque para VADER.")
    ap.add_argument("--stream", action="store_true",
                    help="Escribe hotel_reviews_processed.csv mientras procesa (menos RAM).")
    args = ap.parse_args()

    print(f" Cargando: {DATA_IN}")
    if not DATA_IN.exists():
        raise FileNotFoundError(f"No existe {DATA_IN}. Coloca el CSV en /data/")
    try:
        df = pd.read_csv(DATA_IN, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_IN, encoding="latin-1")

    if args.sample > 0:
        df = df.sample(n=min(args.sample, len(df)), random_state=42).reset_index(drop=True)
        print(f" Usando muestra de {len(df)} filas.")
    print(f" Datos: {df.shape[0]} filas, {df.shape[1]} columnas")
    print(" Analizando sentimiento (VADER)...")

    if args.stream:
        # escribe directo a DATA_OUT por bloques
        if DATA_OUT.exists(): DATA_OUT.unlink()
        sentiment_chunked(df, chunk_size=args.chunk, stream_path=DATA_OUT)
        print(f" Procesado guardado (stream) en: {DATA_OUT}")
        # cargar back para LDA opcional sin recocinar VADER
        if args.topics:
            df_small = pd.read_csv(DATA_OUT, encoding="utf-8")
            print(" Modelando tópicos (LDA)...")
            topics = run_topics(df_small)
            print(" Temas detectados:")
            for t in topics: print("   -", t)
    else:
        # procesa en memoria y guarda al final
        df_out = sentiment_chunked(df, chunk_size=args.chunk, stream_path=None)
        print("Distribución:")
        print(df_out["sentiment_label"].value_counts(dropna=False))
        df_out.to_csv(DATA_OUT, index=False, encoding="utf-8")
        print(f" Procesado guardado en: {DATA_OUT}")

        if args.topics:
            print("Modelando tópicos (LDA)...")
            topics = run_topics(df_out)
            print(" Temas detectados:")
            for t in topics: print("   -", t)

if __name__ == "__main__":
    main()
