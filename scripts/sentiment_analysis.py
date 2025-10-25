import pandas as pd
from pathlib import Path


def ensure_vader():
    
    # Asegura que el lexicon de VADER esté descargado.
    
    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        print("Descargando VADER lexicon...")
        nltk.download("vader_lexicon")


def analyze_sentiment_batch(texts):
    
    # Analiza el sentimiento de una lista de textos usando VADER.
    
    ensure_vader()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    
    sia = SentimentIntensityAnalyzer()
    scores = texts.apply(sia.polarity_scores).apply(pd.Series)
    return scores


def classify_sentiment(compound_score):
    
    # Clasifica un score compuesto en categoría de sentimiento.
    
    if compound_score <= -0.05:
        return "negativo"
    elif compound_score >= 0.05:
        return "positivo"
    else:
        return "neutro"


def sentiment_chunked(df, chunk_size=100_000, stream_path: Path | None = None):
    
    # Procesa sentimiento por bloques para manejar grandes datasets.
    
    ensure_vader()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()

    outs = []
    wrote_header = False
    n = len(df)

    print(f"Analizando sentimiento en {n:,} reseñas...")

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = df.iloc[start:end].copy()

        # Asegurar que review_text existe y es string
        if "review_text" not in chunk.columns:
            raise ValueError("DataFrame debe contener columna 'review_text'")
        
        chunk["review_text"] = chunk["review_text"].fillna("").astype(str)
        
        # Calcular puntajes VADER
        scores = chunk["review_text"].apply(sia.polarity_scores).apply(pd.Series)
        chunk = pd.concat([chunk, scores], axis=1)
        
        # Clasificar sentimiento
        chunk["sentiment_label"] = pd.cut(
            chunk["compound"], 
            bins=[-1.0, -0.05, 0.05, 1.0],
            labels=["negativo", "neutro", "positivo"]
        )

        # Columnas de salida
        cols_keep = [
            "Hotel_Name", "Hotel_Address", "Reviewer_Nationality",
            "Positive_Review", "Negative_Review", "review_text",
            "compound", "pos", "neu", "neg", "sentiment_label",
            "Average_Score", "Reviewer_Score", "Tags", "lat", "lng"
        ]
        chunk_out = chunk[[c for c in cols_keep if c in chunk.columns]].copy()

        # Streaming a CSV o acumular en memoria
        if stream_path:
            mode = "a" if wrote_header else "w"
            chunk_out.to_csv(
                stream_path, 
                index=False, 
                encoding="utf-8", 
                mode=mode, 
                header=not wrote_header
            )
            wrote_header = True
        else:
            outs.append(chunk_out)

        print(f"   Bloque {start:,}-{end:,} listo")

    return None if stream_path else pd.concat(outs, ignore_index=True)